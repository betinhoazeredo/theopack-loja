"""
Theopack - Módulo de Integração Loja Virtual com Omie
Funções específicas para e-commerce: catálogo, carrinho, checkout, pedidos.
"""

import time
from typing import Dict, List, Optional
from .client import OmieClient


class OmieLojaVirtual:
    """Integração da loja virtual Theopack com o ERP Omie."""
    
    def __init__(self, client: OmieClient = None):
        self.client = client or OmieClient()
    
    # ==========================================
    # CATÁLOGO DE PRODUTOS (LOJA VIRTUAL)
    # ==========================================
    
    def obter_catalogo(self, pagina: int = 1, registros: int = 50) -> Dict:
        """
        Obtém o catálogo de produtos formatado para a loja virtual.
        Retorna produtos com informações relevantes para exibição.
        """
        data = self.client.listar_produtos(pagina=pagina, registros=registros)
        produtos_raw = data.get("produto_servico_cadastro", [])
        
        catalogo = []
        for prod in produtos_raw:
            item = {
                "id_omie": prod.get("codigo_produto"),
                "codigo": prod.get("codigo"),
                "nome": prod.get("descricao", ""),
                "descricao_detalhada": prod.get("descricao_detalhada", ""),
                "preco": prod.get("valor_unitario", 0),
                "unidade": prod.get("unidade", "UN"),
                "ncm": prod.get("ncm", ""),
                "peso_bruto": prod.get("peso_bruto", 0),
                "peso_liquido": prod.get("peso_liq", 0),
                "marca": prod.get("marca", ""),
                "modelo": prod.get("modelo", ""),
                "ativo": not prod.get("inativo", False),
                "imagens": prod.get("imagens", []),
                "familia": prod.get("codigo_familia", ""),
                "ean": prod.get("ean", ""),
            }
            catalogo.append(item)
        
        return {
            "produtos": catalogo,
            "pagina": data.get("pagina", pagina),
            "total_paginas": data.get("total_de_paginas", 1),
            "total_produtos": data.get("total_de_registros", 0)
        }
    
    def obter_produto_detalhe(self, codigo_produto: int) -> Dict:
        """Obtém detalhes completos de um produto para página de produto."""
        prod = self.client.consultar_produto(codigo_produto=codigo_produto)
        
        # Consultar estoque do produto
        try:
            estoque = self.client.consultar_estoque_produto(codigo_produto)
            qtd_estoque = 0
            produtos_estoque = estoque.get("produtos", [])
            for p in produtos_estoque:
                if p.get("nCodProd") == codigo_produto:
                    qtd_estoque = p.get("nSaldo", 0)
                    break
        except:
            qtd_estoque = 0
        
        return {
            "id_omie": prod.get("codigo_produto"),
            "codigo": prod.get("codigo", ""),
            "nome": prod.get("descricao", ""),
            "descricao_detalhada": prod.get("descricao_detalhada", ""),
            "preco": prod.get("valor_unitario", 0),
            "unidade": prod.get("unidade", "UN"),
            "estoque_disponivel": qtd_estoque,
            "peso_bruto": prod.get("peso_bruto", 0),
            "peso_liquido": prod.get("peso_liq", 0),
            "marca": prod.get("marca", ""),
            "modelo": prod.get("modelo", ""),
            "ean": prod.get("ean", ""),
            "ncm": prod.get("ncm", ""),
            "imagens": prod.get("imagens", []),
            "ativo": not prod.get("inativo", False),
        }
    
    def verificar_disponibilidade(self, codigo_produto: int, quantidade: float = 1) -> Dict:
        """Verifica se um produto está disponível em estoque."""
        try:
            estoque = self.client.consultar_estoque_produto(codigo_produto)
            produtos = estoque.get("produtos", [])
            for p in produtos:
                if p.get("nCodProd") == codigo_produto:
                    saldo = p.get("nSaldo", 0)
                    return {
                        "disponivel": saldo >= quantidade,
                        "saldo_atual": saldo,
                        "quantidade_solicitada": quantidade
                    }
            return {"disponivel": False, "saldo_atual": 0, "quantidade_solicitada": quantidade}
        except Exception as e:
            return {"disponivel": False, "erro": str(e)}
    
    # ==========================================
    # CHECKOUT / PEDIDOS
    # ==========================================
    
    def criar_pedido_loja(self, cliente_data: Dict, itens: List[Dict], 
                          forma_pagamento: str = "000",
                          observacoes: str = "",
                          codigo_pedido_integracao: str = None) -> Dict:
        """
        Cria um pedido de venda no Omie a partir de uma compra na loja virtual.
        
        Args:
            cliente_data: Dados do cliente (codigo_cliente_omie ou dados para cadastro)
            itens: Lista de itens [{codigo_produto, quantidade, valor_unitario}]
            forma_pagamento: Código da forma de pagamento
            observacoes: Observações do pedido
            codigo_pedido_integracao: Código único para integração
        
        Returns:
            Resultado da criação do pedido
        """
        # Garantir que o cliente existe no Omie
        codigo_cliente = cliente_data.get("codigo_cliente_omie")
        
        if not codigo_cliente:
            # Cadastrar/atualizar cliente
            cliente_result = self.cadastrar_cliente_loja(cliente_data)
            codigo_cliente = cliente_result.get("codigo_cliente_omie")
        
        # Montar itens do pedido
        det = []
        for i, item in enumerate(itens, 1):
            det.append({
                "ide": {"codigo_item_integracao": str(i)},
                "produto": {
                    "codigo_produto": item["codigo_produto"],
                    "quantidade": item["quantidade"],
                    "valor_unitario": item["valor_unitario"],
                },
                "inf_adic": {
                    "peso_bruto": item.get("peso_bruto", 0),
                    "peso_liquido": item.get("peso_liquido", 0),
                }
            })
        
        # Montar pedido
        pedido = {
            "cabecalho": {
                "codigo_cliente": codigo_cliente,
                "codigo_pedido_integracao": codigo_pedido_integracao or f"LOJA-{int(time.time())}",
                "data_previsao": time.strftime("%d/%m/%Y"),
                "etapa": "10",  # 10 = Pedido, 20 = Separar, 50 = Faturar
                "codigo_parcela": forma_pagamento,
            },
            "det": det,
            "informacoes_adicionais": {
                "consumidor_final": "S",
                "enviar_email": "S",
            },
            "observacoes": {
                "obs_venda": observacoes or "Pedido realizado via Loja Virtual Theopack"
            }
        }
        
        return self.client.incluir_pedido(pedido)
    
    def consultar_status_pedido(self, codigo_pedido: int = None,
                                 codigo_pedido_integracao: str = None) -> Dict:
        """Consulta o status de um pedido da loja virtual."""
        pedido = self.client.consultar_pedido(
            codigo_pedido=codigo_pedido,
            codigo_pedido_integracao=codigo_pedido_integracao
        )
        
        cabecalho = pedido.get("cabecalho", {})
        etapa = cabecalho.get("etapa", "")
        
        # Mapear etapas para status amigável
        status_map = {
            "10": "Pedido Recebido",
            "20": "Em Separação",
            "30": "Separado",
            "40": "Em Expedição",
            "50": "Faturado",
            "60": "Entregue",
            "70": "Concluído",
            "80": "Cancelado",
        }
        
        return {
            "codigo_pedido": cabecalho.get("codigo_pedido"),
            "numero_pedido": cabecalho.get("numero_pedido"),
            "etapa_codigo": etapa,
            "status": status_map.get(etapa, f"Etapa {etapa}"),
            "data_previsao": cabecalho.get("data_previsao", ""),
            "bloqueado": cabecalho.get("bloqueado", "N"),
            "total_pedido": pedido.get("total_pedido", {}),
        }
    
    # ==========================================
    # CLIENTES (LOJA VIRTUAL)
    # ==========================================
    
    def cadastrar_cliente_loja(self, dados: Dict) -> Dict:
        """
        Cadastra ou atualiza um cliente da loja virtual no Omie.
        
        Args:
            dados: {
                nome_fantasia, razao_social, cnpj_cpf, email,
                telefone, cep, endereco, numero, complemento,
                bairro, cidade, estado, pessoa_fisica (S/N)
            }
        """
        cliente = {
            "codigo_cliente_integracao": dados.get("codigo_cliente_integracao", 
                                                    f"LOJA-{dados.get('cnpj_cpf', '').replace('.','').replace('-','').replace('/','')}"
                                                   ),
            "razao_social": dados.get("razao_social", dados.get("nome_fantasia", "")),
            "nome_fantasia": dados.get("nome_fantasia", ""),
            "cnpj_cpf": dados.get("cnpj_cpf", ""),
            "email": dados.get("email", ""),
            "telefone1_numero": dados.get("telefone", ""),
            "endereco": dados.get("endereco", ""),
            "endereco_numero": dados.get("numero", ""),
            "complemento": dados.get("complemento", ""),
            "bairro": dados.get("bairro", ""),
            "cidade": dados.get("cidade", ""),
            "estado": dados.get("estado", ""),
            "cep": dados.get("cep", ""),
            "pessoa_fisica": dados.get("pessoa_fisica", "S"),
            "contribuinte": "2" if dados.get("pessoa_fisica", "S") == "S" else "1",
        }
        
        return self.client.upsert_cliente(cliente)
    
    def buscar_cliente_por_cpf_cnpj(self, cpf_cnpj: str) -> Optional[Dict]:
        """Busca um cliente pelo CPF/CNPJ."""
        try:
            data = self.client.listar_clientes(pagina=1, registros=1, filtros={
                "cnpj_cpf": cpf_cnpj
            })
            clientes = data.get("clientes_cadastro", [])
            return clientes[0] if clientes else None
        except:
            return None
    
    # ==========================================
    # CATEGORIAS / FAMÍLIAS (MENU DA LOJA)
    # ==========================================
    
    def obter_categorias_loja(self) -> List[Dict]:
        """Obtém as categorias/famílias de produtos para menu da loja."""
        familias = self.client.listar_familias_produto()
        return [
            {
                "id": f.get("codigo"),
                "nome": f.get("nomeFamilia", ""),
            }
            for f in familias
        ]
    
    # ==========================================
    # FORMAS DE PAGAMENTO
    # ==========================================
    
    def obter_formas_pagamento(self) -> List[Dict]:
        """Obtém as formas de pagamento disponíveis para a loja."""
        formas = self.client.listar_formas_pagamento()
        return [
            {
                "codigo": f.get("cCodigo", ""),
                "descricao": f.get("cDescricao", ""),
                "parcelas": f.get("nQtdeParc", 1),
            }
            for f in formas
        ]
    
    # ==========================================
    # RELATÓRIOS / DASHBOARD
    # ==========================================
    
    def resumo_loja(self) -> Dict:
        """Retorna resumo operacional para dashboard da loja."""
        return self.client.resumo_operacional()
