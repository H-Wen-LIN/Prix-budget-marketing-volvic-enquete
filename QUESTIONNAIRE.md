# Questionnaire A/B : eau au collagène d'origine végétale (A) ou animale (B)

**Principe** : chaque répondant voit une seule version, attribuée au hasard (randomisation par blocs de 4 : 2 A et 2 B dans un ordre aléatoire). Le texte, l'image, le format et la marque sont identiques ; seul le mot « végétale » / « animale » change.

## Accueil
**Q1.** « Cette enquête porte sur les boissons. Elle dure environ 5 minutes. Vos réponses sont anonymes et utilisées uniquement à des fins d'étude. Acceptez-vous de participer ? » ☐ Oui ☐ Non (fin)

## Filtre
- **Q2.** Au cours des 3 derniers mois, avez-vous acheté de l'eau en bouteille ? ☐ Oui ☐ Non (fin)
- **Q3.** Au cours des 3 derniers mois, avez-vous acheté au moins une fois une boisson ou un complément enrichi (vitamines, protéines, collagène…) ? Les boissons énergisantes ne sont pas concernées. ☐ Oui ☐ Non
- **Q4.** Quel est votre âge ? ____ ans (moins de 18 ans → fin : « Cette étude est réservée aux personnes âgées de 18 ans et plus. »)

## L'offre (seule partie qui change), même visuel de bouteille 50 cl

| Version A | Version B |
|---|---|
| « Eau minérale naturelle enrichie en collagène d'origine végétale. 50 cl. » | « Eau minérale naturelle enrichie en collagène d'origine animale. 50 cl. » |

## Contrôle de manipulation (juste après l'offre)
- **Q5.** D'après la description, quelle est l'origine du collagène contenu dans ce produit ? ☐ Origine végétale ☐ Origine animale ☐ Origine marine ☐ Je ne sais pas
- Les répondants qui se trompent sont isolés à l'export (colonne `groupe_controle`).

## Van Westendorp (curseurs du coût de revient estimé, 0,50 €, à 10 €, par pas de 0,10 €)
- **Q6.** À partir de quel prix trouveriez-vous ce produit trop cher au point de ne pas l'acheter ?
- **Q7.** À partir de quel prix le trouveriez-vous cher, tout en envisageant de l'acheter ?
- **Q8.** À quel prix le trouveriez-vous bon marché, une bonne affaire ?
- **Q9.** À partir de quel prix le trouveriez-vous trop bon marché au point de douter de sa qualité ?

## Gabor-Granger (Q10, réponse Oui / Non, sur une seule page)
« Achèteriez-vous ce produit au prix de X € ? » ☐ Oui ☐ Non
Prix du plus élevé au plus bas : 3,50 € → 2,90 € → 2,40 € → 1,90 € → 1,50 €. Le prix suivant n'apparaît que si la réponse est Non ; arrêt au premier Oui.

## Perception (Likert 5 points, une échelle propre à chaque question)
| | Question | Échelle (1 → 5) |
|---|---|---|
| Q11 | Comment jugez-vous la qualité de ce produit ? | Très mauvaise → Très bonne |
| Q12 | Selon vous, quel est l'effet de ce produit sur la santé ? | Très négatif → Très positif |
| Q13 | Quel degré de confiance accordez-vous à l'efficacité de ce produit ? | Aucune confiance → Totale confiance |
| Q14 | Ce produit correspond-il à vos valeurs (éthique, environnement) ? | Pas du tout → Tout à fait |
| Q15 | Ce produit vous paraît-il naturel ? | Pas du tout naturel → Très naturel |

## Profil
- **Q16.** Vous êtes : ☐ une femme ☐ un homme ☐ autre ☐ je préfère ne pas répondre
- **Q17.** Régime alimentaire : ☐ omnivore ☐ flexitarien ☐ végétarien ☐ végan ☐ autre (variable clé à croiser)
- **Q18.** Dépense habituelle pour une bouteille d'eau de 50 cl : ☐ moins de 0,30 € ☐ 0,30–0,49 € ☐ 0,50–0,79 € ☐ 0,80–0,99 € ☐ 1,00–1,49 € ☐ 1,50–1,99 € ☐ 2,00 € ou plus

## Analyse
- Van Westendorp : point de prix optimal (OPP), plage de prix acceptable, par version.
- Gabor-Granger : courbe de demande et prix maximisant le revenu, par version.
- Comparaison A vs B : test t ou Mann-Whitney ; croisement par régime alimentaire.
- Échantillon cible : 100 à 150 répondants par version.
