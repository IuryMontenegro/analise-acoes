from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .services import coleta_dados_acoes, atualizar_historico_acoes_monitoradas
from config.mongo_config import db

monitoramento_router = APIRouter()

class AcaoRequest(BaseModel):
    codigo_acao: str

@monitoramento_router.post("/adicionar_acao/")
def adicionar_acao(request: AcaoRequest):
    codigo_acao = request.codigo_acao
    
    if db.acoes_monitoradas.find_one({"codigo": codigo_acao}):
        raise HTTPException(status_code=400, detail="Ação já está sendo monitorada")

    acao = yf.Ticker(codigo_acao)
    info = acao.info

    if not info.get('longName'):
        raise HTTPException(status_code=404, detail="Ação não encontrada ou inválida no yfinance")

    info["codigo"] = codigo_acao
    db.acoes_monitoradas.insert_one(info)

    logging.info(f"Ação {codigo_acao} adicionada ao monitoramento.")

    coleta_dados_acoes([codigo_acao])

    return {"message": f"Ação {codigo_acao} adicionada com sucesso"}

@monitoramento_router.get("/acao/{codigo_acao}/info")
def obter_info_acao(codigo_acao: str):
    info = db.acoes_monitoradas.find_one({"codigo": codigo_acao}, {"_id": 0})
    
    if not info:
        raise HTTPException(status_code=404, detail="Ação não encontrada")

    return JSONResponse(content=info, media_type="application/json; charset=utf-8")

@monitoramento_router.get("/acao/{codigo_acao}/historico")
def obter_historico_acao(codigo_acao: str, periodo: str = Query("1m")):
    if periodo not in ["1w", "1m", "1y", "max"]:
        raise HTTPException(status_code=400, detail="Período inválido")

    # Define os limites de data com base no período
    if periodo == "1w":
        start_date = datetime.now() - timedelta(weeks=1)
    elif periodo == "1m":
        start_date = datetime.now() - timedelta(days=30)
    elif periodo == "1y":
        start_date = datetime.now() - timedelta(days=365)
    else:  # "max"
        start_date = datetime.min

    # Recupera o histórico de preços da ação dentro do período
    historico = db.historico_acoes.find(
        {"Ticker": codigo_acao, "Date": {"$gte": start_date}},
        {"_id": 0}
    ).sort("Date", 1)

    # Converte o histórico para uma lista e formata as datas
    historico_formatado = []
    for registro in historico:
        registro['Date'] = registro['Date'].strftime('%Y-%m-%d %H:%M:%S')
        historico_formatado.append(registro)

    return JSONResponse(content={"historico": historico_formatado})

@monitoramento_router.get("/acoes/")
def listar_acoes():
    acoes = list(db.acoes_monitoradas.find({}, {"_id": 0, "codigo": 1, "longName": 1, "currentPrice": 1}))
    return JSONResponse(content={"acoes": acoes}, media_type="application/json; charset=utf-8")
