# Enquête prix — eau au collagène vegan (A) vs bovin (B)

- `QUESTIONNAIRE.md` : questionnaire complet et plan d'analyse.
- `index.html` : version interactive (ouvrir dans un navigateur). Attribution aléatoire A/B par blocs de 4 (équilibre exact 50/50 sur un même appareil), filtres de fin, Van Westendorp sur curseurs 0,50–10 € avec contrôle de cohérence, Gabor-Granger descendant sur une seule page (Oui/Non, 3,50 → 1,50 €, arrêt au premier Oui), contrôle de manipulation (`controle_ok`), Likert facultatif, profil. Les réponses sont stockées localement et exportables en CSV (séparateur `;`), triées par résultat au contrôle Q5 (colonne `groupe_controle`).

**Mode administrateur** : ouvrir `index.html#admin` pour afficher en fin de questionnaire le compteur, le bouton « Nouveau répondant » et l'export CSV. Sans `#admin`, les répondants ne voient que le message de remerciement.
