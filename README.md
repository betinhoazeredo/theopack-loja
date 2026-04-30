# Theopack - Loja Virtual

Loja virtual da Theopack com integração completa ao ERP Omie.

## Funcionalidades

- Catálogo de produtos sincronizado com Omie
- Consulta de estoque em tempo real
- Checkout com criação automática de pedidos no Omie
- Cadastro automático de clientes
- Acompanhamento de status do pedido
- Formas de pagamento sincronizadas

## Estrutura do Projeto

```
theopack-loja/
├── omie_api/              # Módulo de integração com API Omie
│   ├── config.py          # Configurações e credenciais
│   ├── client.py          # Cliente base da API
│   └── loja_virtual.py    # Funções específicas para e-commerce
├── omie_api_validacao.py  # Script de validação da integração
└── Documentacao_Integracao_Omie.md  # Documentação completa
```

## Tecnologias

- **Backend:** Python (integração Omie)
- **Frontend:** Em desenvolvimento
- **Hospedagem:** Hostinger
- **ERP:** Omie

## Status

- [x] Integração API Omie configurada e testada
- [x] Módulo de loja virtual (catálogo, checkout, clientes)
- [ ] Front-end da loja virtual
- [ ] Deploy na Hostinger
- [ ] Domínio theopack.com.br configurado