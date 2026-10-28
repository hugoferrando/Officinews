# Officinews

Journal de veille pharmaceutique personnel de Hugo (étudiant en 6e année de pharmacie, filière officine, Montpellier). Agrège les actualités ANSM, HAS, Le Moniteur des pharmacies et Le Quotidien du pharmacien : médicaments, vaccins, ruptures, pharmacovigilance, recos, réglementation, profession. Répondre en français.

Site public : https://hugoferrando.github.io/Officinews/ (GitHub Pages, branche `main`, racine du dépôt).

## Structure

| Fichier | Rôle |
|---|---|
| `index.html` | Toute la page : HTML, CSS et JS dans un seul fichier, sans dépendance ni build. Charge `articles.json` au chargement. |
| `articles.json` | `{ "updatedAt": "<ISO Europe/Paris>", "articles": [...] }`. Seul fichier modifié par les mises à jour automatiques. |
| `scripts/ajout.py` | `recents [jours]` liste les articles récents ; `fusion fichier.json` ajoute sans doublon, purge > 120 jours, met à jour `updatedAt`. |
| `manifest.webmanifest`, `icon.svg`, `icon-*.png` | Installation sur l'écran d'accueil (PWA légère, sans service worker). |
| `.nojekyll` | GitHub Pages sert les fichiers tels quels. |

## Format d'un article

Champs obligatoires : `id` (slug sans accents), `date` (`YYYY-MM-DD`), `source`, `category`, `title`, `summary`, `url`.
Optionnels : `rank` (ordre dans la journée, 1 = plus important), `comptoir` (conduite à tenir pratique), `related` (`[{label, url, source}]`), `tags`, `approx` (date estimée).

- `source` : `ANSM`, `HAS`, `Moniteur`, `Quotidien`, `Autre`
- `category` : `Ruptures & tensions`, `Vaccins`, `Pharmacovigilance`, `Nouveaux médicaments`, `Recommandations`, `Réglementation`, `Profession`

Ajouter une source ou une catégorie demande de modifier à la fois `index.html` (listes `SOURCES`/`CATS`, couleurs `--s-*`) et `scripts/ajout.py` (`SOURCES`/`CATEGORIES`).

## Règles de contenu

- Résumés rédigés avec nos propres mots, jamais de phrases copiées des articles (les sources sont sous droit d'auteur, le site est public).
- Chaque article renvoie vers sa source d'origine.

## Mises à jour automatiques

Une tâche programmée Claude (« Mise à jour Officinews », modèle Sonnet) tourne à 6 h 37, 13 h 37 et 18 h 37 (heure de Paris). Elle clone ce dépôt, lit les pages d'actus des quatre sources, écrit les nouveautés dans un fichier temporaire, lance `scripts/ajout.py fusion`, puis commit et push `articles.json`. Hugo veut une consommation de tokens minimale : ne pas alourdir ce flux.

## Conventions de la page

- Thèmes clair et sombre via des tokens CSS sur `:root` ; toute nouvelle couleur passe par un token défini dans les deux thèmes.
- Doit rester lisible à 390 px de large sans défilement horizontal (les filtres défilent à l'horizontale sur mobile).
- Polices Google Fonts : Newsreader (titres), Public Sans (texte), IBM Plex Mono (dates, étiquettes).
- Le statut « lu » est stocké dans le `localStorage` du navigateur (clé `veille-read`).
- Après une modification de `index.html`, vérifier que le script se parse et que la page charge les articles sans erreur avant de pousser.
