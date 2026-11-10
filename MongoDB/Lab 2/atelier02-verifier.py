import sys
from pymongo import MongoClient, version

adresse = sys.argv[1] if len(sys.argv) > 1 else "mongodb://localhost:27017"
print("Adresse: ", adresse)
client = MongoClient(adresse, serverSelectionTimeoutMS=3000)
print("Ping: ", client.admin.command("ping"))
print("server version: ", client.server_info()["version"])
print("pymongo version: ", version)




messages = client["essai"]["messages"]
resultat = messages.insert_one({"text":"hello from python"})
print("Insertion, _id :", resultat.inserted_id)
print("Lecture :", messages.find_one({"_id": resultat.inserted_id}))
suppression = messages.delete_one({"_id": resultat.inserted_id})
print("Lecture :", suppression.deleted_count, "document")


client.drop_database("essai")
client.close()
print("installation ok")