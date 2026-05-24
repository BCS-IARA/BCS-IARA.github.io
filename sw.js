// IARA BCS — Service Worker
// Atualiza o número de versão a cada novo deploy para forçar refresh nos clientes
const CACHE_NAME = 'iara-bcs-v1';

// Arquivos essenciais para funcionar offline
const PRECACHE = [
  '/index.html',
  '/inscricao.html',
  '/manifest.json'
];

// ── Instalação: guarda arquivos no cache ─────────────────────────────────────
self.addEventListener('install', function(event) {
  self.skipWaiting(); // ativa imediatamente sem esperar fechar abas
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(PRECACHE).catch(function() {
        // Se algum arquivo não existir ainda (ex: inscricao.html), ignora
        return Promise.resolve();
      });
    })
  );
});

// ── Ativação: remove caches antigos ─────────────────────────────────────────
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys
          .filter(function(key) { return key !== CACHE_NAME; })
          .map(function(key) { return caches.delete(key); })
      );
    }).then(function() {
      return self.clients.claim(); // assume controle de todas as abas abertas
    })
  );
});

// ── Fetch: tenta rede primeiro, cai no cache se offline ─────────────────────
self.addEventListener('fetch', function(event) {
  // Ignora requisições que não sejam GET (POST para Sheets, etc.)
  if (event.request.method !== 'GET') return;

  // Ignora requisições externas (CDNs, Sheets, QR API)
  var url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    fetch(event.request)
      .then(function(response) {
        // Atualiza o cache com a versão nova da rede
        if (response && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, clone);
          });
        }
        return response;
      })
      .catch(function() {
        // Sem internet — serve do cache
        return caches.match(event.request);
      })
  );
});

// ── Mensagem para forçar update manual ──────────────────────────────────────
self.addEventListener('message', function(event) {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});
