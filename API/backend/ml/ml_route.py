from fastapi import APIRouter, HTTPException
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
from config.mongo_config import db

ml_router = APIRouter()

@ml_router.get("/acao/{codigo_acao}/prever_preco")
def prever_preco(codigo_acao: str):
    # Pegar histórico de preços
    historico = list(db.historico_acoes.find({"Ticker": codigo_acao}, {"_id": 0}))
    if not historico:
        raise HTTPException(status_code=404, detail="Histórico não encontrado")

    df = pd.DataFrame(historico)
    df['Date'] = pd.to_datetime(df['Date'])

    # Adiciona variáveis baseadas em datas
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day

    # Features: Adiciona médias móveis e o próprio preço anterior como features
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['Previous_Close'] = df['Close'].shift(1)

    # Drop linhas com valores NaN
    df.dropna(inplace=True)

    X = df[['Year', 'Month', 'Day', 'SMA_5', 'SMA_10', 'Previous_Close']]
    y = df['Close']

    # Divide o dataset em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Treina o modelo
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Prever o preço para o próximo dia
    X_next = np.array([[df.iloc[-1]['Year'], df.iloc[-1]['Month'], df.iloc[-1]['Day'] + 1,
                        df.iloc[-1]['SMA_5'], df.iloc[-1]['SMA_10'], df.iloc[-1]['Close']]])
    predicted_price = model.predict(X_next)[0]

    return {"preco_previsto": predicted_price}
