# Agente Instagram — conteúdo com voz, não só autopost

Este projeto **não é um “bot que repete o mesmo tipo de post”**. Ele combina **seleção de notícias**, **três linhas editoriais** que alternam sozinhas, **gêneros de legenda** variados, **CTAs** que mudam e um **estilo visual fixo** (imagens claras, minimalistas, sem poluição típica de “wallpaper de tecnologia”).

O fluxo usa **NewsAPI**, **OpenAI** (GPT para texto e DALL·E para imagem), **Cloudinary** (URL pública para o Instagram) e a **Instagram Graph API**, com postagem que **espera a mídia ficar pronta** antes de publicar.

---

## O que agrega valor (em resumo)

| Aspecto | Comportamento |
|--------|----------------|
| **Tipos de conteúdo** | Rotação automática entre **notícias**, **curiosidades** (“você sabia…”) e **tendências** — cada execução segue para o próximo tipo (estado em `post_mode_index.txt`). |
| **Notícias** | Filtro por **palavras-chave** + escolha da melhor pauta por **score de impacto** (ex.: menções a IA, grandes empresas, “lançamento”, “novo”). Evita repostar o mesmo título com `used_titles.txt`. |
| **Gêneros de legenda** (modo notícia) | Estilo escolhido **aleatoriamente** a cada post: **notícia direta**, **explicativo para leigos** ou **opinião provocativa** — o tom muda, o feed não parece monocórdico. |
| **CTAs** | Um **chamado à ação** aleatório no fim da legenda (pergunta ou “comenta aqui”), para parecer mais conversa e menos robô. |
| **Imagem** | Prompts orientados a **estética editorial minimalista**: poucos elementos, fundo claro/neutro, sem texto na arte; o código ainda **reforça esse estilo** em toda chamada ao DALL·E. |
| **Segurança no console** | Respostas de API e URLs sensíveis passam por **sanitização** antes de ir para log/terminal (`safe_log`). |

Modo **manual** (não altera a rotação): `python src/main.py news` | `curiosity` | `trend`.

---

## Estrutura do projeto

```
agent-instagram/
├── src/
│   ├── config.py
│   ├── content_generator.py   # gêneros de legenda, CTAs, curiosidade/tendência
│   ├── image_generator.py     # DALL·E + Cloudinary
│   ├── instagram_poster.py    # Graph API + espera FINISHED
│   ├── instagram_tester.py    # só testa postagem (imagem fixa)
│   ├── main.py                # rotação + pipeline completo
│   ├── news_fetcher.py        # keywords, relevância, score
│   └── safe_log.py
├── assets/                    # imagem padrão (ex.: modo teste)
├── .env.example
├── README.md
└── requirements.txt
```

Arquivos locais (gerados ao rodar; listados no `.gitignore`): `used_titles.txt`, `post_mode_index.txt`.

---

## Configuração

1. **Crie um `.env`** na raiz do projeto com base em `.env.example` (News API, OpenAI, Cloudinary, Instagram). Opcional: `DEFAULT_POST_IMAGE_URL` para o modo teste sem upload no Cloudinary.

2. **Chaves e documentação**
   - [NewsAPI](https://newsapi.org/)
   - [OpenAI](https://platform.openai.com/)
   - [Cloudinary](https://cloudinary.com/)
   - [Instagram Platform](https://developers.facebook.com/docs/instagram-platform/getting-started)

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Execução

**Fluxo completo com rotação automática** (recomendado no dia a dia):

```bash
cd agent-instagram
python src/main.py
```

**Forçar um tipo** (testes):

```bash
python src/main.py news
python src/main.py curiosity
python src/main.py trend
```

**Só validar postagem no Instagram** (imagem pública fixa, sem News/OpenAI de conteúdo):

```bash
python src/instagram_tester.py
```

Requer `INSTAGRAM_ACCESS_TOKEN` e `INSTAGRAM_BUSINESS_ACCOUNT_ID` no `.env`.

---

## Agendamento (cron, Linux)

Execute **sempre a partir da raiz do repositório** para que `used_titles.txt`, `post_mode_index.txt` e `assets/` resolvam corretamente. Use o Python do virtualenv.

Exemplo (todo dia às 9h; ajuste caminhos):

```cron
0 9 * * * cd /var/www/agent-instagram && /var/www/agent-instagram/.venv/bin/python src/main.py >> /var/log/agent-instagram.log 2>&1
```

No Windows, use o **Agendador de Tarefas** com o mesmo princípio: diretório de trabalho = pasta do projeto.

---

## Checklist rápido

1. Conta Instagram **Business** ou **Creator** ligada a uma **Página do Facebook**.
2. `.env` preenchido com todas as variáveis necessárias.
3. Primeiro teste opcional com `instagram_tester.py`; depois `python src/main.py`.

Se algo falhar na Graph API, confira token, permissões e se a imagem está em **URL HTTPS pública** (Cloudinary ou variável `DEFAULT_POST_IMAGE_URL` no modo teste).
