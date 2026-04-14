# 🛒 E-Commerce Full Stack

Projeto completo de e-commerce desenvolvido com arquitetura moderna, incluindo backend robusto, autenticação segura, pagamentos integrados e painel administrativo.

---

## 🚀 Tecnologias utilizadas

### 🔙 Backend
- FastAPI
- MySQL
- SQLAlchemy
- JWT (JSON Web Token)
- Pydantic

### 🎨 Frontend
- React / Next.js
- TypeScript
- CSS / Tailwind

### 💳 Integrações
- MercadoPago API

---

## ⚙️ Funcionalidades

### 🔐 Autenticação
- Cadastro e login de usuários
- Autenticação via JWT
- Proteção de rotas privadas

### 🛍️ Produtos
- Listagem de produtos
- Página de detalhes
- Upload de imagens
- Controle de estoque

### 🛒 Carrinho
- Adicionar/remover produtos
- Atualização dinâmica de quantidade

### 📦 Endereços e Frete
- Cadastro de múltiplos endereços
- Cálculo de frete
- Seleção de endereço na compra

### 💳 Pagamentos
- Integração com MercadoPago
- Checkout seguro
- Confirmação de pagamento

### 🧑‍💼 Painel Administrativo
- CRUD de produtos
- Gerenciamento de pedidos
- Controle de usuários
- Upload e gerenciamento de imagens

---

## 🧱 Estrutura do Projeto

```bash
ecommerce/
│
├── backend/
│   ├── app/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   └── main.py
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── styles/
│
└── README.md
```

---

## 🔑 Autenticação (JWT)

A autenticação é baseada em tokens JWT:

- Login retorna um token
- Token deve ser enviado no header:

```bash
Authorization: Bearer SEU_TOKEN
```

---

## 🖼️ Upload de Imagens

- Upload via API
- Armazenamento local ou cloud
- Associação com produtos

---

## 💳 Integração com MercadoPago

- Criação de preferência de pagamento
- Redirecionamento para checkout
- Webhook para confirmação automática

---

## 📦 Sistema de Frete

- Baseado em endereço do usuário
- Possibilidade de integração com APIs externas (Correios, etc.)

---

## ▶️ Como rodar o projeto

### 🔧 Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

### 💻 Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Variáveis de Ambiente

Crie um arquivo `.env`:

```env
# Backend
DATABASE_URL=mysql://user:password@localhost/db
SECRET_KEY=sua_chave_secreta
ALGORITHM=HS256

# MercadoPago
MERCADO_PAGO_ACCESS_TOKEN=seu_token
```

---


## 📚 Aprendizados

- Construção de API REST com FastAPI
- Autenticação segura com JWT
- Integração com APIs externas
- Manipulação de arquivos (upload)
- Desenvolvimento full stack moderno

---

## 👨‍💻 Autor

Desenvolvido por **Guilherme Volpolini**

