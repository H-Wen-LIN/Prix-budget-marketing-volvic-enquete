# Questionnaire A/B : eau au collagène d'origine végétale (A) ou animale (B)

**Principe** : chaque répondant voit une seule version, attribuée au hasard (randomisation par blocs de 4 : 2 A et 2 B dans un ordre aléatoire). Le texte, l'image, le format et la marque sont identiques ; seul le mot « végétale » / « animale » change.

## Accueil
> Bonjour !
>
> Nous sommes un groupe d'étudiants de M1 Marketing à l'IAE Clermont Auvergne. Dans le cadre d'un projet de cours, nous étudions le prix que les consommateurs accepteraient de payer pour une bouteille d'eau Volvic proposant une innovation visant à soutenir naturellement la production de collagène.
>
> Le questionnaire prend environ 5 minutes. Il est anonyme : nous ne recueillons ni nom ni adresse e-mail. Les réponses servent uniquement à ce projet.

**Q1.** Acceptez-vous de participer ? ☐ Oui ☐ Non (fin)

Mention en bas de chaque page : « Étude universitaire — M1 Marketing, IAE Clermont Auvergne. Non affiliée à la marque Volvic. »

## Filtre
- **Q2.** Au cours des 3 derniers mois, avez-vous acheté de l'eau en bouteille ? ☐ Oui ☐ Non (n'élimine pas)
- **Q3.** Au cours des 3 derniers mois, avez-vous acheté au moins une fois une boisson ou un complément enrichi (vitamines, protéines, collagène…) ? Les boissons énergisantes ne sont pas concernées. ☐ Oui ☐ Non
- **Q4.** Quel est votre âge ? Curseur de 0 à 100 ans (moins de 18 ans → fin : « Cette étude est réservée aux personnes âgées de 18 ans et plus. »)

## L'offre (seule partie qui change) : photo du produit Volvic Boost « Soutien collagène » 50 cl

Photos : `img/bouteille_vegetal.jpg` (version A, étiquette verte « 100 % végétal ») et `img/bouteille_animal.jpg` (version B, étiquette rose « Collagène d'origine animale »). La photo est montrée sur l'écran de l'offre puis rappelée en vignette au-dessus des questions de prix (Q6 à Q10).

| Version A | Version B |
|---|---|
| « Eau minérale naturelle enrichie en collagène d'origine végétale. 50 cl. » | « Eau minérale naturelle enrichie en collagène d'origine animale. 50 cl. » |

## Contrôle de manipulation (juste après l'offre)
- **Q5.** D'après la description, quelle est l'origine du collagène contenu dans ce produit ? ☐ Origine végétale ☐ Origine animale ☐ Origine marine ☐ Je ne sais pas
- Les répondants qui se trompent sont isolés à l'export (colonne `groupe_controle`).

## Van Westendorp (curseurs du coût de revient estimé, 0,50 €, à 10 € ; boutons − / + par pas de 0,10 €)
- **Q6.** À partir de quel prix trouveriez-vous ce produit trop cher au point de ne pas l'acheter ?
- **Q7.** À partir de quel prix le trouveriez-vous cher, tout en envisageant de l'acheter ?
- **Q8.** À quel prix le trouveriez-vous bon marché, une bonne affaire ?
- **Q9.** À partir de quel prix le trouveriez-vous trop bon marché au point de douter de sa qualité ?

## Gabor-Granger (Q10, réponse Oui / Non, sur une seule page)
« Achèteriez-vous ce produit au prix de X € ? » ☐ Oui ☐ Non
Prix du plus élevé au plus bas : 3,50 € → 2,90 € → 2,40 € → 1,90 € → 1,50 €. Le prix suivant n'apparaît que si la réponse est Non ; arrêt au premier Oui.

## Perception (Q11 à Q17, une seule page, échelles en 7 points reprises des échelles d'origine)
Les concepts ne sont pas affichés aux répondants. Sources et liens : voir `SOURCES.md`.

| | Question | Concept | Échelle (1 → 7) |
|---|---|---|---|
| Q11 | Ce produit peut-il contribuer à votre bien-être ? | Bien-être | Différentiel sémantique : Ne joue aucun rôle → Joue un rôle très important |
| Q12 | Pensez-vous que ce produit convient à une consommation quotidienne ? | Routine (compatibilité) | Likert : Extrêmement en désaccord → Extrêmement d'accord |
| Q13 | Ce produit correspond-il à vos valeurs (éthique, environnement) ? | Valeurs | Likert : Pas du tout d'accord → Tout à fait d'accord |
| Q14 | L'innovation de ce produit justifie-t-elle un prix plus élevé ? | Innovation (prix premium) | Likert : Pas du tout d'accord → Tout à fait d'accord |
| Q15 | Quel degré de confiance accordez-vous à l'efficacité de ce produit ? | Confiance | Likert : Très fortement en désaccord → Très fortement d'accord |
| Q16 | La présence de collagène vous donne-t-elle une impression de qualité supérieure ? | Qualité perçue | Échelle bipolaire : Très mauvaise qualité → Très bonne qualité |
| Q17 | L'ajout de collagène vous semble-t-il compatible avec l'image naturelle de l'eau minérale ? | RSE (fit) | Différentiel sémantique : Incohérent → Cohérent |

## Profil
- **Q18.** Vous êtes : ☐ une femme ☐ un homme ☐ autre ☐ je préfère ne pas répondre
- **Q19.** Régime alimentaire : ☐ omnivore ☐ flexitarien ☐ végétarien ☐ végan ☐ autre (variable clé à croiser)
- **Q20.** Dépense habituelle pour une bouteille d'eau de 50 cl : ☐ moins de 0,30 € ☐ 0,30–0,49 € ☐ 0,50–0,79 € ☐ 0,80–0,99 € ☐ 1,00–1,49 € ☐ 1,50–1,99 € ☐ 2,00 € ou plus

## Analyse
- Van Westendorp : point de prix optimal (OPP), plage de prix acceptable, par version.
- Gabor-Granger : courbe de demande et prix maximisant le revenu, par version.
- Comparaison A vs B : test t ou Mann-Whitney ; croisement par régime alimentaire.
- Échantillon cible : 100 à 150 répondants par version.
