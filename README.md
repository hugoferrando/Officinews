# Officinews

Journal de veille pharmaceutique : actualités ANSM, HAS, Le Moniteur des pharmacies et Le Quotidien du pharmacien, triées pour le comptoir.

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `index.html` | La page du journal (aucune dépendance à installer) |
| `articles.json` | Les articles affichés, mis à jour trois fois par jour |
| `dispo.json` | La liste ANSM des ruptures et tensions (onglet Ruptures), mise à jour chaque matin |
| `vaccins.json` | Les campagnes de vaccination en cours (onglet Vaccins), mises à jour quand l'ANSM ou la HAS en parlent |
| `sw.js` | Mode hors ligne |
| `manifest.webmanifest`, `icon-*.png`, `favicon.png` | Pour ajouter Officinews à l'écran d'accueil comme une appli |
| `.nojekyll` | Dit à GitHub Pages de servir les fichiers tels quels |

## Mettre en ligne sur GitHub Pages

1. Sur github.com, crée un dépôt nommé `officinews` (public, sans README).
2. Clique sur **Add file → Upload files**, glisse tous les fichiers du dossier (y compris `.nojekyll`), puis **Commit changes**.
3. Va dans **Settings → Pages**. Sous *Build and deployment*, choisis **Deploy from a branch**, branche `main`, dossier `/ (root)`, puis **Save**.
4. Après une à deux minutes, le site est en ligne à l'adresse `https://<ton-identifiant>.github.io/officinews/`.

Sur iPhone : ouvre l'adresse dans Safari, bouton Partager, **Sur l'écran d'accueil**.

## Mises à jour automatiques

Les mises à jour remplacent `articles.json` dans le dépôt. Le site se met à jour tout seul après chaque commit (environ une minute).

Format d'un article dans `articles.json` :

```json
{
  "id": "slug-unique",
  "date": "2026-10-28",
  "rank": 1,
  "source": "ANSM | HAS | Moniteur | Quotidien | Autre",
  "category": "Ruptures & tensions | Vaccins | Pharmacovigilance | Nouveaux médicaments | Recommandations | Réglementation | Profession",
  "title": "Titre de l'article d'origine",
  "summary": "Résumé en une à deux phrases",
  "comptoir": "Conduite à tenir (optionnel)",
  "url": "https://…",
  "related": [{"label": "Le Moniteur", "url": "https://…", "source": "Moniteur"}],
  "tags": ["molécule", "pathologie"],
  "approx": true
}
```

`updatedAt` en haut du fichier indique l'heure de la dernière mise à jour, affichée dans l'en-tête du journal.

Le script `scripts/ajout.py` fait la fusion : `python3 scripts/ajout.py recents` liste les articles des 7 derniers jours, `python3 scripts/ajout.py fusion nouveaux.json` ajoute les nouveaux articles sans doublon, supprime ceux de plus d'un an et met à jour `updatedAt`.

## Nom de domaine (optionnel)

Pour utiliser `officinews.fr` : achète le domaine, crée dans le dépôt un fichier `CNAME` contenant `officinews.fr`, puis suis la page d'aide GitHub « Managing a custom domain for your GitHub Pages site » pour les réglages DNS chez ton registrar.

## Note

Le site est public. Les résumés sont rédigés pour la veille ; chaque article renvoie vers sa source d'origine, où se trouve le texte complet.
