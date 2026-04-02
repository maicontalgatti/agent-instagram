# Agente Instagram — seleção editorial multi-fonte

Pipeline **production-ready** que **varre várias fontes tech** (RSS + NewsAPI), **normaliza** artigos, **deduplica**, **classifica tema**, **pontua relevância e frescor**, escolhe a **melhor pauta do momento**, gera **legenda** e **imagem final estilo capa de portal** (`src/visual/`): prioriza **foto da notícia**, depois **logo de marca** (Clearbit), depois **DALL·E editorial**; aplica **template fixo** (gradiente, selo de categoria, título, `@marca`) e envia o JPEG ao **Cloudinary** antes do **Instagram** (Graph API com espera `FINISHED`).

Não é só “pegar uma notícia”: o sistema prioriza **recência**, **tema** (IA, big tech, segurança…), **força do título**, **bônus de fonte** e evita **repetir URLs/títulos** já postados (`data/editorial_state.json`).

---

## Arquitetura (`src/`)

```
src/
  config.py                 # Env + pesos, limites, query NewsAPI, idioma
  main.py                   # CLI: --mode select_and_post (padrão), rotate, mock_post…
  models/article.py         # Formato padronizado de artigo
  sources/
    source_registry.py      # Lista central de feeds RSS (TechCrunch, Verge, Wired…)
    rss_fetcher.py
    newsapi_fetcher.py
    site_fetcher.py         # Stub para scraping futuro
    keyword_filter.py       # Filtro legado (modo rotate/news)
    normalize.py
  ranking/
    deduplicator.py         # URL + título similar
    topic_classifier.py     # ai, big_tech, cybersecurity…
    freshness.py
    scorer.py               # Score editorial configurável
  content/
    caption_generator.py    # Legenda tech + CTAs
    image_prompt_builder.py # (opcional) prompts auxiliares
    post_builder.py
    image_generator.py      # DALL·E editorial + upload Cloudinary
  visual/
    image_pipeline.py       # build_post_image: notícia → marca → IA → template
    template_engine.py      # Composição 1080×1350, selo, título, @BRAND_HANDLE
    image_selector.py
    asset_fetcher.py
    brand_style.py
  publish/
    instagram_poster.py
  pipeline/
    select_and_post.py      # Fluxo principal select_and_post
  storage/
    state_store.py          # JSON: URLs/títulos já postados
    cache.py
  legacy/
    rotation.py             # Modo antigo: rotação news/curiosity/trend
  utils/
    logger.py, time_utils.py, text_utils.py, safe_log.py
  instagram_tester.py       # Só testa API Instagram (imagem fixa)
```

Se **uma fonte falhar**, as demais continuam (logs de aviso).

---

## Requisitos

- Python 3.10+
- Conta Instagram **Business/Creator** + **Página Facebook** + token Graph API
- Chaves: **OpenAI** (legenda + fallback de imagem IA se não houver foto/logo), **Cloudinary**, **Instagram**; **NewsAPI** opcional mas recomendada (mais matéria).
- **Pillow** (composição do template; instalado via `requirements.txt`).

```bash
pip install -r requirements.txt
```

Copie `.env.example` → `.env` e preencha.

---

## Uso principal (recomendado)

**Pipeline completo** — busca multi-fonte, ranking, geração e postagem:

```bash
cd agent-instagram
python src/main.py --mode select_and_post
```

**Dry-run** — coleta, dedup, score, top 5, escolhe a melhor e gera **só a legenda**; **não** monta imagem nem publica:

```bash
python src/main.py --mode select_and_post --dry-run
```

Requer `OPENAI_API_KEY` no dry-run (só para a legenda). Sem ela, o comando encerra com erro explícito.

### Variáveis do módulo visual (`.env`)

- `USE_REAL_IMAGE`, `USE_BRAND_ASSET`, `USE_AI_FALLBACK` (padrão `true`)
- `MIN_IMAGE_WIDTH`, `BRAND_HANDLE` (padrão `technews.maik`)
- Saída local: `data/visual_output/`

---

## Modos legados

| Modo | Comando |
|------|---------|
| Rotação automática (news → curiosity → trend) | `python src/main.py --mode rotate` |
| Só notícia (NewsAPI + filtro keywords) | `python src/main.py --mode news` |
| Curiosidade / tendência | `python src/main.py --mode curiosity` ou `--mode trend` |
| Só testar Instagram (sem OpenAI de conteúdo) | `python src/main.py --mode mock_post` |

---

## Agendamento (cron, Linux)

```cron
0 9 * * * cd /caminho/agent-instagram && /caminho/agent-instagram/.venv/bin/python src/main.py --mode select_and_post >> /var/log/agent-instagram.log 2>&1
```

---

## Configuração avançada

- **Fontes RSS:** edite `src/sources/source_registry.py` (URLs de feed).
- **Pesos e janela de idade:** `src/config.py` ou variáveis no `.env` (ver `.env.example`).
- **Estado de postagens:** `data/editorial_state.json` (criado automaticamente; no `.gitignore`).

---

## Teste rápido só Instagram

```bash
python src/instagram_tester.py
```

---

## Critério de sucesso

Com `.env` válido:

```bash
python src/main.py --mode select_and_post
```

→ busca em paralelo (RSS + NewsAPI), ranqueia, gera conteúdo e publica, registrando o que já foi usado.
