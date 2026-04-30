"""
Theopack - Cliente Principal da API Omie
Classe unificada para todas as operações com a API.
"""

import requests
import json
import time
from typing import Optional, Dict, Any, List
from .config import OMIE_APP_KEY, OMIE_APP_SECRET, OMIE_API_BASE_URL, DEFAULT_PAGE_SIZE


class OmieClient:
    """Cliente para integração com a API Omie."""
    
    def __init__(self, app_key: str = None, app_secret: str = None):
        self.app_key = app_key or OMIE_APP_KEY
        self.app_secret = app_secret or OMIE_APP_SECRET
        self.base_url = OMIE_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _request(self, endpoint: str, call: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma requisição à API Omie."""
        url = f"{self.base_url}/{endpoint}/"
        payload = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "call": call,
            "param": [params]
        }
        
        response = self.session.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def _list_all(self, endpoint: str, call: str, params: Dict[str, Any], 
                  data_key: str, page_key: str = "pagina", 
                  page_size_key: str = "registros_por_pagina",
                  total_pages_key: str = "total_de_paginas") -> List[Dict]:
        """Lista todos os registros com paginação automática."""
        all_records = []
        page = 1
        
        while True:
            params[page_key] = page
            params[page_size_key] = DEFAULT_PAGE_SIZE
            
            data = self._request(endpoint, call, params)
            records = data.get(data_key, [])
            all_records.extend(records)
            
            total_pages = data.get(total_pages_key, 1)
            if page >= total_pages:
                break
            page += 1
            time.sleep(0.3)  # Rate limit
        
        return all_records

    # ==========================================
    # EMPRESA
    # ==========================================
    
    def listar_empresas(self) -> List[Dict]:
        """Lista as empresas cadastradas."""
        data = self._request("geral/empresas", "ListarEmpresas", {
            "pagina": 1, "registros_por_pagina": 50
        })
        return data.get("empresas_cadastro", [])
    
    # ==========================================
    # PRODUTOS
    # ==========================================
    
    def listar_produtos(self, pagina: int = 1, registros: int = DEFAULT_PAGE_SIZE, 
                        filtros: Dict = None) -> Dict:
        """Lista produtos com paginação."""
        params = {
            "pagina": pagina,
            "registros_por_pagina": registros,
            "apenas_importado_api": "N"
        }
        if filtros:
            params.update(filtros)
        return self._request("geral/produtos", "ListarProdutos", params)
    
    def listar_todos_produtos(self) -> List[Dict]:
        """Lista todos os produtos (paginação automática)."""
        return self._list_all("geral/produtos", "ListarProdutos",
                             {"apenas_importado_api": "N"},
                             "produto_servico_cadastro")
    
    def consultar_produto(self, codigo_produto: int = None, 
                          codigo_produto_integracao: str = None) -> Dict:
        """Consulta um produto específico."""
        params = {}
        if codigo_produto:
            params["codigo_produto"] = codigo_produto
        if codigo_produto_integracao:
            params["codigo_produto_integracao"] = codigo_produto_integracao
        return self._request("geral/produtos", "ConsultarProduto", params)
    
    def incluir_produto(self, produto: Dict) -> Dict:
        """Inclui um novo produto."""
        return self._request("geral/produtos", "IncluirProduto", produto)
    
    def alterar_produto(self, produto: Dict) -> Dict:
        """Altera um produto existente."""
        return self._request("geral/produtos", "AlterarProduto", produto)
    
    def excluir_produto(self, codigo_produto: int = None,
                        codigo_produto_integracao: str = None) -> Dict:
        """Exclui um produto."""
        params = {}
        if codigo_produto:
            params["codigo_produto"] = codigo_produto
        if codigo_produto_integracao:
            params["codigo_produto_integracao"] = codigo_produto_integracao
        return self._request("geral/produtos", "ExcluirProduto", params)
    
    def listar_familias_produto(self) -> List[Dict]:
        """Lista as famílias/categorias de produtos."""
        data = self._request("geral/familias", "PesquisarFamilias", {
            "pagina": 1, "registros_por_pagina": 500
        })
        return data.get("famCadastro", [])
    
    # ==========================================
    # ESTOQUE
    # ==========================================
    
    def consultar_estoque(self, pagina: int = 1, registros: int = DEFAULT_PAGE_SIZE) -> Dict:
        """Consulta posição de estoque."""
        return self._request("estoque/consulta", "ListarPosEstoque", {
            "nPagina": pagina, "nRegPorPagina": registros
        })
    
    def listar_todo_estoque(self) -> List[Dict]:
        """Lista todo o estoque (paginação automática)."""
        all_records = []
        page = 1
        while True:
            data = self._request("estoque/consulta", "ListarPosEstoque", {
                "nPagina": page, "nRegPorPagina": DEFAULT_PAGE_SIZE
            })
            records = data.get("produtos", [])
            all_records.extend(records)
            total_pages = data.get("nTotPaginas", 1)
            if page >= total_pages:
                break
            page += 1
            time.sleep(0.3)
        return all_records
    
    def consultar_estoque_produto(self, codigo_produto: int) -> Dict:
        """Consulta estoque de um produto específico."""
        return self._request("estoque/consulta", "ListarPosEstoque", {
            "nPagina": 1, "nRegPorPagina": 1,
            "nCodProd": codigo_produto
        })
    
    def listar_locais_estoque(self) -> List[Dict]:
        """Lista os locais de estoque."""
        data = self._request("estoque/local", "ListarLocaisEstoque", {
            "nPagina": 1, "nRegPorPagina": 500
        })
        return data.get("locaisEncontrados", [])
    
    def ajustar_estoque(self, codigo_produto: int, quantidade: float, 
                        tipo: str = "ENT", observacao: str = "") -> Dict:
        """Ajusta o estoque de um produto (ENT=entrada, SAI=saída)."""
        return self._request("estoque/ajuste", "IncluirAjusteEstoque", {
            "codigo_local_estoque": 0,
            "id_prod": codigo_produto,
            "tipo": tipo,
            "qtde": quantidade,
            "obs": observacao
        })
    
    # ==========================================
    # CLIENTES
    # ==========================================
    
    def listar_clientes(self, pagina: int = 1, registros: int = DEFAULT_PAGE_SIZE,
                        filtros: Dict = None) -> Dict:
        """Lista clientes com paginação."""
        params = {
            "pagina": pagina,
            "registros_por_pagina": registros,
            "apenas_importado_api": "N"
        }
        if filtros:
            params["clientesFiltro"] = filtros
        return self._request("geral/clientes", "ListarClientes", params)
    
    def listar_todos_clientes(self) -> List[Dict]:
        """Lista todos os clientes (paginação automática)."""
        return self._list_all("geral/clientes", "ListarClientes",
                             {"apenas_importado_api": "N"},
                             "clientes_cadastro")
    
    def consultar_cliente(self, codigo_cliente: int = None,
                          codigo_cliente_integracao: str = None) -> Dict:
        """Consulta um cliente específico."""
        params = {}
        if codigo_cliente:
            params["codigo_cliente_omie"] = codigo_cliente
        if codigo_cliente_integracao:
            params["codigo_cliente_integracao"] = codigo_cliente_integracao
        return self._request("geral/clientes", "ConsultarCliente", params)
    
    def incluir_cliente(self, cliente: Dict) -> Dict:
        """Inclui um novo cliente."""
        return self._request("geral/clientes", "IncluirCliente", cliente)
    
    def alterar_cliente(self, cliente: Dict) -> Dict:
        """Altera um cliente existente."""
        return self._request("geral/clientes", "AlterarCliente", cliente)
    
    def upsert_cliente(self, cliente: Dict) -> Dict:
        """Inclui ou altera um cliente (upsert)."""
        return self._request("geral/clientes", "UpsertCliente", cliente)
    
    # ==========================================
    # PEDIDOS DE VENDA
    # ==========================================
    
    def listar_pedidos(self, pagina: int = 1, registros: int = DEFAULT_PAGE_SIZE,
                       filtros: Dict = None) -> Dict:
        """Lista pedidos de venda com paginação."""
        params = {"pagina": pagina, "registros_por_pagina": registros}
        if filtros:
            params.update(filtros)
        return self._request("produtos/pedido", "ListarPedidos", params)
    
    def consultar_pedido(self, codigo_pedido: int = None, 
                         numero_pedido: str = None,
                         codigo_pedido_integracao: str = None) -> Dict:
        """Consulta um pedido específico."""
        params = {}
        if codigo_pedido:
            params["codigo_pedido"] = codigo_pedido
        if numero_pedido:
            params["numero_pedido"] = numero_pedido
        if codigo_pedido_integracao:
            params["codigo_pedido_integracao"] = codigo_pedido_integracao
        return self._request("produtos/pedido", "ConsultarPedido", params)
    
    def incluir_pedido(self, pedido: Dict) -> Dict:
        """Inclui um novo pedido de venda."""
        return self._request("produtos/pedido", "IncluirPedido", pedido)
    
    def alterar_pedido(self, pedido: Dict) -> Dict:
        """Altera um pedido de venda existente."""
        return self._request("produtos/pedido", "AlterarPedido", pedido)
    
    def excluir_pedido(self, codigo_pedido: int = None,
                       codigo_pedido_integracao: str = None) -> Dict:
        """Exclui um pedido de venda."""
        params = {}
        if codigo_pedido:
            params["codigo_pedido"] = codigo_pedido
        if codigo_pedido_integracao:
            params["codigo_pedido_integracao"] = codigo_pedido_integracao
        return self._request("produtos/pedido", "ExcluirPedido", params)
    
    def faturar_pedido(self, codigo_pedido: int) -> Dict:
        """Fatura um pedido de venda (gera NF-e)."""
        return self._request("produtos/pedidovendafat", "FaturarPedidoVenda", {
            "codigo_pedido": codigo_pedido
        })
    
    # ==========================================
    # FINANÇAS
    # ==========================================
    
    def listar_contas_receber(self, pagina: int = 1, registros: int = DEFAULT_PAGE_SIZE) -> Dict:
        """Lista contas a receber."""
        return self._request("financas/contareceber", "ListarContasReceber", {
            "pagina": pagina, "registros_por_pagina": registros
        })
    
    def listar_contas_pagar(self, pagina: int = 1, registros: int = DEFAULT_PAGE_SIZE) -> Dict:
        """Lista contas a pagar."""
        return self._request("financas/contapagar", "ListarContasPagar", {
            "pagina": pagina, "registros_por_pagina": registros
        })
    
    def pesquisar_titulos(self, pagina: int = 1, registros: int = DEFAULT_PAGE_SIZE) -> Dict:
        """Pesquisa títulos financeiros."""
        return self._request("financas/pesquisartitulos", "PesquisarLancamentos", {
            "nPagina": pagina, "nRegPorPagina": registros
        })
    
    def incluir_conta_receber(self, titulo: Dict) -> Dict:
        """Inclui um título a receber."""
        return self._request("financas/contareceber", "IncluirContaReceber", titulo)
    
    def incluir_conta_pagar(self, titulo: Dict) -> Dict:
        """Inclui um título a pagar."""
        return self._request("financas/contapagar", "IncluirContaPagar", titulo)
    
    # ==========================================
    # CRM
    # ==========================================
    
    def listar_contas_crm(self, pagina: int = 1, registros: int = DEFAULT_PAGE_SIZE) -> Dict:
        """Lista contas do CRM."""
        return self._request("crm/contas", "ListarContas", {
            "pagina": pagina, "registros_por_pagina": registros
        })
    
    def listar_oportunidades(self, pagina: int = 1, registros: int = DEFAULT_PAGE_SIZE) -> Dict:
        """Lista oportunidades do CRM."""
        return self._request("crm/oportunidades", "ListarOportunidades", {
            "pagina": pagina, "registros_por_pagina": registros
        })
    
    def incluir_oportunidade(self, oportunidade: Dict) -> Dict:
        """Inclui uma nova oportunidade no CRM."""
        return self._request("crm/oportunidades", "IncluirOportunidade", oportunidade)
    
    # ==========================================
    # CADASTROS AUXILIARES
    # ==========================================
    
    def listar_categorias(self) -> List[Dict]:
        """Lista todas as categorias."""
        return self._list_all("geral/categorias", "ListarCategorias",
                             {}, "categoria_cadastro")
    
    def listar_departamentos(self) -> List[Dict]:
        """Lista departamentos."""
        data = self._request("geral/departamentos", "ListarDepartamentos", {
            "pagina": 1, "registros_por_pagina": 500
        })
        return data.get("departamentos", [])
    
    def listar_projetos(self) -> List[Dict]:
        """Lista projetos."""
        data = self._request("geral/projetos", "ListarProjetos", {
            "pagina": 1, "registros_por_pagina": 500
        })
        return data.get("cadastro", [])
    
    def listar_vendedores(self) -> List[Dict]:
        """Lista vendedores."""
        data = self._request("geral/vendedores", "ListarVendedores", {
            "pagina": 1, "registros_por_pagina": 500
        })
        return data.get("cadastro", [])
    
    def listar_formas_pagamento(self) -> List[Dict]:
        """Lista formas de pagamento."""
        data = self._request("produtos/formaspagvendas", "ListarFormasPagVendas", {
            "pagina": 1, "registros_por_pagina": 500
        })
        return data.get("cadastros", [])
    
    def listar_parcelas(self) -> List[Dict]:
        """Lista parcelas disponíveis."""
        data = self._request("geral/parcelas", "ListarParcelas", {
            "pagina": 1, "registros_por_pagina": 500
        })
        return data.get("parcela_cadastro", [])
    
    # ==========================================
    # UTILITÁRIOS
    # ==========================================
    
    def testar_conexao(self) -> Dict:
        """Testa a conexão com a API Omie."""
        try:
            empresas = self.listar_empresas()
            return {
                "success": True,
                "empresa": empresas[0].get("nome_fantasia", "N/A") if empresas else "N/A",
                "cnpj": empresas[0].get("cnpj", "N/A") if empresas else "N/A"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def resumo_operacional(self) -> Dict:
        """Retorna um resumo operacional da empresa."""
        resumo = {}
        
        try:
            # Empresa
            empresas = self.listar_empresas()
            if empresas:
                resumo["empresa"] = {
                    "nome": empresas[0].get("nome_fantasia", ""),
                    "cnpj": empresas[0].get("cnpj", "")
                }
        except:
            pass
        
        try:
            # Produtos
            data = self.listar_produtos(pagina=1, registros=1)
            resumo["total_produtos"] = data.get("total_de_registros", 0)
        except:
            pass
        
        try:
            # Clientes
            data = self.listar_clientes(pagina=1, registros=1)
            resumo["total_clientes"] = data.get("total_de_registros", 0)
        except:
            pass
        
        try:
            # Pedidos
            data = self.listar_pedidos(pagina=1, registros=1)
            resumo["total_pedidos"] = data.get("total_de_registros", 0)
        except:
            pass
        
        try:
            # Estoque
            data = self.consultar_estoque(pagina=1, registros=1)
            resumo["total_itens_estoque"] = data.get("nTotRegistros", 0)
        except:
            pass
        
        try:
            # Financeiro
            data = self.listar_contas_receber(pagina=1, registros=1)
            resumo["total_contas_receber"] = data.get("total_de_registros", 0)
        except:
            pass
        
        try:
            data = self.listar_contas_pagar(pagina=1, registros=1)
            resumo["total_contas_pagar"] = data.get("total_de_registros", 0)
        except:
            pass
        
        return resumo
