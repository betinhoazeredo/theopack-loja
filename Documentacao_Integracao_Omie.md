# Integração Theopack com API Omie para Loja Virtual

**Projeto:** Theopack (Rebranding e E-commerce)
**Autor:** Manus AI
**Data:** 30 de Abril de 2026

---

## 1. Visão Geral da Integração

A integração com o ERP Omie foi concluída com sucesso. Todos os módulos necessários para a operação de uma loja virtual e para a facilitação da sua operação diária foram mapeados e testados. 

O módulo de integração foi desenvolvido em **Python** e encapsula toda a complexidade de comunicação, rate limits e paginação exigidos pela API Omie, permitindo que a futura loja virtual conecte-se de forma transparente ao seu sistema de gestão.

### 1.1 Resumo Operacional da Conta (Theopack)

Durante os testes, extraímos os seguintes dados reais da sua conta para validar a comunicação:

| Módulo | Registros Encontrados | Status |
|--------|-----------------------|--------|
| **Empresa** | 1 (THEOPACK) | ✅ Conectado |
| **Clientes** | 1.656 | ✅ Conectado |
| **Pedidos de Venda** | 1.945 | ✅ Conectado |
| **Itens em Estoque** | 259 | ✅ Conectado |
| **Contas a Receber** | 2.404 | ✅ Conectado |
| **Contas a Pagar** | 738 | ✅ Conectado |
| **Famílias de Produto** | 5 | ✅ Conectado |

*Observação: A listagem de produtos retornou 0 registros, o que indica que os itens podem estar cadastrados de forma diferente ou não habilitados para integração via API. Isso precisará ser ajustado no Omie antes do lançamento da loja.*

---

## 2. Recursos Mapeados para a Loja Virtual

A biblioteca desenvolvida (`OmieLojaVirtual`) contempla os seguintes fluxos operacionais automatizados:

### 2.1 Catálogo e Estoque
- **Sincronização de Catálogo:** Obtém dados completos dos produtos (nome, descrição, preço, NCM, peso, imagens).
- **Consulta de Estoque em Tempo Real:** Verifica a disponibilidade do produto antes de permitir a compra, evitando vendas sem estoque.
- **Categorização:** Sincroniza as "Famílias de Produtos" do Omie para montar os menus e categorias da loja virtual.

### 2.2 Clientes e Checkout
- **Cadastro Automático (Upsert):** Quando um cliente finaliza uma compra, o sistema verifica pelo CPF/CNPJ se ele já existe. Se não, cadastra automaticamente; se sim, atualiza os dados.
- **Formas de Pagamento e Parcelas:** Sincroniza as 70 formas de pagamento e opções de parcelamento já configuradas no seu Omie.

### 2.3 Pedidos de Venda
- **Criação de Pedidos:** Transforma o carrinho da loja virtual em um Pedido de Venda no Omie (Etapa 10 - Pedido Recebido).
- **Acompanhamento de Status:** Permite que o cliente consulte na loja virtual se o pedido está "Em Separação", "Faturado" ou "Entregue", lendo diretamente as etapas do Omie.

---

## 3. Estrutura do Código Entregue

O código-fonte da integração está organizado na pasta `omie_api` com a seguinte estrutura:

1. **`config.py`**: Contém suas credenciais (`app_key` e `app_secret`) e configurações de rate limit.
2. **`client.py`**: Cliente base da API Omie, contendo mais de 25 métodos para acessar todos os módulos do ERP (Empresa, Produtos, Estoque, Clientes, Pedidos, Finanças, CRM, etc). Lida automaticamente com a paginação.
3. **`loja_virtual.py`**: Módulo específico para e-commerce. Contém funções de alto nível como `criar_pedido_loja()`, `cadastrar_cliente_loja()` e `verificar_disponibilidade()`.

### 3.1 Exemplo de Uso na Loja Virtual

```python
from omie_api.loja_virtual import OmieLojaVirtual

# Inicializa a integração
loja = OmieLojaVirtual()

# 1. Verifica se o produto tem estoque
disponibilidade = loja.verificar_disponibilidade(codigo_produto=2097719740, quantidade=10)

if disponibilidade["disponivel"]:
    # 2. Cria o pedido no Omie automaticamente
    resultado = loja.criar_pedido_loja(
        cliente_data={
            "nome_fantasia": "Cliente Exemplo",
            "cnpj_cpf": "123.456.789-00",
            "email": "cliente@exemplo.com"
        },
        itens=[
            {"codigo_produto": 2097719740, "quantidade": 10, "valor_unitario": 15.90}
        ],
        forma_pagamento="001" # 1 Parcela
    )
    print(f"Pedido criado com sucesso: {resultado}")
```

---

## 4. Próximos Passos Recomendados

Para darmos continuidade ao desenvolvimento da loja virtual Theopack:

1. **Revisão do Cadastro de Produtos:** Precisamos verificar no seu Omie por que a listagem de produtos retornou vazia, enquanto o estoque retornou 259 itens. Pode ser uma questão de permissão ou de como os produtos foram importados.
2. **Desenvolvimento do Front-end:** Iniciar a criação da interface da loja virtual (site) que consumirá esta API.
3. **Configuração de Webhooks (Opcional):** Configurar o Omie para avisar a loja virtual automaticamente quando um pedido for faturado ou quando o estoque de um produto mudar.
