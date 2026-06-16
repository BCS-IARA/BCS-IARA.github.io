# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**IARA** — Sistema de Gestão Integrada da 77ª CIPM (Polícia Militar da Bahia, BCS). A Progressive Web App (PWA) for police unit management: occurrence tracking, community visits, projects, armament control, inventory, school liaison, VCM (violence against women), and AI assistant.

## Running the App

There is no build step. The app is a static PWA — open `index.html` directly in a browser or serve it with any static file server:

```
python -m http.server 8080
# then open http://localhost:8080
```

The Service Worker (`sw.js`) caches assets. Increment `CACHE_NAME` version in `sw.js` after any deploy to force clients to refresh.

## Architecture

### Single-file frontend (`index.html` — ~19,900 lines)

The entire application lives in one HTML file. It is structured as:

1. **CSS** (lines ~23–195) — CSS custom properties, layout, components, animations, responsive breakpoints
2. **CONFIG** — `SHEETS_URL` (Google Apps Script backend URL), `BCS_TOKEN`, PINs, `ANTHROPIC_KEY` (from `localStorage`)
3. **Persistence layer** — `salvarLocal()` / `carregarLocal()` / `exportarDadosBCS()` / `importarDadosBCS()`. Data lives in `localStorage` under keys prefixed `bcs_*`. Module-specific fields (escola, PS links on ocorrências) are isolated in `bcs_oc_modulos` to survive Sheets sync overwrites.
4. **Google Sheets sync** — `sincronizarSheets()` calls the Apps Script endpoint via JSONP (`<script>` tag injection). Primary data (ocorrências, atendimentos, visitas, agendamentos) sync to/from Sheets; secondary data stays only in `localStorage`.
5. **State object** (`state`) — global mutable object. `state.db` holds the main collections (`ocorrencias`, `atendimentos`, `visitas`, `agendamentos`). Other top-level keys: `perfil`, `tela`, `projetos`, `eventosAvulsos`, `policiais`, `vcmCasos`, etc.
6. **Router** — `renderTela()` (line ~10906) reads `state.tela` and calls the appropriate `render*` function. Navigation updates `state.tela` then calls `render()` (alias for `renderTela()`).
7. **Module render functions** — each screen is a pure function `renderXxx(main)` that sets `main.innerHTML`. Key modules:

| Function | Screen |
|---|---|
| `renderDashComandante` | Commander dashboard (KPIs, charts, heat map) |
| `renderTela` | Main router / occurrence list / forms |
| `renderCalendar` | Calendar with events |
| `renderChat` | AI assistant (Anthropic API via `localStorage` key) |
| `renderDashboardVCM` / `renderCadastrosVCM` | Violência contra a mulher |
| `renderGestaoProjectos` | Projects management |
| `renderProjetosSociais` | Social projects |
| `renderModuloEscolar` | School liaison |
| `renderInventario` | Inventory / patrimony |
| `renderLivroParteArmamento` | Armament logbook |
| `renderModuloConselho` | Community council |
| `renderPortalInstrutor` | Instructor portal |
| `renderSolicitacoesGestor` | Requests manager |
| `renderConfiguracoes` | Settings |

### Auxiliary HTML files

- `projetos.html` — standalone public portal for Projetos Sociais (read-only, seed data + Sheets sync)
- `inscricao.html` — public enrollment form for social projects
- `solicitacao.html` — public request form
- `candidatura.html` — job candidacy form
- `carga-armamento.html` — armament load form (standalone)
- `crav-devolutiva.html` — CRAV report page
- `qr-portfolio.html` — QR portfolio landing page
- `gerar_icones.html` — utility to generate PWA icons as base64

### Python utilities (data import)

- `gerar_json.py` — parses `SIGESPOL_01-01-2025_ate_07-05-2026.xlsx` → `BCS_importacao_sigespol.json`
- `importar_planilha.py` — general spreadsheet importer
- `process_sigespol.py` — SIGESPOL data processor
- `fix_parser.py` — parser fix utility
- `recuperar_datas.js` — date recovery from SIGESPOL JSON

### PWA

- `manifest.json` — PWA manifest
- `sw.js` — Service Worker (network-first for HTML, cache for assets)
- Icons embedded as base64 in `_b64_*.txt` and injected via `_inject*.js` scripts

## Key Conventions

### Data flow
- All writes go through `salvarLocal()` then optionally `sincronizarSheets()`
- Module-specific data on ocorrências must be saved to `bcs_oc_modulos` via `_salvarModulos()` — this key is immune to Sheets sync overwrites
- Deleted IDs tracked in `state._deletedEvIds`, `state._deletedMatIds`, etc. to prevent re-syncing deleted records

### Rendering
- All HTML generation uses string concatenation with the `esc()` helper for user-supplied values (XSS prevention)
- `render()` is a global alias for `renderTela()` — call it after any state mutation to re-render

### Authentication / access control
- `state.perfil` controls which sections are visible: `"gestor"`, `"operador"`, `"comandante"`, `"conselho"`, `"instrutor"`
- PINs for gestor/operador/comandante are validated server-side via the Apps Script endpoint
- `CONSELHO_PIN` and `INSTRUTOR_PIN` are hardcoded client-side (change before publishing)
- `BCS_TOKEN` must match the value in the Google Apps Script — change before publishing

### Sync / backend
- Backend is Google Apps Script (separate repo/deployment), accessed via `SHEETS_URL`
- All Sheets calls use JSONP pattern: inject a `<script src="...&callback=fnName">` tag
- `state.filaPendente` queues writes when offline; `sincronizarSheets()` flushes on reconnect
