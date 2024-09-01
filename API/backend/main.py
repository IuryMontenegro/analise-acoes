from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging
from monitoramento.routes import monitoramento_router
from ml.ml_route import ml_router
from monitoramento.services import scheduler

# Configurando o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

scheduler.start()
logging.info("Scheduler iniciado na inicialização do aplicativo.")

app = FastAPI()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens, você pode restringir a uma lista específica de URLs
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)

# Inclui o router de monitoramento
app.include_router(monitoramento_router)
# Inclui o router de ml
app.include_router(ml_router)

@app.get("/")
def read_root():
    return {"message": "API de Monitoramento de Ações"}
