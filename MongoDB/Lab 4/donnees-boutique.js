// =================================================================
//  Données des ateliers MongoDB : base « boutique »
//  200 produits et 1 000 commandes, toujours les mêmes (aucun tirage au hasard).
//  Relancer le script remet la base dans son état de départ : il supprime toute
//  la base, y compris commandes_volume (atelier 4, à recharger avec
//  donnees-volume.js) et les fichiers rangés à l'atelier 3 (partie 3).
//
//  Installation native :  mongosh --file donnees-boutique.js
//  Docker :               docker cp donnees-boutique.js mongo:/tmp/
//                         docker exec -it mongo mongosh --file /tmp/donnees-boutique.js
// =================================================================
(function () {
  const base = db.getSiblingDB("boutique");
  base.dropDatabase();

  const categories = ["Informatique", "Téléphonie", "Maison", "Livres", "Sport"];
  const villes = ["Rabat", "Casablanca", "Fès", "Tanger", "Marrakech"];
  const unJour = 24 * 60 * 60 * 1000;

  // --- 200 produits : P-001 à P-200 --------------------------------
  const produits = [];
  for (let i = 1; i <= 200; i++) {
    const tags = [];
    if (i % 3 === 0) tags.push("promo");
    if (i % 4 === 0) tags.push("nouveau");
    produits.push({
      ref: "P-" + String(i).padStart(3, "0"),
      libelle: categories[i % 5] + " n°" + i,
      categorie: categories[i % 5],
      prix: Decimal128(String(10 + (i * 37) % 500) + ".00"),
      stock: (i * 13) % 50,
      tags: tags,
      ajoute_le: new Date(Date.UTC(2025, 0, 1) + i * unJour)
    });
  }
  base.produits.insertMany(produits);

  // --- 1 000 commandes : 10001 à 11000 ------------------------------
  const commandes = [];
  for (let j = 1; j <= 1000; j++) {
    const c = 1 + (j * 7) % 100;
    const lignes = [];
    for (let k = 0; k < 1 + (j % 3); k++) {
      const p = produits[(j * 11 + k * 17) % 200];
      lignes.push({ ref: p.ref, libelle: p.libelle, prix: p.prix, qte: 1 + (j + k) % 4 });
    }
    commandes.push({
      _id: 10000 + j,
      client: { id: c, nom: "Client " + c, ville: villes[c % 5] },
      date: new Date(Date.UTC(2026, 0, 1) + (j % 270) * unJour),
      statut: j % 10 === 0 ? "annulée" : "payée",
      lignes: lignes
    });
  }
  base.commandes.insertMany(commandes);

  print("Base boutique chargée : " + base.produits.countDocuments() + " produits, "
        + base.commandes.countDocuments() + " commandes.");
})();
