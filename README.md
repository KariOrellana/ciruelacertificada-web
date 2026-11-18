# ciruelacertificada-web

Maqueta estática del sitio **ciruelacertificada.cl** (reemplazo de WordPress).

- `site/` — el sitio publicado (HTML, CSS, imágenes, PDF y medios de verificación).
- `content/` — textos y datos editables (`config.json`, `estandar.json`).
- `tools/build.py` — genera Recursos, Auditores, Preguntas frecuentes y los bloques de la portada a partir de `content/` y de `material-nuevo/` (no se versiona).
- `.github/workflows/pages.yml` — publica `site/` en GitHub Pages en cada push a `main`.

Los cambios se piden y se aplican con `python3 tools/build.py`.
