from pymongo import MongoClient

# Configuração da conexão com o MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['acoes_db']