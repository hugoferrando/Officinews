#!/usr/bin/env python3
"""Mise à jour de dispo.json (liste ANSM « Disponibilité des produits de santé – médicaments »).

Source : https://ansm.sante.fr/disponibilites-des-produits-de-sante/medicaments

Usage :
  python3 scripts/dispo.py derniere              -> date de mise à jour la plus récente déjà enregistrée
  python3 scripts/dispo.py fusion lignes.txt     -> ajoute ou met à jour les produits listés (mise à jour quotidienne)
  python3 scripts/dispo.py complet lignes.txt    -> remplace toute la liste (resynchronisation complète)

Format de lignes.txt, une ligne par produit, tel que le tableau ANSM :
  Statut | JJ/MM/AAAA (mise à jour) | Spécialité | JJ/MM/AAAA ou - (remise à disposition) | Domaine, Domaine
"""
import json
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

FICHIER = Path(__file__).resolve().parent.parent / "dispo.json"
SOURCE = "https://ansm.sante.fr/disponibilites-des-produits-de-sante/medicaments"
STATUTS = {"Rupture de stock", "Tension d'approvisionnement", "Remise à disposition", "Arrêt de commercialisation"}
# les remises à disposition et arrêts de commercialisation ne restent affichés que 90 jours
CONSERVATION_RESOLUS = 90


def cle(nom):
    n = unicodedata.normalize("NFKD", nom.lower())
    n = "".join(c for c in n if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", n).strip()


def date_iso(s):
    s = (s or "").strip()
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def lire_lignes(chemin):
    items, rejets = [], []
    for brut in Path(chemin).read_text(encoding="utf-8").splitlines():
        if not brut.strip():
            continue
        parts = [p.strip() for p in brut.split("|")]
        if len(parts) != 5 or parts[0] not in STATUTS or not date_iso(parts[1]) or not parts[2]:
            rejets.append(brut)
            continue
        items.append({
            "statut": parts[0],
            "maj": date_iso(parts[1]),
            "nom": parts[2],
            "remise": date_iso(parts[3]),
            "domaines": [d.strip() for d in parts[4].split(",") if d.strip() and d.strip() != "-"],
        })
    return items, rejets


def charger():
    if FICHIER.exists():
        return json.loads(FICHIER.read_text(encoding="utf-8"))
    return {"updatedAt": None, "source": SOURCE, "items": []}


def enregistrer(data):
    limite = (date.today() - timedelta(days=CONSERVATION_RESOLUS)).isoformat()
    data["items"] = [i for i in data["items"]
                     if i["statut"] in ("Rupture de stock", "Tension d'approvisionnement") or i["maj"] >= limite]
    data["items"].sort(key=lambda i: (i["maj"], i["nom"]), reverse=True)
    data["source"] = SOURCE
    data["updatedAt"] = datetime.now(timezone(timedelta(hours=1))).isoformat(timespec="seconds")
    FICHIER.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "derniere":
        items = charger()["items"]
        print(max((i["maj"] for i in items), default="aucune"))
        return
    if len(sys.argv) != 3 or sys.argv[1] not in ("fusion", "complet"):
        print(__doc__)
        sys.exit(1)
    nouveaux, rejets = lire_lignes(sys.argv[2])
    data = charger()
    if sys.argv[1] == "complet":
        data["items"] = nouveaux
        ajoutes, modifies = len(nouveaux), 0
    else:
        par_cle = {cle(i["nom"]): i for i in data["items"]}
        ajoutes = modifies = 0
        for n in nouveaux:
            k = cle(n["nom"])
            ancien = par_cle.get(k)
            if ancien is None:
                data["items"].append(n)
                par_cle[k] = n
                ajoutes += 1
            elif n["maj"] >= ancien["maj"] and n != ancien:
                ancien.update(n)
                modifies += 1
    enregistrer(data)
    print(f"{ajoutes} ajouté(s), {modifies} mis à jour, {len(data['items'])} produit(s) affiché(s)")
    for r in rejets:
        print("ligne ignorée :", r)


if __name__ == "__main__":
    main()
