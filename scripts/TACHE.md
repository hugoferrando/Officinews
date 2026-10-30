# Mise à jour automatique d'Officinews

Instructions suivies par la tâche programmée « Mise à jour Officinews ». Travaille seul, sans poser de question, et de façon ÉCONOME : le moins d'appels d'outils et de texte possible. Ne lis jamais articles.json ni dispo.json en entier.

## 1. Se placer dans le dépôt
Le dépôt hugoferrando/Officinews est attaché à la tâche et déjà cloné : place-toi dans le dossier qui contient `scripts/ajout.py` (`ls -d */ ~/*/ 2>/dev/null` si besoin). Toutes les commandes suivantes s'exécutent dans ce dossier.

## 2. Passage de rattrapage ?
Si l'heure de Paris est vers 9 h 37, 16 h 37 ou 21 h 37 (passages de rattrapage éventuels) : `python3 scripts/ajout.py age`. Si le résultat est inférieur à 4, arrête-toi et réponds « À jour ». Sinon (ou à tout autre horaire), continue.

## 3. Articles
1. `python3 scripts/ajout.py recents 7` : date de dernière mise à jour + articles récents (id | date | titre | url), période élargie automatiquement si des passages ont été manqués. Sert à éviter les doublons.
2. UN WebFetch par page, en demandant uniquement « titre, date, URL et une phrase de résumé des articles publiés depuis <date de dernière mise à jour> » :
   - https://ansm.sante.fr/actualites/a-la-une
   - https://www.has-sante.fr/jcms/c_476564
   - https://www.lequotidiendupharmacien.fr/tous-les-articles
   - https://www.lemoniteurdespharmacies.fr/therapeutique/medicaments/
   N'ouvre pas les articles un par un. WebSearch seulement si une page ne répond pas (une seule recherche).
   Garde uniquement : médicaments, vaccins, ruptures/tensions, pharmacovigilance, recos HAS, substitution/biosimilaires, réglementation officinale, grands sujets de la profession.
3. Écris `/tmp/nouveaux.json` : une liste JSON, un objet par nouveau sujet :
   - `id` : slug court sans accents (lettres, chiffres, tirets)
   - `date` "YYYY-MM-DD" ; `rank` (entier, 1 = plus important du jour)
   - `source` : "ANSM" | "HAS" | "Moniteur" | "Quotidien" | "Autre" (la plus officielle si plusieurs)
   - `category` : une de "Ruptures & tensions", "Vaccins", "Pharmacovigilance", "Nouveaux médicaments", "Recommandations", "Réglementation", "Profession"
   - `title` (titre d'origine) ; `summary` : 1 à 2 phrases avec TES PROPRES MOTS (jamais de phrase copiée)
   - `comptoir` (OBLIGATOIRE pour chaque article, affiché dans l'encadré « Au comptoir ») : une phrase courte et pratique pour l'équipe officinale (quoi vérifier, dire au patient, commander, à qui orienter). Sans conduite à tenir concrète, dire ce que ça change ou non pour l'officine (ex. « Rien ne change pour l'instant : … »). N'invente aucune posologie ni date absente de la source.
   - `url` ; `related` (optionnel) [{label, url, source}] ; `tags` (3 à 5 mots-clés) ; `approx`: true si la date est estimée
   Pour une autre source sur un sujet déjà listé : {"id": "<id existant>", "related_add": [{label, url, source}]}.
4. `python3 scripts/ajout.py fusion /tmp/nouveaux.json` (liste vide [] s'il n'y a rien de nouveau, pour mettre quand même à jour la date).

## 4. Vaccins — seulement si un nouvel article ANSM ou HAS annonce le début, la fin ou la prolongation d'une campagne de vaccination, un changement de publics ou de produits, ou une nouvelle recommandation vaccinale
`python3 scripts/vaccins.py voir`, puis écris `/tmp/vaccins-patch.json` au format décrit en tête de `scripts/vaccins.py` (seulement les champs qui changent ; textes courts avec tes propres mots ; dates "YYYY-MM-DD" ; source = URL ANSM ou HAS ; n'invente aucune date, ouvre l'article une seule fois si besoin), puis `python3 scripts/vaccins.py maj /tmp/vaccins-patch.json`. Sinon, ne touche pas à vaccins.json.

## 5. Ruptures ANSM — une fois par jour
`python3 scripts/dispo.py afaire` : si « non », saute cette étape. Si « oui » : `python3 scripts/dispo.py derniere` → date D, puis UN WebFetch de https://ansm.sante.fr/disponibilites-des-produits-de-sante/medicaments en demandant : « Liste uniquement les lignes du tableau dont la date de Mise à jour est postérieure ou égale au <D en JJ/MM/AAAA>, au format strict une ligne par entrée : Statut | Mise à jour | Spécialité | Remise à disposition | Domaines médicaux. Mets - si une colonne est vide. Spécialité raccourcie au nom, dosage et forme, sans la liste des substances entre crochets. » Le 1er du mois : demande TOUTES les lignes. Écris la réponse (lignes seules) dans `/tmp/dispo.txt` puis `python3 scripts/dispo.py fusion /tmp/dispo.txt` (ou `complet` le 1er du mois).

## 6. Envoi — directement sur la branche main (publiée par GitHub Pages ; pas de branche claude/ ni de pull request)
`git add articles.json dispo.json vaccins.json && git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "Mise à jour <date et heure>" && git fetch origin main && git rebase origin/main && git push origin HEAD:main`

Réponse finale : une seule ligne (sorties des scripts, ou « À jour »).
