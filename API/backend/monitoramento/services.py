import logging
import pandas as pd
import yfinance as yf
from config.mongo_config import db
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def coleta_dados_acoes(tickers):
    for ticker in tickers:
        acao = yf.Ticker(ticker)
        historico = acao.history(period="5y")
        historico.reset_index(inplace=True)
        historico['Date'] = pd.to_datetime(historico['Date'])
        historico['Ticker'] = ticker

        for index, row in historico.iterrows():
            filtro = {'Date': row['Date'], 'Ticker': row['Ticker']}
            update = {'$set': row.to_dict()}
            db.historico_acoes.update_one(filtro, update, upsert=True)

        logging.info(f"Histórico de {ticker} atualizado.")

def atualizar_historico_acoes_monitoradas():
    logging.info("Iniciando a atualização do histórico das ações monitoradas.")

    try:
        acoes_monitoradas = db.acoes_monitoradas.find({}, {"codigo": 1})
        tickers = [acao["codigo"] for acao in acoes_monitoradas]

        coleta_dados_acoes(tickers)

        logging.info("Atualização do histórico concluída com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao atualizar o histórico das ações monitoradas: {e}")

# Adicionando a tarefa ao scheduler
scheduler.add_job(atualizar_historico_acoes_monitoradas, 'interval', hours=1)
