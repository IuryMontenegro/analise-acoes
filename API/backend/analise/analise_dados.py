import numpy as np
import pandas as pd
from pymongo import MongoClient

# Configuração da conexão com o MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['acoes_db']

# Função para calcular a média móvel simples (SMA)
def calcula_sma(dados, window):
    return dados['Close'].rolling(window=window).mean()

# Função para detectar sinais de compra e venda usando a estratégia de média móvel cruzada
def estrategia_media_movel(ticker, short_window=40, long_window=100):
    # Buscar dados do MongoDB
    cursor = db.historico_acoes.find({"Ticker": ticker})
    dados = pd.DataFrame(list(cursor))
    
    # Verificar se há dados suficientes
    if dados.empty:
        print(f"Nenhum dado encontrado para {ticker}")
        return

    # Calcular as médias móveis
    dados['SMA_Short'] = calcula_sma(dados, short_window)
    dados['SMA_Long'] = calcula_sma(dados, long_window)

    # Gerar sinais de compra e venda
    dados.loc[dados.index[short_window:], 'Signal'] = np.where(
        dados['SMA_Short'][short_window:] > dados['SMA_Long'][short_window:], 1.0, 0.0
    )
    dados['Position'] = dados['Signal'].diff()

    # Exibir as oportunidades de compra/venda
    compra = dados[dados['Position'] == 1.0]
    venda = dados[dados['Position'] == -1.0]

    print(f"Sinais de Compra para {ticker}:")
    print(compra[['Date', 'Close', 'SMA_Short', 'SMA_Long']])

    print(f"\nSinais de Venda para {ticker}:")
    print(venda[['Date', 'Close', 'SMA_Short', 'SMA_Long']])

if __name__ == "__main__":
    tickers = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA']
    for ticker in tickers:
        estrategia_media_movel(ticker)