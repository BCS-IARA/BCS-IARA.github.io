// IARA BCS — Service Worker
// Atualiza o número de versão a cada novo deploy para forçar refresh nos clientes
const CACHE_NAME = 'iara-bcs-v16';

// Arquivos essenciais para funcionar offline
// HTMLs não entram no precache — sempre buscados da rede (nunca ficam presos)
const PRECACHE = [
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

// ── Fetch: arquivos HTML sempre da rede; resto: rede primeiro, cache fallback ─
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;

  var url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  // Arquivos HTML (.html) e o próprio sw.js: NUNCA do cache — sempre rede
  var pathname = url.pathname;
  var isHtml = pathname.endsWith('.html') || pathname === '/' || pathname.endsWith('sw.js');
  if (isHtml) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' })
        .catch(function() {
          return caches.match(event.request); // offline: fallback do cache
        })
    );
    return;
  }

  // Outros assets (manifest, ícones): rede primeiro, atualiza cache
  event.respondWith(
    fetch(event.request)
      .then(function(response) {
        if (response && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, clone);
          });
        }
        return response;
      })
      .catch(function() {
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
