# Agente de Postagem Automática no Instagram

Este projeto implementa um agente automatizado para pesquisar notícias de tecnologia, gerar imagens e legendas com inteligência artificial e postar diariamente no Instagram. O agente utiliza as seguintes APIs e serviços:

- **NewsAPI**: Para buscar notícias de tecnologia.
- **OpenAI (DALL-E e GPT-4.1-mini)**: Para gerar imagens e legendas.
- **Cloudinary**: Para hospedar as imagens geradas antes de postar no Instagram.
- **Instagram Graph API**: Para realizar as postagens no Instagram.

## Estrutura do Projeto

```
agent-instagram/
├── src/
│   ├── config.py
│   ├── content_generator.py
│   ├── image_generator.py
│   ├── instagram_poster.py
│   ├── instagram_tester.py
│   ├── main.py
│   └── news_fetcher.py
├── .env.example
├── README.md
└── requirements.txt
```

## Configuração

Para que o agente funcione corretamente, você precisará configurar as seguintes variáveis de ambiente:

1.  **Crie um arquivo `.env`** na raiz do projeto (`agent-instagram/`) com base no arquivo `.env.example`:

    ```dotenv
    # News API Key (https://newsapi.org/)
    NEWS_API_KEY=sua_chave_da_news_api

    # OpenAI API Key (https://platform.openai.com/)
    OPENAI_API_KEY=sua_chave_da_openai_api

    # Cloudinary Credentials (https://cloudinary.com/)
    CLOUDINARY_CLOUD_NAME=seu_cloud_name_cloudinary
    CLOUDINARY_API_KEY=sua_chave_da_cloudinary_api
    CLOUDINARY_API_SECRET=seu_segredo_da_cloudinary_api

    # Instagram Graph API Credentials (https://developers.facebook.com/)
    INSTAGRAM_ACCESS_TOKEN=seu_token_de_acesso_do_instagram
    INSTAGRAM_BUSINESS_ACCOUNT_ID=seu_id_de_conta_comercial_do_instagram
    ```

2.  **Obtenha as chaves das APIs:**
    *   **NewsAPI**: Registre-se em [newsapi.org](https://newsapi.org/) para obter sua chave de API.
    *   **OpenAI**: Obtenha sua chave de API em [platform.openai.com](https://platform.openai.com/).
    *   **Cloudinary**: Crie uma conta em [cloudinary.com](https://cloudinary.com/) e encontre suas credenciais no dashboard.
    *   **Instagram Graph API**: Este é o passo mais complexo, pois você precisará de uma conta do Instagram Business/Creator e uma página do Facebook conectada. Siga a documentação oficial do Facebook para desenvolvedores para obter um `INSTAGRAM_ACCESS_TOKEN` e o `INSTAGRAM_BUSINESS_ACCOUNT_ID`.
        *   [Começar com a Plataforma Instagram](https://developers.facebook.com/docs/instagram-platform/getting-started)
        *   [Configurar uma Conta Comercial no Instagram](https://www.facebook.com/business/help/898752980190821)

## Instalação das Dependências

Certifique-se de ter Python 3.x instalado. Em seguida, instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

## Execução do Agente

Para executar o agente manualmente, navegue até o diretório `agent-instagram` e execute o script `main.py`:

```bash
python src/main.py
```

## Teste de Publicação no Instagram

Se quiser validar somente a etapa de postagem (sem consumir créditos de NewsAPI/OpenAI), use o tester dedicado:

```bash
python src/instagram_tester.py
```

Esse script:
- cria uma mídia com imagem pública fixa;
- aguarda o processamento da mídia;
- consulta `status_code` até `FINISHED`;
- publica o post com `media_publish`.

### Variáveis obrigatórias no `.env`

```dotenv
INSTAGRAM_ACCESS_TOKEN=seu_token_de_acesso_do_instagram
INSTAGRAM_BUSINESS_ACCOUNT_ID=seu_id_de_conta_comercial_do_instagram
```

Se uma delas estiver ausente, o script encerra imediatamente.

## Agendamento Diário

O agente foi agendado para ser executado diariamente. No entanto, para que o agendamento funcione de forma persistente, você precisará garantir que o ambiente onde o agente está sendo executado (neste caso, o sandbox) esteja ativo ou que você configure um cron job em um servidor de sua preferência que possa acessar as variáveis de ambiente e executar o script `main.py`.

**Nota:** O agendamento foi configurado para rodar diariamente às 09:00 (horário do sistema onde o agente está rodando). Você pode ajustar isso conforme sua necessidade.

## Próximos Passos

1.  Crie sua conta no Instagram e converta-a para uma conta Business ou Creator.
2.  Conecte sua conta do Instagram a uma página do Facebook.
3.  Obtenha as credenciais necessárias para a Instagram Graph API.
4.  Preencha o arquivo `.env` com todas as suas chaves de API.
5.  Execute o agente para testar a postagem automática.

Se tiver alguma dúvida ou precisar de ajuda com a configuração, por favor, me informe!
