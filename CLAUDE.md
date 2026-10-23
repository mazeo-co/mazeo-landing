# mazeo-landing · consignes de travail

Le site mazeo.co. Des pages statiques, sans étape de construction : Vercel sert chaque fichier du dépôt tel quel.

Le protocole commun (Journal partagé, pages ÉTAT, to-do) est dans `MAZEO-OPS.md`. Ce fichier ne dit que ce qui est propre à ce dépôt.

## La branche de prod est `main`

- `main` est la seule branche de référence. Elle contient ce qui est en ligne, ou ce qui attend le clic de mise en ligne.
- Tout travail part de `main` à jour : `git fetch origin`, puis `git checkout -b candidate-<sujet> origin/main`.
- PR en brouillon dès le premier commit, vers `main`, avec la zone dans le titre (`[accueil]`, `[quiz]`, `[salons]`…).
- Jamais d'envoi direct sur `main` : GitHub le refuse, y compris pour un administrateur.
- Aucune autre branche ne sert de base. Une branche en avance sur `main` sans PR ouverte est une anomalie : la signaler à Romain.

## Mettre en ligne

1. Romain fusionne la PR dans `main`.
2. Vercel construit la version, sans la mettre en ligne (réglage « Auto-assign Custom Production Domains » désactivé).
3. Romain clique « Promote » sur ce déploiement dans Vercel. C'est ce clic qui met en ligne.
4. La prod met quelques secondes à servir la nouvelle version : revérifier sur www.mazeo.co avant de conclure.

Une PR fusionnée n'est donc pas en ligne tant que le « Promote » n'est pas fait. Le dire à Romain à chaque fusion.

## Ce que le site sert

Tout fichier du dépôt est lisible par tous sur mazeo.co, sauf ceux listés dans `.vercelignore`. Le dépôt lui-même est public. Ne rien poser ici qui ne doit pas être lu par tous.

## La barre « mazeo / Ressources » des ressources

Chaque ressource (growth academy et ses fiches, Village, Pitch, Quiz, salons, Dernier appel, Bourse de l'emploi) porte en haut la barre « mazeo / Ressources / <la ressource> ». Elle vient d'une seule ligne posée juste après `<body>` :

`<script src="/assets/fil-ressources.js"></script>`

- Nouvelle ressource : ajouter cette ligne dans sa page (FR et EN), et son chemin dans la liste `RESSOURCES` de `assets/fil-ressources.js`.
- Les générateurs hors dépôt la posent déjà : `~/dev/quiz-build.py`, `~/dev/salons-etudes/site.py`, `~/dev/infographie-pistes/site_village.py`.
- Une page calée sur la hauteur de l'écran retranche `var(--fil-h)` (exemple : `academy.html`, `pitch-des-etudes.html`).
- La fiche 1 (`positionnement.html`, `en/positioning.html`) n'a pas la barre : ses écrans sont calés au pixel sur 1400 × 715 et son en-tête est fixe.

## Historique

Jusqu'au 05/10/2026, le site vivait sur la branche `fix/login-redirect-app` et `main` datait de mars 2026. Le 05/10/2026, `main` a été avancée jusqu'à la version en ligne, l'ancienne branche supprimée, et `main` verrouillée.
