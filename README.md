# 🚀 AlmoxiBot

Bot de controle de estoque, registro de ordens de serviço e consulta
rápida, desenvolvido em Python com Telegram Bot API.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Ativo-success.svg)

------------------------------------------------------------------------

## 📌 **Descrição**

O **AlmoxiBot** é um bot do Telegram criado para ajudar técnicos e
equipes de campo a registrar, consultar e organizar informações como:

-   📝 Ordem de Serviço (OS)\
-   🔢 Serial da ONT\
-   📸 Até 2 fotos por registro\
-   📅 Data e hora automaticamente\
-   🔍 Consultas por SA (OS), Serial ou todos os registros

Tudo é salvo localmente em um banco SQLite.

------------------------------------------------------------------------

## 📁 **Estrutura do Projeto**

    AlmoxiBot/
    │── bot/
    │   ├── main.py
    │   ├── handlers.py
    │   ├── registry.py
    │   ├── consulta.py
    │   ├── database.py
    │   ├── utils.py
    │
    │── data/          # Banco de dados (ignorado no git)
    │── images/        # Imagens recebidas (ignorado no git)
    │── .env           # Token do bot e configs (IGNORADO)
    │── .gitignore
    │── requirements.txt
    │── README.md

------------------------------------------------------------------------

## 🔒 **Segurança**

O projeto utiliza um arquivo `.env` para armazenar informações
sensíveis:

    BOT_TOKEN=SEU_TOKEN_AQUI
    DB_PATH=data/user.db
    IMAGES_PATH=images

O `.env`, o banco de dados e as imagens **não são enviados ao GitHub**,
pois estão declarados no `.gitignore`.

------------------------------------------------------------------------

## 🛠️ **Tecnologias Utilizadas**

-   **Python 3.10+**
-   **pyTelegramBotAPI (Telebot)**\
-   **SQLite3**
-   **python-dotenv**

------------------------------------------------------------------------

## 📦 **Instalação**

### 1. Clone o repositório:

``` bash
git clone https://github.com/machadopy/botmachado.git
cd botmachado
```

### 2. Crie um ambiente virtual:

``` bash
python -m venv .venv
```

### 3. Ative o ambiente virtual:

**Windows**

``` bash
.venv\Scripts\activate
```

**Linux/Mac**

``` bash
source .venv/bin/activate
```

### 4. Instale as dependências:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## ⚙️ **Configuração do .env**

Crie um arquivo `.env` na raiz do projeto:

``` env
BOT_TOKEN=SEU_TOKEN_AQUI
DB_PATH=data/user.db
IMAGES_PATH=images
```

------------------------------------------------------------------------

## ▶️ **Como Rodar**

``` bash
python bot/main.py
```

------------------------------------------------------------------------

## 🔍 **Funcionalidades**

### ✔️ Registro de OS

-   Ordem de Serviço
-   Serial da ONT
-   Até 2 fotos
-   Data/Hora automática

### ✔️ Consulta Rápida

-   Por O.S (SA)
-   Por Serial ONT
-   Mostrar todos
-   Exibe fotos relacionadas

------------------------------------------------------------------------

## 📚 **Banco de Dados**

O banco SQLite é gerado automaticamente:

-   `users`
-   `registros`
-   `imagens`

------------------------------------------------------------------------

## 🤝 **Contribuição**

Pull Requests são bem-vindos!

------------------------------------------------------------------------

## 📄 **Licença**

MIT License

------------------------------------------------------------------------

## 👨‍💻 **Autor**

**Machado**\
GitHub: https://github.com/machadopy
