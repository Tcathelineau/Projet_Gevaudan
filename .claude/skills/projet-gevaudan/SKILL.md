---
name: projet-gevaudan
description: Connaissance du projet Gévaudan (Loup-Garou en Streamlit, jeu hotseat) : architecture du code, conventions, règles de jeu déjà décidées, ambiance visuelle, façon de travailler avec l'équipe. À charger avant toute modification du jeu, d'un rôle, d'une option, de l'interface ou du README.
---

# Projet Gévaudan : guide pour travailler dessus

Application Streamlit de Loup-Garou en **hotseat** : un seul appareil passe de main en main, sans maître du jeu. Dépôt `github.com/Tcathelineau/Projet_Gevaudan` (compte personnel Tcathelineau, pas l'identité git professionnelle).

```bash
uv run --python 3.12 --with streamlit streamlit run src/loup_garou_app.py
```

## 1. Esprit du projet

- **Jeu grandeur nature** sur plusieurs heures ou jours : l'app gère rôles, nuits et votes ; l'essentiel se joue entre les joueurs. Le rythme des conseils est libre. Les morts deviennent des « esprits frappeurs » (ils discutent, ne votent pas). Ces règles sociales sont dans le README, pas dans le code.
- **Pas de maître du jeu** : l'app joue ce rôle. Chaque écran doit être compréhensible par quelqu'un qui découvre le jeu.
- **Secret d'abord** : à chaque tour de nuit, deux écrans de passage (« Je vais chercher X », puis « Oui, je suis X ») évitent qu'on voie la carte d'un autre. Ne jamais afficher un rôle ou un résultat de vision sans passer par ces écrans.
- **Ambiance** : thème sombre (`.streamlit/config.toml`, `base = "dark"`), village gothique en SVG/CSS animé (lune, étoiles, nuages, maisons, confettis de victoire, lune de sang), cartes de rôle avec dégradé propre à chaque rôle, bandeaux et encarts d'annonce (`annonce`, `plaquette`, `scene_ciel`, `scene_victoire`). Toute nouvelle interface doit rester dans ce registre : pas de widget Streamlit brut quand une brique maison existe.
- **Sobriété visuelle** : pas de scroll dans l'écran de nuit (conteneur de hauteur 400), les dalles tiennent sur 3 lignes au plus.
- Les textes affichés sont en **français**, tutoiement dans les écrans de passage.

## 2. Architecture du code

```
src/loup_garou_app.py        point d'entrée (importe loup_garou.app.main)
src/loup_garou/
  assets/                    roles/<clé>.svg (icônes CC BY 3.0, cf. CREDITS.md), sons/ (musiques MP3 CC0 FreePD, bruitages WAV synthétisés), favicon.png
  config.py                  SAVE_FILE, HISTORIQUE_DIR, MUSIQUE_FILE (chemins relatifs au dossier courant)
  options.py                 OPTIONS_DEFAUT, opt(), taille_couple(), nuit_active(), prochaine_nuit(), CADENCES
  roles.py                   dataclass Role, registre ROLES, ROLES_SPECIAUX (données seulement)
  moteur/                    règles du jeu, SANS Streamlit
    partie.py                nouvelle_partie, vivants, camp, tuer, vainqueur, fin_de_tour,
                             terminer_partie, resoudre_nuit, composition_recommandee
    journal.py               log, prendre_instantane
    statistiques.py          statistiques(parties archivées) : victoires par camp, par taille de table, fiche par rôle
    bilan.py                 bilan_partie : chiffres clés, distinctions, frise (lit s["morts"])
    persistance.py           save_game/load_game/clear_save, archiver_partie, lister_historique,
                             date_partie, gagnant_partie
  ui/                        interface Streamlit
    styles.py                CSS (cartes, scènes, passage, accueil, historique) et décors SVG
    composants.py            carte_role, carte_dos, badges, scene_ciel/victoire, annonce, plaquette,
                             grille_dalles, selection_dalles, bouton_validation, bouton_fin, panneau_avis
    illustrations.py         svg_role(clé, classe, repli) : SVG en ligne d'un rôle (couleur = CSS `color`)
    sons.py                  musique_courante(s), effet_courant(s) ; jouer_musique / jouer_effet insèrent les lecteurs invisibles
    nuit_roles.py            une fonction de tour de nuit par rôle + NUIT_ROLES (clé de rôle -> fonction)
    barre_laterale.py        recharger_etape, panneau_rechargement, garder_sidebar_ouverte
    ecrans/                  accueil, installation, nuit, jour (réveil, maire, conseil, tir), fin
  app.py                     main() : CSS, barre latérale, aiguillage sur s["phase"], musique, menu Option
```

**Sens des dépendances** : `ui` -> `moteur` -> `roles` / `options` -> `config`. Le moteur n'importe jamais `streamlit` ni `ui` (c'est ce qui le rend testable). `roles.py` ne connaît pas l'interface : c'est pour cela que le tour de nuit d'un rôle est dans `NUIT_ROLES` (ui) et non dans la dataclass `Role`.

Streamlit relance le script d'entrée à chaque interaction ; les modules importés restent en cache. Tout l'état vit dans `st.session_state.partie` (le dictionnaire `s`), les saisies temporaires d'écran aussi (clés `sel_*`, `pick_*`, `reload_*`...).

### L'état de partie `s`

Créé par `nouvelle_partie`, sauvegardé dans `save.json` après chaque rendu (`save_game(s)` en fin de `main`), rechargé au démarrage (reprise automatique).

| Clé | Rôle |
|---|---|
| `joueurs` | `{nom: {"role", "vivant", "amoureux", ...}}` ; extras éventuels : `camp_choisi` (Chien-Loup), `enfant_sauvage` |
| `phase` | `nuit`, `reveil`, `election_maire`, `conseil`, `tir_chasseur`, `fin` |
| `jour` | 0 = première nuit (Cupidon seulement, pas de mort) ; 1, 2... ensuite |
| `ordre_nuit`, `tour`, `devoile`, `transfert` | déroulé du passage de l'appareil en nuit |
| `votes_loups`, `morts_nuit`, `morts_tir`, `tirs_en_attente`, `retour_tir` | résolution de nuit et tirs du chasseur |
| `amoureux`, `maire`, `dernier_maire`, `loups`, `cartes_milieu` | état social |
| `options` | options de partie (voir §4) |
| clés propres aux rôles | viennent de `Role.etat_initial` (ex. `potions_sorciere`, `protege_nuit`, `mentor_enfant`, `cible_loup_blanc`) |
| `morts`, `composition` | `morts` : une entrée par mort (nom, role, camp, genre, jour, moment) alimentée par `tuer(..., genre)` ; `composition` : le paquet, pour « Rejouer » et le rappel des règles |
| `journal`, `instantanes` | historique daté par moment, points de retour pour le rechargement d'étape |

### Registre des rôles

`Role` (dataclass figée) : `key, nom, emoji, degrade, camp ("village" | "loups"), unique, etat_initial, cartes_en_plus, recommande, tir_a_la_mort, solitaire, camp_secret, priorite_nuit, categorie, lot, description`. `categorie` range le rôle dans l'écran de composition (clés de `CATEGORIES` : info, pouvoir, chaos, loups ; un test exige qu'elle soit connue). Rôles actuels : loup, villageois, sorciere, voyante, cupidon, chasseur, salvateur, enfant_sauvage, voleur, renard, loup_blanc, chien_loup, louveteau, soeur, frere, servante, juge_begue, montreur_ours, petite_fille, corbeau, idiot, bouc_emissaire. `lot` = nombre de cartes ajoutées quand la case est cochée (sœurs 2, frères 3) ; les mesures d'équilibre de chaque rôle (impact, information, chaos) sont dans `assets/equilibre.json`, produit par `outils/simuler_equilibre.py` (un test exige une entrée par rôle ; ne pas éditer à la main).

**Ajouter un rôle** :
1. déclarer l'entrée dans `ROLES` (`roles.py`), avec ses clés d'état dans `etat_initial` ;
2. écrire `_nuit_<role>(s, nom, cle)` dans `ui/nuit_roles.py` et l'ajouter à `NUIT_ROLES` (un rôle absent dort comme un villageois) ;
3. si le rôle change les morts ou la victoire : `moteur/partie.py` (`tuer`, `resoudre_nuit`, `vainqueur`) ;
4. si le rôle a des réglages : `OPTIONS_DEFAUT` et `saisir_options` (écran d'installation) ;
5. mettre à jour le tableau des rôles et les règles du README.

### Briques d'interface

- `grille_dalles(theme, cle, choix, selection)` et `selection_dalles(theme, cle, choix, k)` : dalles cliquables. Chaque `theme` a son style CSS via la classe `st-key-dalles_<theme>_...` (themes existants : voy, loup, cupi, salv, mentor, flair, lb, poison, vote, maire, tir). Un nouveau thème = une entrée dans `styles.py`.
- `bouton_validation(libelle, cle, disabled=False)` valide une étape ; `bouton_fin(s, cle)` termine le tour d'un joueur de nuit ; les clés de boutons de nuit contiennent `jour` et `tour` pour rester uniques.
- **Dalles en fragment** : `selection_et_validation(theme, cle, choix, k, libelle, libelle_vide, cle_bouton)` joue sélection et validation dans un `st.fragment` (les clics sur les dalles ne relancent pas la page) et renvoie la sélection validée, sinon None. `grille_dalles` seule sert aux clics immédiats (tir, poison, salvateur).
- **Installation en 4 étapes** (`config_etape` : table, roles, options, noms) : tous les réglages vivent sous des clés de session hors widget ou conservées par `_conserver()` (un widget non affiché perd son état, réaffecter la clé le garde) ; `composition_courante()` les lit ; bandeau `barre_fixe` en bas. Les commandes sur mesure sont `compteur` (boutons ronds) et `choix_segmente` ; la couleur d'accent de Streamlit est fixée par `primaryColor` dans `.streamlit/config.toml`.
- `st.container(key="x")` donne la classe CSS `st-key-x` : c'est le crochet de style privilégié.
- Après toute mutation de `s` qui doit changer l'écran : `st.rerun()`.

## 3. Règles de jeu décidées (à ne pas casser)

- **Première nuit (`jour` 0)** : seul Cupidon agit ; les loups se découvrent mais personne n'est dévoré ; pas de vote le premier jour. Le Renard ne flaire pas la nuit 0.
- **Ordre de nuit** par `priorite_nuit` : Voleur (0), Chien-Loup (1), puis les autres (2) dans l'ordre des joueurs.
- **Loups en désaccord** (égalité des votes) : personne n'est dévoré. Les loups peuvent désigner n'importe quel autre vivant, y compris l'un des leurs.
- **Couple tiré au sort** (`couple_hasard`) : Cupidon est remplacé par un villageois (case grisée à la composition) ; la voyante peut, une fois (`voyante_a_vu_couple`), découvrir le couple au lieu de sonder un rôle.
- **Sorcière à l'aveugle** : elle ne sait pas qui est la victime. Potion de soin sauve du festin des loups ; le poison et le festin du Loup Blanc échappent au soin et au Salvateur.
- **Maire** : élu au premier jour ; s'il meurt, il désigne lui-même son successeur.
- **Égalité loups / village** : la partie continue tant que le maire n'est pas un loup ; option `maire_depart` désactivée = les loups gagnent dès l'égalité.
- **Amoureux** : meurent ensemble. Couple mixte loup + villageois = camp à part : ni village ni meute ne peut gagner tant qu'il vit ; il gagne s'il est le dernier groupe vivant (2 joueurs, 3 en trouple).
- **Solitaire** (Loup Blanc) : ne gagne qu'en restant seul ; bloque les victoires des autres tant qu'il vit.
- **Camp secret** (Chien-Loup) : son camp n'est dévoilé qu'à la fin.
- **Louveteau** : sa mort pose `s["double_victime"]` ; la nuit suivante les loups désignent 2 victimes (`victimes_loups`), la potion ne sauve que la plus désignée.
- **Servante dévouée** : la nuit suivant un vote, elle peut reprendre le rôle d'un condamné de la veille (`condamnes`, `enregistrer_condamne`, `condamnes_de_la_veille`, `servante_prend_role`) ; `s["servante_nuit"]` fait annoncer l'intervention sur le panneau du réveil, puis est remis à zéro au début de la nuit suivante.
- **Montreur d'ours** : `ours_grogne(s)` (voisins vivants dans l'ordre des noms) ; annoncé au panneau du réveil. **Corbeau** : `corbeau_cible` (+2 voix annoncées au réveil et au vote, remis à zéro au début de la nuit suivante). **Petite Fille** : joue après les loups (`priorite_nuit` 3), 1 chance sur 3 de `petite_fille_surprise` (dévorée, rien ne la sauve). **Idiot** : `epargner_idiot` (une fois, puis `vote_perdu`). **Bouc émissaire** : bouton « Égalité des voix » au vote.
- **Juge bègue** : active `second_vote = jour` pendant sa nuit (une fois, `juge_utilise`) ; le conseil du même `jour` enchaîne un second vote.
- **Enfant sauvage** : devient loup à la mort de son mentor.
- **Chasseur** : tir à la mort, ou renonce ; géré par la phase `tir_chasseur` et `tirs_en_attente`.

## 4. Système d'options

`OPTIONS_DEFAUT` (`options.py`) : `potions_sorciere`, `potions_mort`, `couple_hasard`, `trouple`, `cadence_voyante`, `cadence_loup_blanc`, `maire_depart`, `voyante_couple`. Toujours lire via `opt(s, "cle")` : les anciennes sauvegardes n'ont pas de clé `options`, `opt` retombe sur le défaut. À l'installation (étape Options, cartes centrées `carte_option`), les réglages d'un rôle absent restent visibles mais grisés. Ajouter une option : `OPTIONS_DEFAUT`, `OPTIONS_SESSION` et `CLES_OPTIONS` dans `installation.py`, une commande dans `etape_options`, et `opt(s, ...)` dans les règles (les anciennes sauvegardes retombent sur le défaut). `couple_hasard` remplace Cupidon par un villageois ; `trouple` est le mode « fun » (amour à trois).

## 5. Historique, sauvegarde et rechargement

- **Reprise** : l'app ne reprend plus la partie sauvegardée toute seule ; `ecran_accueil` la résume (`resume_sauvegarde`) et propose « Reprendre » (confirmation avant de la remplacer).
- **Préférences** : `preferences.json` (`load_preferences` / `maj_preferences`) garde le son (`son`) et la dernière composition (`composition`). Le son reste désactivé tant qu'on ne l'a pas activé une fois.

- **Migrations** : l'état `s` porte une `version` ; `moteur/migrations.py` met à niveau les anciennes sauvegardes (et leurs instantanés). **Toute clé obligatoire ajoutée à l'état exige une migration** (incrémenter `VERSION`, ajouter une fonction à `MIGRATIONS`) et un test. `load_game` met de côté (`save.json.corrompue`, `.invalide`, `.plus_recente`) un fichier inutilisable au lieu de planter ; `save_game` écrit puis remplace (jamais de fichier tronqué).

- `save.json` (ignoré par git) : partie en cours, reprise automatique.
- `historique/partie_AAAAMMJJ_HHMMSS.json` : archive écrite à la fin de la partie, **versionnée dans le dépôt**. Les parties abandonnées ne sont pas conservées.
- `log(s, texte, moment)` journalise ; `prendre_instantane(s, "nuit" | "jour")` crée un point de retour utilisé par « Recharger une étape » (menu Option).

## 6. Façon de travailler

- **Une branche + une PR par changement** (`feat/...`, `fix/...`, `refactor/...`, `docs/...`), titre explicite, corps avec sections « Résumé » et « À tester ». C'est l'utilisateur qui fusionne.
- Ne pousser que le compte **Tcathelineau**.
- **Ne jamais ajouter au commit** `.DS_Store` ni les fichiers `historique/partie_*.json` laissés par les parties de test de l'utilisateur ; ajouter les fichiers par nom, pas `git add -A`.
- Réponses à l'utilisateur en **français**, concises ; prose sans tiret cadratin ni flèche.
- Commits : trailer `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`.
- **Son pendant les tests** : le laisser désactivé (c'est le défaut) ; l'utilisateur travaille en open space.
- Tests : l'utilisateur teste lui-même l'interface dans son navigateur ; ne pas lancer de test navigateur pour chaque PR (coût en tokens). Vérifier par `pyflakes`, import des modules et, pour le moteur, des tests unitaires ; une partie complète peut se jouer sans navigateur avec `streamlit.testing.v1.AppTest` (limites : `st.rerun` après un formulaire laisse l'arbre périmé, `selectbox(index=None)` ne se pilote pas : injecter la valeur dans `session_state`).
- Pièges déjà rencontrés : `sed -i` se comporte autrement sur macOS (préférer un remplacement Python) ; un script d'édition doit échouer bruyamment si une ancre est introuvable ; `location.reload()` en JS demande un `setTimeout` ; l'aperçu du navigateur peut avoir un viewport 0x0 ; après un test, tuer le serveur (`pkill -f "streamlit run"`) et supprimer le `save.json` généré.

- **Fichiers locaux** : `joueurs.json` (noms de la dernière partie, ignoré par git, préremplis à l'installation).
- **Assets générés** : ne pas éditer à la main `assets/roles`, `assets/sons`, `assets/favicon.png` ; modifier `outils/importer_icones.py`, `importer_musiques.py`, `generer_sons.py`, `generer_favicon.py` et les relancer (la licence CC BY 3.0 impose de garder `CREDITS.md` à jour : le script le réécrit). Un nouveau rôle sans icône retombe sur son emoji, mais un test exige une icône par rôle.
- **Son** : deux lecteurs dans les conteneurs réservés `zone_musique` et `zone_effet` (premiers éléments de la barre latérale, masqués par CSS) pour que leur position ne change pas et que le son en cours ne soit pas relancé à chaque clic. Musique par phase (nuit, jour, conseil ; le conseil commence dès le réveil s'il y a des morts), gong grave quand un innocent meurt (`mort_gentil`), hurlement à la première révélation d'une carte de loup (`cri_loup` sur le joueur, marqué par `marquer_cri` seulement s'il est joué) et à la victoire des loups, ovation à la victoire du village ;  réglages `musique_on`, `sons_on`, `cri_on` **désactivés par défaut** (rien ne doit jouer à l'arrivée sur la page), activés par des cases du menu Option (`cases_a_cocher`, widgets `case_<réglage>` recopiés vers le réglage pour survivre à la fermeture du menu ; `vider_session` garde ces réglages).

## 7. Chantiers connus

- **Parties célèbres (presets)** : proposer à l'installation des compositions inspirées de parties médiatisées, avec un court résumé du contexte. Retenus : Classique Thiercelieux, Canal+ saison 1 (2024, 13 joueurs, 3 loups), Canal+ saison 2 (2025, 3 loups, Cupidon, Montreur d'ours, Capitaine), Squeezie Minecraft (2020, plugin LoupGarou). Écartés : Wankil, film Netflix. À reprendre une fois les rôles manquants importés.
- **Rôles à importer** : Petite Fille, Montreur d'ours, Corbeau, Détective, Ange, Assassin, Pyromane. Autres idées étudiées (barème dans `docs/equilibre-roles.md`) : Idiot du village, Bouc émissaire, Ancien, Grand méchant loup, Infect père des loups, Chevalier à l'épée rouillée, Joueur de flûte, Comédien.
- Vérifier toute affirmation sur ces parties médiatisées (compositions, dates, règles) à la source avant de l'écrire dans le jeu ou le README.
