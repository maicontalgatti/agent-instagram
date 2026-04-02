# Agente Instagram — seleção editorial multi-fonte

Pipeline **production-ready** que **varre várias fontes tech** (RSS + NewsAPI), **normaliza** artigos, **deduplica**, **classifica tema**, **pontua relevância e frescor**, escolhe a **melhor pauta do momento**, gera **legenda** e **imagem** (DALL·E + Cloudinary) e publica no **Instagram** (Graph API com espera `FINISHED`).

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
    image_prompt_builder.py # Prompt rico para DALL·E (composição + estética)
    post_builder.py
    image_generator.py      # DALL·E + Cloudinary
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
- Chaves: **OpenAI** (obrigatório para legenda/imagem), **Cloudinary**, **Instagram**; **NewsAPI** opcional mas recomendada (mais matéria).

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

**Dry-run** — executa coleta, dedup, score, top 5, escolhe a melhor e gera **legenda + prompt de imagem**; **não** chama DALL·E nem Instagram:

```bash
python src/main.py --mode select_and_post --dry-run
```

Requer `OPENAI_API_KEY` também no dry-run (legenda e prompt vêm do GPT). Sem ela, o comando encerra com erro explícito.

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
