# 🛒 E-commerce API — FastAPI + MySQL

API REST completa para e-commerce com autenticação, controle de estoque e gestão de pedidos.

---

## 📁 Estrutura do Projeto

```
ecommerce-api/
├── app/
│   ├── main.py            # Entrada da aplicação
│   ├── database.py        # Configuração do banco e sessão
│   ├── models/
│   │   └── models.py      # Modelos SQLAlchemy (tabelas)
│   ├── schemas/
│   │   └── schemas.py     # Schemas Pydantic (validação)
│   └── routers/
│       ├── categorias.py  # CRUD de categorias
│       ├── produtos.py    # CRUD de produtos
│       ├── clientes.py    # CRUD de clientes
│       └── pedidos.py     # CRUD de pedidos
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Instalação e Configuração

### 1. Clone e entre na pasta
```bash
cd ecommerce-api
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados MySQL

Crie o banco no MySQL:
```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configure o arquivo .env
```bash
cp .env.example .env
# Edite o .env com suas credenciais MySQL
```

Exemplo de `.env`:
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ecommerce_db
DB_USER=root
DB_PASSWORD=sua_senha
```

### 6. Inicie o servidor
```bash
uvicorn app.main:app --reload
```

As tabelas serão criadas automaticamente no primeiro start.

---

## 📚 Endpoints

### Acesse a documentação interativa
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Categorias `GET POST PUT DELETE /categorias`
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /categorias | Listar todas |
| GET | /categorias/{id} | Buscar por ID |
| POST | /categorias | Criar |
| PUT | /categorias/{id} | Atualizar |
| DELETE | /categorias/{id} | Deletar |

### Produtos `GET POST PUT DELETE /produtos`
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /produtos?nome=X&categoria_id=1 | Listar com filtros |
| GET | /produtos/{id} | Buscar por ID |
| POST | /produtos | Criar |
| PUT | /produtos/{id} | Atualizar |
| DELETE | /produtos/{id} | Deletar |

### Clientes `GET POST PUT DELETE /clientes`
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /clientes | Listar todos |
| GET | /clientes/{id} | Buscar por ID |
| POST | /clientes | Criar |
| PUT | /clientes/{id} | Atualizar |
| DELETE | /clientes/{id} | Deletar |

### Pedidos `GET POST PATCH DELETE /pedidos`
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /pedidos?cliente_id=1&status=pago | Listar com filtros |
| GET | /pedidos/{id} | Buscar por ID |
| POST | /pedidos | Criar pedido |
| PATCH | /pedidos/{id}/status | Atualizar status |
| DELETE | /pedidos/{id} | Deletar |

### Status dos Pedidos
`pendente` → `pago` → `enviado` → `entregue` / `cancelado`

---

## 🧪 Exemplo de Uso

### Criar um produto
```bash
curl -X POST http://localhost:8000/produtos \
  -H "Content-Type: application/json" \
  -d '{"nome": "Camiseta", "preco": 49.90, "estoque": 100}'
```

### Criar um pedido
```bash
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "itens": [
      {"produto_id": 1, "quantidade": 2}
    ]
  }'
```

### Atualizar status do pedido
```bash
curl -X PATCH http://localhost:8000/pedidos/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "pago"}'
```

---

## 🔧 Funcionalidades

- ✅ CRUD completo para Categorias, Produtos, Clientes e Pedidos
- ✅ Controle automático de estoque ao criar/cancelar pedidos
- ✅ Filtros por nome, categoria e status
- ✅ Validação de dados com Pydantic
- ✅ Documentação automática (Swagger + ReDoc)
- ✅ Suporte a CORS
- ✅ Relacionamentos entre tabelas com SQLAlchemy
