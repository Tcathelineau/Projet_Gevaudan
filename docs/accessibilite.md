# Accessibilité : état des lieux

Objectif de conception : WCAG 2.2 niveau AA. L'application n'est **pas** auditée et ne se déclare conforme à aucun référentiel (RGAA, EN 301 549).

## Ce qui est en place
- **Contrastes** : les couleurs de texte de `styles.py` sont calculées contre les fonds sombres (4,5:1 minimum) ; deux corrections faites (texte du badge des loups, petit texte « Loups » de la page Documentation). Test : `tests/test_accessibilite.py`.
- **Clavier** : les dalles, cases et boutons sont de vrais éléments interactifs ; le focus est toujours visible (contour doré de 3 px).
- **Langue** : la page se déclare en français (Streamlit la déclare en anglais par défaut).
- **Taille des cibles** : zone cliquable des icônes d'aide agrandie à 24 px.
- **Images** : les illustrations de rôles sont décoratives (`aria-hidden`), le nom du rôle figure toujours en texte.
- **Couleur seule** : aucune information n'est portée par la couleur seule (jauges et barres ont une valeur en texte, les camps ont un libellé).
- **Animations** : réduites ou coupées si le système demande de réduire les animations (scènes, retournement de carte).
- **Petits écrans** : pas de défilement horizontal à 375 px ; panneaux de composition empilés sous 520 px ; boutons d'accueil qui ne coupent plus les mots.

## Ce qui n'a pas été vérifié
- Aucun test avec un lecteur d'écran (VoiceOver, NVDA).
- Pas d'analyse automatique (axe-core) ni de test à 200 % d'agrandissement ou à 320 px.
- Les écrans de nuit et de conseil n'ont pas été contrôlés en mode mobile ; seuls l'accueil et la composition l'ont été.
- Les composants de Streamlit eux-mêmes (listes déroulantes, onglets) ne sont pas maîtrisés par ce dépôt.
- Le jeu en hotseat repose sur le secret visuel : un joueur aveugle ne peut pas profiter des écrans de passage.
