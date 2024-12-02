# -*- coding: utf-8 -*-

"""
Script para buscar dados e criar gráficos.

Este script busca dados de recebimentos semanais e diários,
e cria gráficos de colunas para visualizar os dados.

Autor: [Seu Nome]
Data: [Data de Criação]
"""

import plotly.express as px
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Dados de login
USUARIO = "guilhermealves"
SENHA = "88412594"

# URL da página
URL_LOGIN = "https://smartnet.sgp.tsmx.com.br/accounts/login/"
URL_BUSCA = "https://smartnet.sgp.tsmx.com.br/admin/financeiro/relatorios/titulo/recebidos/"

def buscar_dados(datas_busca):
    """
    Busca dados de recebimentos.

    Args:
        datas_busca (list): Lista de dicionários com as datas de início e fim.

    Returns:
        list: Lista de valores recebidos.
    """
    valores = []
    for dados_busca in datas_busca:
        # Fazer login
        response = requests.post(URL_LOGIN, data={"username": USUARIO, "password": SENHA}, timeout=10)

        # Verificar se o login foi bem-sucedido
        if response.status_code == 200:
            # Fazer busca
            response_busca = requests.get(URL_BUSCA, params={
                "reqtime": "20241128230720",
                "dpb_token": "df7e1ed519839fc00bbcbdfc5224db66",
                "razaosocial": "",
                "tipo_cliente": "",
                "portador": "",
                "gateway_pagamento": "",
                "grupo": "",
                "nas": "",
                "torre": "",
                "data_ini": dados_busca["ini"],
                "data_fim": dados_busca["fim"],
                "data_venc_ini": "",
                "data_venc_fim": "",
                "data_cad_contrato_ini": "",
                "data_cad_contrato_fim": "",
                "usuario": "",
                "com_api": "",
                "com_pix": "",
                "id_remessa": "",
                "id_remessagateway": "",
                "com_remessa": "",
                "valor": "",
                "status_contrato": "",
                "vendedor": "",
                "titulos_nota": "",
                "titulos_nfse": "",
                "tipo_data": "pagamento",
                "pontorecebimento": "",
                "modobaixa": "",
                "retornobanco": "",
                "printpdf": "",
                "printexcel": "",
                "page": "",
                "data_p_ini": dados_busca["ini"],
                "data_p_fim": dados_busca["fim"]
            }, cookies=response.cookies, timeout=10)

            # Verificar se a busca foi bem-sucedida
            if response_busca.status_code == 200:
                # Extrair os dados da tabela
                soup = BeautifulSoup(response_busca.content, "html.parser")
                tabela = soup.find("table")

                # Verificar se a tabela foi encontrada
                if tabela is not None:
                    dados = []
                    for linha in tabela.find_all("tr"):
                        cols = linha.find_all("td")
                        if len(cols) > 0:
                            dados.append([col.text.strip() for col in cols])

                    # Criar um DataFrame com os dados
                    df = pd.DataFrame(dados)

                    # Verificar se o DataFrame tem dados
                    if not df.empty:
                        # Verificar se o DataFrame tem as colunas necessárias
                        if len(df.columns) >= 8:
                            # Criar um novo DataFrame com apenas as colunas necessárias
                            colunas = df.columns
                            df_novo = df.iloc[:, [0, 7]]  # Pegar a coluna 0 (cliente) e 7 (valor pago)

                            # Resetar o índice do DataFrame
                            df_novo = df_novo.reset_index(drop=True)

                            # Renumerar o índice do DataFrame
                            df_novo.index += 1

                            # Somar os valores pagos
                            soma_valores_pagos = 0
                            for index, row in df_novo.iterrows():
                                valor_pago = row.iloc[1].replace('.', '', 1).replace(',', '.', 1)
                                if valor_pago.replace('.', '', 1).isdigit():
                                    soma_valores_pagos += float(valor_pago)

                            valores.append(soma_valores_pagos)
                        else:
                            valores.append(0)
                    else:
                        valores.append(0)
                else:
                    valores.append(0)
            else:
                valores.append(0)
        else:
            valores.append(0)
    return valores

def criar_grafico_semanal(valores_atual):
    """
    Cria um gráfico de colunas para os dados semanais.

    Args:
        valores_atual (list): Lista de valores recebidos.
    """
    # Criar um DataFrame com os dados do mês atual
    df_atual = pd.DataFrame({
        "semana": [f"Semana {i+1}" for i in range(len(valores_atual))],
        "valor": valores_atual
    })

    # Criar um gráfico de colunas
    fig_semanal = px.bar(x=df_atual["semana"], y=df_atual["valor"], title="Gráfico de Colunas Semanais", color_discrete_sequence=["red", "blue", "green", "yellow"])

    # Mostrar o gráfico semanal
    fig_semanal.show()

def criar_grafico_diario(valores_diarios):
    """
    Cria um gráfico de barras com linha para os dados diários.

    Args:
        valores_diarios (list): Lista de valores recebidos.
    """
    # Criar um DataFrame com os dados diários
    df_diarios = pd.DataFrame({
        "dia": [f"Dia {i+1}" for i in range(len(valores_diarios))],
        "valor": valores_diarios
    })

    # Criar um gráfico de barras com linha
    fig_diario = px.bar(df_diarios, x="dia", y="valor", title="Gráfico de Barras Diário", text_auto=True, color_discrete_sequence=["green"])

    # Adicionar linha que conecta os picos
    fig_diario.add_scatter(x=df_diarios["dia"], y=df_diarios["valor"], mode="lines", line=dict(color="blue", width=3, dash="solid"))

    # Mostrar o gráfico diário
    fig_diario.show()

def main():
    # Dados da busca
    agora = datetime.now()
    mes_atual = agora.month
    ano_atual = agora.year

    datas_busca_atual = [
        {"ini": f"01/{mes_atual:02}/{ano_atual}", "fim": f"07/{mes_atual:02}/{ano_atual}", "titulo": "Semana 1"},
        {"ini": f"08/{mes_atual:02}/{ano_atual}", "fim": f"14/{mes_atual:02}/{ano_atual}", "titulo": "Semana 2"},
        {"ini": f"15/{mes_atual:02}/{ano_atual}", "fim": f"21/{mes_atual:02}/{ano_atual}", "titulo": "Semana 3"},
        {"ini": f"22/{mes_atual:02}/{ano_atual}", "fim": f"{agora.day:02}/{mes_atual:02}/{ano_atual}", "titulo": "Semana 4"}
    ]

    valores_atual = buscar_dados(datas_busca_atual)

    criar_grafico_semanal(valores_atual)

    # Criar um loop para iterar sobre cada dia do mês
    dias_mes = []
    valores_diarios = []
    for dia in range(1, agora.day + 1):
        data_ini = f"{dia:02}/{mes_atual:02}/{ano_atual}"
        data_fim = f"{dia:02}/{mes_atual:02}/{ano_atual}"
        valor_diario = buscar_dados([{"ini": data_ini, "fim": data_fim}])[0]
        dias_mes.append(data_ini)
        valores_diarios.append(valor_diario)

    criar_grafico_diario(valores_diarios)

if __name__ == "__main__":
    main()
