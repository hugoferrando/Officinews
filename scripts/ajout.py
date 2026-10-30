#!/usr/bin/env python3
"""Mise à jour d'articles.json pour Officinews.

Usage :
  python3 scripts/ajout.py age                  -> nombre d'heures depuis la dernière mise à jour (pour les passages de rattrapage)
  python3 scripts/ajout.py recents [jours]      -> liste id | date | titre | url des articles récents (7 jours par défaut,
                                                   élargi automatiquement si des passages ont été manqués)
  python3 scripts/ajout.py fusion nouveaux.json -> ajoute les nouveaux articles, complète les "related",
                                                   supprime les articles de plus d'un an, met à jour updatedAt

nouveaux.json contient une liste d'objets :
  - un article complet (champs id, date, rank, source, category, title, summary, url, tags,
    et optionnellement comptoir, related, approx) ;
  - ou {"id": "<id existant>", "related_add": [{"label": ..., "url": ..., "source": ...}]}
    pour rattacher une nouvelle source à un sujet déjà présent.
"""
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

FICHIER = Path(__file__).resolve().parent.parent / "articles.json"
SOURCES = {"ANSM", "HAS", "Moniteur", "Quotidien", "Autre"}
CATEGORIES = {"Ruptures & tensions", "Vaccins", "Pharmacovigilance", "Nouveaux médicaments",
              "Recommandations", "Réglementation", "Profession"}
OBLIGATOIRES = ("id", "date", "source", "category", "title", "summary", "url")
CONSERVATION_JOURS = 365


def charger():
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def enregistrer(data):
    data["articles"].sort(key=lambda a: (a["date"], -a.get("rank", 0)), reverse=True)
    FICHIER.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def recents(jours=7):
    data = charger()
    maj = data.get("updatedAt")
    # si des passages ont été manqués, élargir la fenêtre pour couvrir toute la période depuis la dernière mise à jour
    if maj:
        retard = (date.today() - date.fromisoformat(maj[:10])).days
        jours = max(jours, retard + 2)
        print(f"updatedAt: {maj} (il y a {retard} jour(s)) -> chercher les articles publiés depuis le {maj[:10]}")
    else:
        print("updatedAt: aucune")
    limite = (date.today() - timedelta(days=jours)).isoformat()
    for a in data["articles"]:
        if a["date"] >= limite:
            print(f'{a["id"]} | {a["date"]} | {a["title"]} | {a["url"]}')


def fusion(chemin):
    data = charger()
    par_id = {a["id"]: a for a in data["articles"]}
    urls = {a["url"] for a in data["articles"]} | {r["url"] for a in data["articles"] for r in a.get("related", [])}
    ajoutes, completes, ignores, sans_comptoir = 0, 0, [], []
    for n in json.loads(Path(chemin).read_text(encoding="utf-8")):
        if "related_add" in n:
            cible = par_id.get(n.get("id"))
            if not cible:
                ignores.append(f'{n.get("id")} (sujet introuvable)')
                continue
            for r in n["related_add"]:
                if r.get("url") and r["url"] not in urls:
                    cible.setdefault("related", []).append(r)
                    urls.add(r["url"])
                    completes += 1
            continue
        manque = [c for c in OBLIGATOIRES if not n.get(c)]
        if manque or n["source"] not in SOURCES or n["category"] not in CATEGORIES:
            ignores.append(f'{n.get("id")} (champ manquant ou invalide : {manque or "source/catégorie"})')
            continue
        if n["id"] in par_id or n["url"] in urls:
            ignores.append(f'{n["id"]} (déjà présent)')
            continue
        if not n.get("comptoir"):
            sans_comptoir.append(n["id"])
        n.setdefault("rank", 1)
        data["articles"].append(n)
        par_id[n["id"]] = n
        urls.add(n["url"])
        ajoutes += 1
    limite = (date.today() - timedelta(days=CONSERVATION_JOURS)).isoformat()
    avant = len(data["articles"])
    data["articles"] = [a for a in data["articles"] if a["date"] >= limite]
    paris = timezone(timedelta(hours=1))
    data["updatedAt"] = datetime.now(paris).isoformat(timespec="seconds")
    enregistrer(data)
    print(f"{ajoutes} ajouté(s), {completes} source(s) rattachée(s), {avant - len(data['articles'])} ancien(s) supprimé(s)")
    for i in ignores:
        print("ignoré :", i)
    for i in sans_comptoir:
        print("attention, sans encadré « Au comptoir » :", i)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "age":
        maj = charger().get("updatedAt")
        if not maj:
            print(999)
        else:
            print(int((datetime.now(timezone.utc) - datetime.fromisoformat(maj)).total_seconds() // 3600))
    elif len(sys.argv) >= 2 and sys.argv[1] == "recents":
        recents(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    elif len(sys.argv) == 3 and sys.argv[1] == "fusion":
        fusion(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
