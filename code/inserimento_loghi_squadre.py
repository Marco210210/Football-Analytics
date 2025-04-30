from pymongo import MongoClient
import bson
import os

# Connessione al Database MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Soccer']
collection = db['squadre']

# Funzione per caricare e convertire l'immagine in dati binari
def carica_immagine(path):
    with open(path, 'rb') as file:
        return bson.Binary(file.read())

# Directory dove sono memorizzati i loghi delle squadre
logo_directory = 'loghi_squadre/'

# Recupera tutti i documenti dalla collezione "squadre"
squadre_cursor = collection.find()

# Aggiorna ogni documento con il logo corrispondente
for squadra in squadre_cursor:
    nome_squadra = squadra['name']
    logo_path = os.path.join(logo_directory, f"{nome_squadra}.png")
    if os.path.isfile(logo_path):
        logo_binario = carica_immagine(logo_path)
        collection.update_one(
            {"name": nome_squadra},
            {"$set": {"logo": logo_binario}}
        )
        print(f"Logo per {nome_squadra} aggiunto con successo.")
    else:
        print(f"Logo per {nome_squadra} non trovato in {logo_path}.")
