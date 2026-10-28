# Officinews

Journal de veille pharmaceutique personnel de Hugo (étudiant en 6e année de pharmacie, filière officine, Montpellier). Agrège les actualités ANSM, HAS, Le Moniteur des pharmacies et Le Quotidien du pharmacien : médicaments, vaccins, ruptures, pharmacovigilance, recos, réglementation, profession. Répondre en français.

Site public : https://hugoferrando.github.io/Officinews/ (GitHub Pages, branche `main`, racine du dépôt).

## Structure

| Fichier | Rôle |
|---|---|
| `index.html` | Toute la page : HTML, CSS et JS dans un seul fichier, sans dépendance ni build. Charge `articles.json` au chargement. |
| `articles.json` | `{ "updatedAt": "<ISO Europe/Paris>", "articles": [...] }`. Seul fichier modifié par les mises à jour automatiques. |
| `dispo.json` | `{ "updatedAt", "source", "items": [{statut, maj, nom, remise, domaines}] }` : liste ANSM « Disponibilité des produits de santé – médicaments », affichée dans l'onglet Disponibilités. |
| `scripts/dispo.py` | `derniere` donne la date de mise à jour la plus récente ; `fusion lignes.txt` ajoute ou met à jour les produits ; `complet lignes.txt` remplace toute la liste. Les remises à disposition et arrêts de plus de 90 jours sont retirés. |
| `scripts/ajout.py` | `recents [jours]` liste les articles récents ; `fusion fichier.json` ajoute sans doublon, purge > 120 jours, met à jour `updatedAt`. |
| `manifest.webmanifest`, `favicon.png`, `icon-*.png`, `logo-mark.png`, `logo.png` | Installation sur l'écran d'accueil. |
| `sw.js` | Mode hors ligne : réseau d'abord pour les pages et les `.json` (dernière version en cache si pas de réseau), cache d'abord pour images et polices. Incrémenter `VERSION` si la liste `ESSENTIELS` change. |
| `.nojekyll` | GitHub Pages sert les fichiers tels quels. |

## Format d'un article

Champs obligatoires : `id` (slug sans accents), `date` (`YYYY-MM-DD`), `source`, `category`, `title`, `summary`, `url`.
Optionnels : `rank` (ordre dans la journée, 1 = plus important), `comptoir` (conduite à tenir pratique), `related` (`[{label, url, source}]`), `tags`, `approx` (date estimée).

- `source` : `ANSM`, `HAS`, `Moniteur`, `Quotidien`, `Autre`
- `category` : `Ruptures & tensions`, `Vaccins`, `Pharmacovigilance`, `Nouveaux médicaments`, `Recommandations`, `Réglementation`, `Profession`

Ajouter une source ou une catégorie demande de modifier à la fois `index.html` (listes `SOURCES`/`CATS`, couleurs `--s-*`) et `scripts/ajout.py` (`SOURCES`/`CATEGORIES`).

## Onglets

- **Actualités** (`#actualites`, par défaut) : le fil d'articles.
- **Disponibilités** (`#disponibilites`) : la liste ANSM, filtrable par statut (en cours, ruptures, tensions, remises à disposition, arrêts) et par recherche. Chaque rupture ou tension renvoie vers Vigirupture (https://vigirupture.fr/), qui n'a pas d'API publique : on ne fait que lier, sans récupérer ses données.
- Les articles de la catégorie Ruptures & tensions ont aussi un lien « Vérifier sur Vigirupture ».

## Règles de contenu

- Résumés rédigés avec nos propres mots, jamais de phrases copiées des articles (les sources sont sous droit d'auteur, le site est public).
- Chaque article renvoie vers sa source d'origine.

## Mises à jour automatiques

Une tâche programmée Claude (« Mise à jour Officinews », modèle Sonnet) tourne à 6 h 37, 13 h 37 et 18 h 37 (heure de Paris). Elle clone ce dépôt, lit les pages d'actus des quatre sources, écrit les nouveautés dans un fichier temporaire, lance `scripts/ajout.py fusion`, puis commit et push `articles.json`. Au passage de 6 h 37 seulement, elle met aussi à jour `dispo.json` à partir des lignes ANSM modifiées depuis `scripts/dispo.py derniere` ; une resynchronisation complète (`complet`) a lieu le 1er de chaque mois. Hugo veut une consommation de tokens minimale : ne pas alourdir ce flux.

**Règle permanente (demandée par Hugo)** : toute modification du site qui touche ce flux (nouveau fichier de données, nouveau script, changement de format, de source ou d'horaire) doit s'accompagner, dans la même session et sans attendre qu'Hugo le demande, de la mise à jour du prompt de la tâche programmée « Mise à jour Officinews » (identifiant `trig_01Fd6gdYnwGHwx84cpa3Te8Q`, outil `update_trigger`), puis de cette section. Le signaler en une ligne dans la réponse.

## Conventions de la page

- Thèmes clair et sombre via des tokens CSS sur `:root` ; toute nouvelle couleur passe par un token défini dans les deux thèmes.
- Doit rester lisible à 390 px de large sans défilement horizontal (les filtres défilent à l'horizontale sur mobile).
- Direction artistique : appli douce alignée sur le logo (fond vert très pâle, cartes blanches arrondies `--r: 16px` avec ombre légère, pastilles colorées pour sources et statuts, onglets en contrôle segmenté, tuiles de synthèse cliquables en en-tête).
- Polices Google Fonts : Outfit (nom Officinews en 800 bicolore comme le logo, titres en 600-700) et Public Sans (texte).
- Logo : `logo.png` (original), `logo-mark.png` (symbole détouré pour l'en-tête), icônes générées depuis le symbole.
- Le statut « lu » est stocké dans le `localStorage` du navigateur (clé `veille-read`).
- **Mes molécules** : liste de molécules suivies, stockée dans le `localStorage` (clé `officinews-watch`). Panneau sous les tuiles avec le statut de chaque molécule (rupture, tension, disponible, d'après `dispo.json`) et le nombre d'articles sur 30 jours ; les articles et lignes de disponibilité correspondants sont mis en évidence. Comparaison sans accents ni majuscules.
- Après une modification de `index.html`, vérifier que le script se parse et que la page charge les articles sans erreur avant de pousser.
