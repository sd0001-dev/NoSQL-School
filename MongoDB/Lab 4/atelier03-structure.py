# atelier03-structure.py : voir, puis modifier la structure de la collection
# fournisseurs de la base logistique (atelier 3). Chaque etape de la migration ne
# touche que les documents qui en ont encore besoin : on peut relancer le programme.
# Lancement : python atelier03-structure.py
#             python atelier03-structure.py mongodb://mongo:27017   (variante Docker)
import sys

from bson import json_util
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

ADRESSE = sys.argv[1] if len(sys.argv) > 1 else "mongodb://localhost:27017"

# (nom de l'etape, filtre, modification) ; une liste [ ... ] est une chaine d'etapes
MIGRATION = [
    ("ajouter actif", {}, {"$set": {"actif": True}}),
    ("renommer tel", {}, {"$rename": {"tel": "telephone"}}),
    ("retirer fax", {}, {"$unset": {"fax": ""}}),
    ("ville dans adresse", {}, {"$rename": {"ville": "adresse.ville"}}),
    ("depuis en date", {"depuis": {"$type": "string"}},
     [{"$set": {"depuis": {"$toDate": "$depuis"}}}]),
    ("note en entier", {"note": {"$type": "string"}},
     [{"$set": {"note": {"$toInt": "$note"}}}]),
]


def inventaire(collection, titre):
    """Affiche chaque champ, son type BSON et le nombre de documents qui l'ont."""
    print(titre)
    etapes = [{"$project": {"champs": {"$objectToArray": "$$ROOT"}}},
              {"$unwind": "$champs"},
              {"$group": {"_id": {"champ": "$champs.k", "type": {"$type": "$champs.v"}},
                          "nb": {"$sum": 1}}},
              {"$sort": {"_id": 1}}]
    for ligne in collection.aggregate(etapes):
        print("  ", ligne["_id"]["champ"].ljust(10), ligne["_id"]["type"].ljust(7),
              ligne["nb"])


def migrer(db):
    fournisseurs = db["fournisseurs"]

    # 1. Creer : la collection et ses documents, seulement s'ils n'existent pas encore
    if "fournisseurs" not in db.list_collection_names():
        db.create_collection("fournisseurs")
        with open("fournisseurs.json", encoding="utf-8") as f:
            fournisseurs.insert_many(json_util.loads(f.read()))
        print("Collection creee :", fournisseurs.count_documents({}), "documents")

    # 2. Voir la structure, puis 3. la modifier, etape par etape
    inventaire(fournisseurs, "Avant :")
    for nom, filtre, modif in MIGRATION:
        r = fournisseurs.update_many(filtre, modif)
        print("  ", nom.ljust(18), r.matched_count, "trouves,", r.modified_count, "modifies")
    inventaire(fournisseurs, "Apres :")


def main():
    with MongoClient(ADRESSE, serverSelectionTimeoutMS=3000) as client:
        try:
            client.admin.command("ping")
        except ServerSelectionTimeoutError:
            sys.exit("Aucun serveur MongoDB ne repond a l'adresse " + ADRESSE)
        print("Connecte a", ADRESSE)
        migrer(client["logistique"])


main()
