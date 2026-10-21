# Mise en ligne et collecte des réponses

Deux réglages à faire une seule fois, avec vos comptes (environ 10 minutes) :
**A.** créer la Google Sheet qui reçoit les réponses ; **B.** activer GitHub Pages pour avoir l'adresse publique du questionnaire.

## A. Google Sheet + script de collecte (gratuit)

1. Sur [sheets.google.com](https://sheets.google.com), créez une feuille vide, par exemple « Réponses enquête collagène ».
2. Menu **Extensions > Apps Script**. Effacez le code présent et collez **tout** le contenu de [`apps-script.gs`](apps-script.gs). Cliquez sur l'icône **Enregistrer**.
3. En haut à droite : **Déployer > Nouveau déploiement**.
   - Roue dentée « Sélectionner le type » : **Application Web**.
   - Description : `collecte v1`.
   - **Exécuter en tant que : Moi** (votre compte : c'est lui qui écrit dans la feuille).
   - **Qui a accès : Tout le monde** (indispensable : les répondants n'ont pas de compte Google à utiliser).
   - **Déployer**, puis **Autoriser l'accès** avec votre compte Google. Si Google affiche « Google n'a pas validé cette application », cliquez sur **Paramètres avancés > Accéder au projet (non sécurisé)** : c'est votre propre script.
4. Copiez l'**URL de l'application Web** (elle commence par `https://script.google.com/macros/s/` et finit par `/exec`).
5. Vérification : ouvrez cette URL dans un navigateur. Vous devez voir `{"ok":true,"reponses":0}` et un onglet **Reponses** avec les en-têtes de colonnes apparaît dans la feuille.
6. Donnez-moi cette URL (ou collez-la dans `index.html`, ligne `const COLLECTE_URL = "";`, entre les guillemets). Ce n'est pas un mot de passe : elle permet seulement d'**ajouter** des lignes, pas de lire la feuille.

> Si vous modifiez un jour `apps-script.gs`, refaites **Déployer > Gérer les déploiements > Modifier (crayon) > Version : Nouvelle version**, pour garder la même URL.

## B. GitHub Pages (gratuit)

1. Sur GitHub, dépôt **Prix-budget-marketing-volvic-enquete** > **Settings** > **Pages**.
2. **Source : Deploy from a branch** ; **Branch : `claude/adoring-brahmagupta-ec1uhd`**, dossier **`/ (root)`** ; **Save**.
3. Après 1 à 2 minutes, le questionnaire est en ligne à l'adresse :
   **https://h-wen-lin.github.io/Prix-budget-marketing-volvic-enquete/**

## Consulter et exporter les réponses

- Les réponses arrivent en temps réel dans l'onglet **Reponses** de la Google Sheet, une ligne par questionnaire.
- Export : **Fichier > Télécharger > Microsoft Excel (.xlsx)** ou **Valeurs séparées par des virgules (.csv)**.
- Dictionnaire des colonnes :

| Colonne | Contenu |
|---|---|
| `id` | identifiant technique aléatoire (non nominatif) |
| `recu_le` | date et heure de réception (UTC) |
| `version` | A = collagène végétal, B = collagène animal |
| `statut` | `complet`, `mineur` (arrêt < 18 ans) ou `refus` (Q1 = Non) |
| `debut`, `fin` | horodatage de début et de fin dans le navigateur (UTC) |
| `consentement` | Q1 |
| `F1`, `F2`, `F3` | Q2 (eau en bouteille), Q3 (boisson enrichie), Q4 (âge en années) |
| `C1`, `controle_ok`, `groupe_controle` | Q5 (contrôle) ; 1 = bonne réponse selon la version, 0 = erreur |
| `P1` à `P4` | Q6 à Q9 (Van Westendorp, en €) : trop cher, cher, bonne affaire, trop bon marché |
| `G_3.50` … `G_1.50` | Q10 (Gabor-Granger) : Oui / Non à chaque prix montré ; vide = prix non montré |
| `GG_prix_accepte` | premier prix accepté (vide si aucun) |
| `bien_etre` … `rse` | Q11 à Q17, score de 1 à 7 (1 = pôle négatif) |
| `genre`, `regime`, `depense_50cl` | Q18 à Q20 |

## Fonctionnement et garanties

- Chaque questionnaire terminé (complet, mineur ou refus) est envoyé à la Google Sheet. Un questionnaire abandonné en cours de route n'est **pas** envoyé.
- En cas de coupure réseau, la réponse reste en attente sur l'appareil du répondant : le site réessaie automatiquement, affiche un bouton « Réessayer », et renvoie aussi à la visite suivante.
- Pas de doublon : le script ignore un identifiant déjà reçu.
- Aucun nom, e-mail, adresse IP ni identifiant d'appareil n'est collecté.
- Limite : une même personne peut répondre deux fois en rechargeant la page (impossible à empêcher sans identifier les répondants).

## Avant de diffuser

1. Faites un ou deux questionnaires de test sur l'adresse publique, vérifiez qu'ils apparaissent dans la feuille, puis **supprimez ces lignes de test** (clic droit sur le numéro de ligne > Supprimer la ligne). Gardez la ligne 1 (les en-têtes).
2. Diffusez l'adresse : https://h-wen-lin.github.io/Prix-budget-marketing-volvic-enquete/

## Importer les données dans le dépôt

Le script peut renvoyer toutes les réponses en CSV, **uniquement** avec une clé secrète :

1. Dans Apps Script : **Paramètres du projet** (roue dentée) > **Propriétés du script** > ajouter la propriété `EXPORT_KEY` avec une valeur longue et aléatoire.
2. Redéployer : **Déployer > Gérer les déploiements > Modifier (crayon) > Version : Nouvelle version > Déployer**. L'URL `/exec` ne change pas.
3. Import :
   ```
   EXPORT_KEY="la-clé" python3 collecte/importer.py
   ```
   Le fichier `donnees/reponses.csv` est créé (séparateur `;`, UTF-8, lisible par Excel).

- La clé ne doit **jamais** être écrite dans un fichier du dépôt.
- Si elle a fuité : changez la valeur de `EXPORT_KEY` dans les Propriétés du script. Il n'y a rien à redéployer.
- Le dépôt est public : `donnees/reponses.csv` est visible par tout le monde sur GitHub.
