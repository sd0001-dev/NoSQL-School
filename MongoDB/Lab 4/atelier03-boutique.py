# atelier03-boutique.py : un petit programme qui lit et ecrit dans la base boutique
# (atelier 3, partie 3). Il reapprovisionne les produits en rupture de stock et
# note chaque reapprovisionnement dans la collection journal.
# Lancement : python atelier03-boutique.py
#             python atelier03-boutique.py mongodb://mongo:27017   (variante Docker)
import sys
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

ADRESSE = sys.argv[1] if len(sys.argv) > 1 else "mongodb://localhost:27017"
AJOUT = 20  # exemplaires ajoutes a chaque produit en rupture


def valeur_du_stock(produits):
    """Somme de prix x stock sur tous les produits, en nombre decimal exact."""
    total = 0
    for p in produits.find({}, {"_id": 0, "prix": 1, "stock": 1}):
        total += p["prix"].to_decimal() * p["stock"]
    return total


def reapprovisionner(db):
    produits = db["produits"]
    print("Produits :", produits.count_documents({}))

    # 1. Lire : les produits en rupture de stock, tries par reference
    curseur = produits.find({"stock": 0}, {"_id": 0, "ref": 1, "libelle": 1})
    rupture = list(curseur.sort("ref", 1))
    print("En rupture de stock :", len(rupture))
    for p in rupture:
        print("  ", p["ref"], p["libelle"])
    print("Valeur du stock :", valeur_du_stock(produits), "DH")
    if not rupture:
        print("Rien a reapprovisionner.")
        return

    # 2. Ecrire : AJOUT exemplaires de plus pour chacun, puis une trace dans le journal
    refs = [p["ref"] for p in rupture]
    maintenant = datetime.now(timezone.utc)
    r = produits.update_many({"ref": {"$in": refs}, "stock": 0},
                             {"$inc": {"stock": AJOUT},
                              "$set": {"reappro_le": maintenant}})
    print("Mise a jour :", r.matched_count, "trouves,", r.modified_count, "modifies")
    r = db["journal"].insert_one({"action": "reappro", "refs": refs,
                                  "ajout": AJOUT, "le": maintenant})
    print("Journal : document", r.inserted_id)

    # 3. Relire pour verifier
    for p in produits.find({"ref": {"$in": refs}}, {"_id": 0, "ref": 1, "stock": 1}):
        print("  ", p["ref"], "stock", p["stock"])
    print("Valeur du stock :", valeur_du_stock(produits), "DH")


def main():
    with MongoClient(ADRESSE, serverSelectionTimeoutMS=3000) as client:
        try:
            client.admin.command("ping")
        except ServerSelectionTimeoutError:
            sys.exit("Aucun serveur MongoDB ne repond a l'adresse " + ADRESSE)
        print("Connecte a", ADRESSE)
        reapprovisionner(client["boutique"])


main()
