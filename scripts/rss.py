#!/usr/bin/env python3
"""Lit un flux RSS et affiche les articles publiés depuis une date (moins de tokens qu'un WebFetch).

Usage :
  python3 scripts/rss.py <url du flux> <AAAA-MM-JJ>
  -> une ligne par article : date | titre | url | début de la description
  -> « indisponible : … » si le flux ne répond pas (passer alors à la suite).
"""
import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    url, depuis = sys.argv[1], sys.argv[2]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Officinews)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            racine = ET.fromstring(r.read())
    except Exception as e:  # réseau, blocage, XML invalide
        print(f"indisponible : {e}")
        return
    n = 0
    for item in racine.iter("item"):
        try:
            d = parsedate_to_datetime(item.findtext("pubDate", "")).date().isoformat()
        except Exception:
            d = "?"
        if d != "?" and d < depuis:
            continue
        titre = html.unescape(item.findtext("title", "").strip())
        lien = item.findtext("link", "").strip()
        desc = html.unescape(re.sub(r"<[^>]+>", " ", item.findtext("description", "")))
        desc = re.sub(r"\s+", " ", desc).strip()[:220]
        print(f"{d} | {titre} | {lien} | {desc}")
        n += 1
    if not n:
        print(f"aucun article depuis le {depuis}")


if __name__ == "__main__":
    main()
