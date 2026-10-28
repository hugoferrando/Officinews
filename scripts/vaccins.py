#!/usr/bin/env python3
"""Mise à jour de vaccins.json (onglet Vaccins d'Officinews).

Usage :
  python3 scripts/vaccins.py voir             -> résumé court des campagnes et recommandations enregistrées
  python3 scripts/vaccins.py maj patch.json   -> applique un correctif

patch.json :
  {
    "campagnes": [ {"id": "grippe", "fin": "2027-02-28"},              # met à jour les champs fournis d'une campagne existante
                   {"id": "zona", "nom": "...", "debut": "...", ...} ],  # ou crée une nouvelle campagne (nom et debut obligatoires)
    "recos": [ {"date": "YYYY-MM-DD", "titre": "...", "texte": "...", "source": "https://..."} ],
    "retirer": ["id-de-campagne"]                                       # optionnel : supprime des campagnes
  }
Champs d'une campagne : id, nom, debut (YYYY-MM-DD), fin (YYYY-MM-DD ou null), pourQui, produits, officine, source,
liens (optionnel, [{label, url}] vers ameli, Meddispar, etc.).
Les recommandations sont dédoublonnées par source et seules les 5 plus récentes sont gardées.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

FICHIER = Path(__file__).resolve().parent.parent / "vaccins.json"
CHAMPS = ("id", "nom", "debut", "fin", "pourQui", "produits", "officine", "source", "liens")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def charger():
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def voir():
    d = charger()
    print("updatedAt:", d.get("updatedAt"))
    for c in d["campagnes"]:
        print(f'- {c["id"]} | {c["nom"]} | {c["debut"]} → {c.get("fin") or "?"}')
    for r in d.get("recos", []):
        print(f'* reco {r["date"]} | {r["titre"]}')


def maj(chemin):
    d = charger()
    patch = json.loads(Path(chemin).read_text(encoding="utf-8"))
    par_id = {c["id"]: c for c in d["campagnes"]}
    msgs = []
    for c in patch.get("campagnes", []):
        c = {k: v for k, v in c.items() if k in CHAMPS}
        for k in ("debut", "fin"):
            if c.get(k) and not DATE.fullmatch(c[k]):
                msgs.append(f'ignoré : date invalide {c[k]!r} pour {c.get("id")}')
                c.pop(k)
        if not c.get("id"):
            msgs.append("ignoré : campagne sans id")
        elif c["id"] in par_id:
            par_id[c["id"]].update(c)
            msgs.append(f'campagne mise à jour : {c["id"]}')
        elif c.get("nom") and c.get("debut"):
            c.setdefault("fin", None)
            d["campagnes"].append(c)
            par_id[c["id"]] = c
            msgs.append(f'campagne ajoutée : {c["id"]}')
        else:
            msgs.append(f'ignoré : nouvelle campagne {c["id"]} sans nom ou date de début')
    for cid in patch.get("retirer", []):
        if cid in par_id:
            d["campagnes"] = [c for c in d["campagnes"] if c["id"] != cid]
            msgs.append(f"campagne retirée : {cid}")
    recos = d.setdefault("recos", [])
    sources = {r.get("source") for r in recos}
    for r in patch.get("recos", []):
        if all(r.get(k) for k in ("date", "titre", "texte", "source")) and DATE.fullmatch(r["date"]) and r["source"] not in sources:
            recos.append(r)
            sources.add(r["source"])
            msgs.append(f'reco ajoutée : {r["titre"]}')
    recos.sort(key=lambda r: r["date"], reverse=True)
    d["recos"] = recos[:5]
    d["campagnes"].sort(key=lambda c: c["debut"])
    d["updatedAt"] = date.today().isoformat()
    FICHIER.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(msgs) or "aucun changement")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "voir":
        voir()
    elif len(sys.argv) == 3 and sys.argv[1] == "maj":
        maj(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
