# Officinews

Journal de veille pharmaceutique personnel de Hugo (étudiant en 6e année de pharmacie, filière officine, Montpellier). Agrège les actualités ANSM, HAS, Le Moniteur des pharmacies et Le Quotidien du pharmacien : médicaments, vaccins, ruptures, pharmacovigilance, recos, réglementation, profession. Répondre en français.

Site public : https://hugoferrando.github.io/Officinews/ (GitHub Pages, branche `main`, racine du dépôt).

## Structure

| Fichier | Rôle |
|---|---|
| `index.html` | Toute la page : HTML, CSS et JS dans un seul fichier, sans dépendance ni build. Charge `articles.json`, `dispo.json` et `vaccins.json`. |
| `articles.json` | `{ "updatedAt": "<ISO Europe/Paris>", "articles": [...] }`. Seul fichier modifié par les mises à jour automatiques. |
| `dispo.json` | `{ "updatedAt", "source", "items": [{statut, maj, nom, remise, domaines}] }` : liste ANSM « Disponibilité des produits de santé – médicaments », affichée dans l'onglet Ruptures. |
| `vaccins.json` | `{ "updatedAt", "campagnes": [{id, nom, debut, fin, pourQui, produits, officine, source}], "recos": [{date, titre, texte, source}] }` : onglet Vaccins. Mis à jour par la tâche programmée **seulement** quand un nouvel article ANSM ou HAS concerne une campagne ou une recommandation vaccinale, via `scripts/vaccins.py`. Peut aussi être modifié à la main ; vérifier les faits sur une source officielle. |
| `scripts/vaccins.py` | `voir` résume les campagnes et recos ; `maj patch.json` met à jour les champs fournis d'une campagne (par `id`), en ajoute une nouvelle, ajoute des recos (dédoublonnées par source, 5 max) ou retire des campagnes. |
| `scripts/dispo.py` | `afaire` répond « oui » si la liste n'a pas été rafraîchie aujourd'hui ; `derniere` donne la date de mise à jour la plus récente ; `fusion lignes.txt` ajoute ou met à jour les produits ; `complet lignes.txt` remplace toute la liste. Les remises à disposition et arrêts de plus de 90 jours sont retirés. |
| `scripts/ajout.py` | `age` donne le nombre d'heures depuis la dernière mise à jour ; `recents [jours]` liste les articles récents (fenêtre élargie automatiquement si des passages ont été manqués) ; `fusion fichier.json` ajoute sans doublon, purge > 1 an (365 jours), met à jour `updatedAt`. |
| `manifest.webmanifest`, `favicon.png`, `icon-*.png`, `logo-mark.png`, `logo.png` | Installation sur l'écran d'accueil. |
| `sw.js` | Mode hors ligne : réseau d'abord **sans cache HTTP** (`no-store`) pour les pages et les `.json` (dernière version en cache si pas de réseau), cache d'abord pour images et polices. Enregistré avec `updateViaCache: "none"` et vérifié à chaque retour sur l'appli. Incrémenter `VERSION` si la liste `ESSENTIELS` ou la logique change. |
| `.nojekyll` | GitHub Pages sert les fichiers tels quels. |

## Format d'un article

Champs obligatoires : `id` (slug sans accents), `date` (`YYYY-MM-DD`), `source`, `category`, `title`, `summary`, `url`.
Obligatoire aussi depuis le 30/10/2026 (demande d'Hugo) : `comptoir` (une phrase pratique, encadré « Au comptoir », présent sur tous les articles). Optionnels : `rank` (ordre dans la journée, 1 = plus important), `related` (`[{label, url, source}]`), `tags`, `approx` (date estimée).

- `source` : `ANSM`, `HAS`, `Moniteur`, `Quotidien`, `Autre`
- `category` : `Ruptures & tensions`, `Vaccins`, `Pharmacovigilance`, `Nouveaux médicaments`, `Recommandations`, `Réglementation`, `Profession`

Ajouter une source ou une catégorie demande de modifier à la fois `index.html` (listes `SOURCES`/`CATS`, couleurs `--s-*`) et `scripts/ajout.py` (`SOURCES`/`CATEGORIES`).

## Onglets

- **Actus** (`#actualites`, par défaut) : le fil d'articles. Recherche + bouton « Filtres » (source, non lus) replié ; les thèmes restent visibles en une ligne défilante.
- **Ruptures** (`#disponibilites`) : la liste ANSM, filtrable par statut (puces), par domaine et ordre (dans « Filtres »), et par recherche. Chaque rupture ou tension renvoie vers Vigirupture (https://vigirupture.fr/), qui n'a pas d'API publique : on ne fait que lier, sans récupérer ses données.
- **Vaccins** (`#vaccins`) : campagnes en cours (grippe, Covid-19, VRS) et recommandations récentes, depuis `vaccins.json`.
- Les articles de la catégorie Ruptures & tensions ont un lien « Vigirupture ↗ ».
- **Outils de référence** (constante `TOOLS` dans `index.html`) : liens Antibioclic, Meddispar, fiches OMéDIT et ameli ajoutés en bas d'une carte seulement si son texte (sans accents) correspond à l'expression régulière de l'outil, 2 au maximum ; Antibioclic aussi sur les ruptures/tensions d'antibiotiques ; liens propres aux campagnes dans `vaccins.json` (`liens`). Tous les outils sont listés dans le second pied de page.
- Journal officiel : écarté pour l'instant (pas de page publique simple à lire automatiquement sans alourdir la tâche) ; les textes importants arrivent via l'ANSM et la presse.

## Règles de contenu

- Résumés rédigés avec nos propres mots, jamais de phrases copiées des articles (les sources sont sous droit d'auteur, le site est public).
- Chaque article renvoie vers sa source d'origine.

## Mises à jour automatiques

Une tâche programmée Claude (« Mise à jour Officinews », modèle Sonnet) tourne **une fois par jour à 6 h 37** (heure de Paris) : horaire choisi par Hugo lui-même le 28/10/2026, ne pas le modifier sans qu'il le demande. Le prompt garde une règle de rattrapage (9 h 37, 16 h 37, 21 h 37, arrêt si la dernière mise à jour a moins de 4 h via `ajout.py age`), inactive tant que ces horaires ne sont pas dans le planning. Un passage peut échouer avant de démarrer quand la limite d'utilisation d'Hugo est atteinte (statut `USAGE_LIMIT_REACHED`) : le passage suivant rattrape toute la période manquée. Le dépôt doit être **attaché à la tâche** (réglages de la tâche → Advanced settings → Repository) pour être cloné au démarrage sans approbation ; sinon le prompt se rabat sur `add_repo`, qui demande une validation à Hugo et bloque les passages automatiques. L'environnement cloud de la tâche doit aussi autoriser les sites des sources : Hugo l'a réglé en Network access → **Full** le 29/10/2026 (avec l'accès par défaut, WebFetch échouait en `ENOTFOUND`). Elle se place dans ce dépôt, lit les pages d'actus des quatre sources, écrit les nouveautés dans un fichier temporaire, lance `scripts/ajout.py fusion`, puis commit et push `articles.json`. Au premier passage réussi de la journée (`dispo.py afaire` = oui), elle met aussi à jour `dispo.json` à partir des lignes ANSM modifiées depuis `scripts/dispo.py derniere` ; une resynchronisation complète (`complet`) a lieu le 1er de chaque mois. Si un nouvel article ANSM ou HAS annonce une campagne de vaccination (début, fin, publics, produits) ou une nouvelle recommandation vaccinale, elle met aussi à jour `vaccins.json` avec `scripts/vaccins.py maj`. Hugo veut une consommation de tokens minimale : ne pas alourdir ce flux.

La procédure complète de la tâche est dans **`scripts/TACHE.md`** ; le prompt de la tâche se contente de dire de la suivre. Pour modifier le flux, modifier ce fichier (et le prompt seulement si nécessaire).

**Règle permanente (demandée par Hugo)** : toute modification du site qui touche ce flux (nouveau fichier de données, nouveau script, changement de format, de source ou d'horaire) doit s'accompagner, dans la même session et sans attendre qu'Hugo le demande, de la mise à jour de `scripts/TACHE.md` (que suit la tâche programmée « Mise à jour Officinews 2 », identifiant `trig_01BkQ7em91LWtGJmt9xt7wWz`, créée par Hugo sur claude.ai/code/routines avec le dépôt attaché ; Claude ne peut ni la lancer ni modifier son prompt, Hugo le fait depuis cette page si besoin), puis de cette section. Le signaler en une ligne dans la réponse.

## Conventions de la page

- Thèmes clair et sombre via des tokens CSS sur `:root` ; toute nouvelle couleur passe par un token défini dans les deux thèmes.
- Doit rester lisible à 390 px de large sans défilement horizontal (les filtres défilent à l'horizontale sur mobile).
- Direction artistique : **épurée**, demandée par Hugo (peu de texte, peu de boutons). Fond vert très pâle, cartes blanches arrondies (`--r: 16px`), onglets en contrôle segmenté, 3 tuiles cliquables (cette semaine, ruptures 30 j, non lus), filtres secondaires repliés derrière un bouton « Filtres », sources supplémentaires d'un article repliées (« + N sources »), « marquer lu » réduit à une coche ronde en haut à droite des cartes. Ne pas réintroduire de paragraphes d'explication ni de boutons visibles en permanence.
- Polices Google Fonts : Outfit (nom Officinews en 800 bicolore comme le logo, titres en 600-700) et Public Sans (texte).
- Logo : `logo.png` (original), `logo-mark.png` (symbole détouré pour l'en-tête), icônes générées depuis le symbole.
- Le statut « lu » est stocké dans le `localStorage` du navigateur (clé `veille-read`).
- **Mes molécules** : liste de molécules suivies, stockée dans le `localStorage` (clé `officinews-watch`). Rangée de puces sous les tuiles, colorées selon le statut ANSM (rouge rupture, orange tension, vert sinon), formulaire d'ajout replié derrière « + Ajouter » ; les articles et lignes de disponibilité correspondants sont mis en évidence. Comparaison sans accents ni majuscules.
- **Fil d'actus** : un an d'articles conservé ; sans recherche, seuls les 30 derniers jours s'affichent, puis + 90 jours à chaque « Voir les plus anciens » ; une recherche (y compris depuis Mes molécules) couvre toute l'année.
- **Liens sur iPhone** : quand le site est lancé depuis l'écran d'accueil iOS, les liens externes sont ouverts via le préfixe `x-safari-https://` pour aller directement dans Safari (et ses connexions au Quotidien, au Moniteur…) ; si Safari ne s'ouvre pas en 1,2 s, repli sur l'ouverture normale. Hugo est sur iPhone.
- **Mise à jour sans réinstaller l'appli** : à chaque retour au premier plan (`visibilitychange`), la page relit `index.html` sans cache et se recharge si son empreinte a changé ; les `.json` sont relus si la dernière lecture date de plus d'une minute. Ne pas supprimer ce mécanisme.
- Après une modification de `index.html`, vérifier que le script se parse et que la page charge les articles sans erreur avant de pousser.
