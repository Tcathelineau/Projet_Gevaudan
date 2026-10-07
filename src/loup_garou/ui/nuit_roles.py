"""Tour de nuit de chaque rôle : ce que voit et choisit le joueur appelé."""

import random

import streamlit as st

from loup_garou.moteur.journal import log
from loup_garou.moteur.partie import camp, condamnes_de_la_veille, fin_de_tour, servante_prend_role, vivants
from loup_garou.options import nuit_active, opt, prochaine_nuit, taille_couple
from loup_garou.roles import ROLES
from loup_garou.ui.composants import (
    badge_meute,
    bouton_fin,
    grille_dalles,
    plaquette,
    selection_et_validation,
)


def _afficher_meute(s, nom):
    if s["joueurs"][nom].get("enfant_sauvage"):
        plaquette("Ton mentor est mort : tu as rejoint la meute.", icone="🐾")
    complices = [l for l in s["loups"] if l != nom and s["joueurs"][l]["vivant"]]
    with st.sidebar:  # comme le badge des amoureux : le rappel de la meute reste dans le menu de gauche
        badge_meute(nom, complices)


def _cibles_loups(s, nom):
    """Tous les vivants sauf soi : la meute peut aussi se voter elle-même (sacrifice, bluff)."""
    return [n for n in vivants(s) if n != nom]


def _vote_loups(s, nom, cle, cibles):
    """Grille de vote de la meute. Renvoie True quand la victime vient d'être désignée."""
    k = min(2, len(cibles)) if s.get("double_victime") else 1
    if k == 1:
        st.markdown("**Qui dévorez-vous ?**")
    else:
        st.markdown(f"**Qui dévorez-vous ? Le Louveteau est mort : désignez {k} victimes.**")
    choix = selection_et_validation("loup", cle, cibles, k, "🐺 Dévorer {sel}", "🐺 Dévorer", f"devorer_{cle}")
    if choix:
        s["votes_loups"] += choix
        log(s, f"{nom} ({ROLES[s['joueurs'][nom]['role']].nom}) désigne {' et '.join(choix)}.")
        st.session_state.pop(f"sel_loup_{cle}", None)
        return True
    return False


def _nuit_loup(s, nom, cle):
    _afficher_meute(s, nom)
    cibles = _cibles_loups(s, nom)
    if s["jour"] == 0:
        plaquette("Première nuit : vous vous découvrez, personne ne meurt encore.", icone="🐾")
        bouton_fin(s, cle)
    elif not cibles:
        plaquette("Plus personne à dévorer.", icone="🐾")
        bouton_fin(s, cle)
    elif _vote_loups(s, nom, cle, cibles):
        fin_de_tour(s)
        st.rerun()


def _nuit_loup_blanc(s, nom, cle):
    """Vote avec la meute, puis une nuit sur deux (nuits impaires) il peut dévorer l'un des siens."""
    _afficher_meute(s, nom)
    if s["jour"] == 0:
        plaquette("Première nuit : vous vous découvrez, personne ne meurt encore.", icone="🐾")
        bouton_fin(s, cle)
        return

    cibles = _cibles_loups(s, nom)
    if cibles and s.get("vote_loup_blanc") != cle:
        if _vote_loups(s, nom, cle, cibles):
            s["vote_loup_blanc"] = cle
            st.rerun()
        return

    freres = [n for n in vivants(s) if n != nom and camp(s, n) == "loups"]
    if not freres:
        plaquette("Tu es le dernier loup : plus aucun frère à dévorer.", icone="🌕")
        bouton_fin(s, cle)
    elif not nuit_active(s, opt(s, "cadence_loup_blanc")):
        plaquette(
            f"Pas de festin cette nuit. Prochain festin : nuit {prochaine_nuit(s, opt(s, 'cadence_loup_blanc'))}.",
            icone="🌕",
        )
        bouton_fin(s, cle)
    else:
        st.markdown("**Un de tes frères est-il de trop ?**")
        st.caption("Tu gagnes seul : élimine le village, puis la meute. Tu peux aussi les épargner cette nuit.")
        cible = grille_dalles("lb", cle, freres)
        epargne = st.button("Épargner la meute", key=f"lb_epargne_{cle}")
        if cible:
            s["cible_loup_blanc"] = cible
            log(s, f"Le Loup Blanc {nom} dévore {cible}.")
        elif epargne:
            log(s, f"Le Loup Blanc {nom} épargne la meute.")
        if cible or epargne:
            fin_de_tour(s)
            st.rerun()


def _nuit_chien_loup(s, nom, cle):
    """Première nuit : choix définitif du camp ; ensuite il agit comme un loup ou comme un villageois."""
    choix = s["joueurs"][nom].get("camp_choisi")
    if choix is None:
        st.markdown("**Que choisis-tu d'être ?**")
        st.caption("Choix définitif : tu gagnes avec ce camp. Les autres ne le sauront qu'à la fin de la partie.")
        col1, col2 = st.columns(2)
        villageois = col1.button("🧑‍🌾 Simple Villageois", use_container_width=True, key=f"chien_vil_{cle}")
        loup = col2.button("🐺 Loup-Garou", use_container_width=True, key=f"chien_loup_{cle}")
        if villageois or loup:
            s["joueurs"][nom]["camp_choisi"] = "loups" if loup else "village"
            log(s, f"Le Chien-Loup {nom} choisit d'être {'Loup-Garou' if loup else 'simple Villageois'}.")
            if loup:
                s["loups"].append(nom)
            st.rerun()
    elif choix == "loups":
        _nuit_loup(s, nom, cle)
    else:
        plaquette("Tu as choisi d'être simple Villageois. Dors.", icone="🐕")
        bouton_fin(s, cle)


def _nuit_renard(s, nom, cle):
    """Chaque nuit où il a encore du flair : il flaire 3 personnes et apprend si un loup s'y trouve."""
    if s["jour"] == 0:
        plaquette("Première nuit : ton flair ne s'éveille qu'à la nuit prochaine.", icone="🦊")
        bouton_fin(s, cle)
        return

    resultat = s.get("resultat_renard")
    if resultat and resultat["cle"] == cle:
        if resultat["loup"]:
            plaquette("Un Loup-Garou se cache dans ce groupe. Tu gardes ton flair : à la nuit prochaine.",
                      icone="🦊", ton="succes")
        else:
            plaquette("Aucun Loup-Garou dans ce groupe. Tu perds ton flair et deviens simple Villageois.",
                      icone="🦊")
        st.caption("Groupe flairé : " + ", ".join(resultat["groupe"]))
        if st.button("Terminer mon tour", type="primary", key=f"fin_{cle}"):
            if not resultat["loup"]:
                s["joueurs"][nom]["role"] = "villageois"
                s["joueurs"][nom]["renard"] = True
                log(s, f"{nom} (Renard) devient simple Villageois.")
            fin_de_tour(s)
            st.rerun()
        return

    candidats = [n for n in vivants(s) if n != nom]
    k = min(3, len(candidats))
    st.markdown(f"**Flaire {k} personnes**")
    groupe = selection_et_validation("flair", cle, candidats, k, "Flairer", "Flairer", f"flairer_{cle}")
    if groupe:
        loup = any(camp(s, n) == "loups" for n in groupe)
        log(s, f"Le renard {nom} flaire {', '.join(groupe)} : "
               + ("un loup-garou s'y trouve." if loup else "aucun loup-garou, il perd son flair."))
        s["resultat_renard"] = {"cle": cle, "groupe": groupe, "loup": loup}
        st.rerun()


def _nuit_voyante(s, nom, cle):
    """La voyante a une vision toutes les N nuits (option de partie) : pas de stock à épuiser.
    Quand le couple est tiré au sort (pas de Cupidon), elle peut, une fois, apprendre qui sont les amoureux
    au lieu de sonder un rôle."""
    deja_vu = st.session_state.get(f"vu_{cle}")
    couple_vu = st.session_state.get(f"couple_vu_{cle}")
    peut_voir = nuit_active(s, opt(s, "cadence_voyante"))

    if deja_vu:
        role_vu = s["joueurs"][deja_vu]["role"]
        plaquette(f"{deja_vu} est {ROLES[role_vu].nom.upper()}.", icone="🔮", ton="succes")
        bouton_fin(s, cle)
    elif couple_vu:
        plaquette(f"Les amoureux sont {' et '.join(s['amoureux'])}.", icone="💘", ton="succes")
        bouton_fin(s, cle)
    elif not peut_voir:
        plaquette(
            f"Pas de vision cette nuit. Prochaine vision : nuit {prochaine_nuit(s, opt(s, 'cadence_voyante'))}.",
            icone="🌙",
        )
        bouton_fin(s, cle)
    else:
        peut_couple = bool(
            opt(s, "couple_hasard") and opt(s, "voyante_couple") and s["amoureux"] and not s.get("voyante_a_vu_couple")
        )
        cle_mode = f"voy_mode_{cle}"
        if peut_couple and st.session_state.get(cle_mode) is None:
            st.markdown("**Que veux-tu voir cette nuit ?**")
            st.caption("Le couple a été tiré au sort : tu peux apprendre qui il forme (une seule fois), ou sonder un rôle.")
            col_role, col_couple = st.columns(2)
            if col_role.button("🔮 Deviner un rôle", use_container_width=True, key=f"voy_role_{cle}"):
                st.session_state[cle_mode] = "role"
                st.rerun()
            if col_couple.button("💘 Découvrir le couple", use_container_width=True, key=f"voy_couple_{cle}"):
                s["voyante_a_vu_couple"] = True
                log(s, f"La voyante {nom} découvre le couple : {' et '.join(s['amoureux'])}.")
                st.session_state[f"couple_vu_{cle}"] = True
                st.rerun()
            return
        if peut_couple and st.button("← Autre choix", key=f"voy_retour_{cle}"):
            st.session_state.pop(cle_mode, None)
            st.rerun()
        candidats = [n for n in vivants(s) if n != nom]
        choix = selection_et_validation("voy", cle, candidats, 1, "🔮 Sonder {sel}", "🔮 Sonder", f"sonder_{cle}")
        if choix:
            vu = choix[0]
            log(s, f"La voyante {nom} sonde {vu} : {ROLES[s['joueurs'][vu]['role']].nom}.")
            st.session_state[f"vu_{cle}"] = vu
            st.rerun()


def _nuit_sorciere(s, nom, cle):
    def reste_a_faire():
        return (s["potions_sorciere"] > 0 and not s["soin_sorciere"]) or (
            s.get("potions_mort_sorciere", 0) > 0 and not s.get("cible_poison"))

    if s["jour"] == 0 or not reste_a_faire():
        plaquette("Rien à faire cette nuit.", icone="🌙")
        bouton_fin(s, cle)
        return

    soin = s["potions_sorciere"]
    mort = s.get("potions_mort_sorciere", 0)
    fioles = "🧪" * soin + "☠️" * mort
    detail = " · ".join(filter(None, (
        f"{soin} potion{'s' if soin > 1 else ''} de soin" if soin else "",
        f"{mort} potion{'s' if mort > 1 else ''} de mort" if mort else "",
    )))
    st.markdown(
        f'<div class="potion-bandeau"><span class="potion-fioles">{fioles}</span>'
        f'<span class="potion-texte">Il te reste : {detail}</span></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get(f"poison_{cle}"):
        st.markdown("**Qui empoisonnes-tu ?**")
        cible = grille_dalles("poison", cle, [n for n in vivants(s) if n != nom])
        if st.button("Annuler", key=f"annule_poison_{cle}"):
            st.session_state.pop(f"poison_{cle}", None)
            st.rerun()
        if cible:
            s["cible_poison"] = cible
            s["potions_mort_sorciere"] -= 1
            log(s, f"La sorcière {nom} empoisonne {cible}.")
            st.session_state.pop(f"poison_{cle}", None)
            if not reste_a_faire():
                fin_de_tour(s)
            st.rerun()
        return

    peut_soigner = soin > 0 and not s["soin_sorciere"]
    peut_empoisonner = mort > 0 and not s.get("cible_poison")
    utilise = s["soin_sorciere"] or bool(s.get("cible_poison"))
    with st.container(key="sorciere_boutons", horizontal=True, horizontal_alignment="center"):
        soigne = peut_soigner and st.button(
            "Utiliser une potion de soin", type="primary", key=f"soin_{cle}")
        empoisonne = peut_empoisonner and st.button(
            "Empoisonner quelqu'un", type="secondary" if peut_soigner else "primary", key=f"empoisonne_{cle}")
        fin = st.button("Terminer mon tour" if utilise else "Ne rien faire", key=f"rien_{cle}")
    if soigne:
        s["soin_sorciere"] = True
        s["potions_sorciere"] -= 1
        log(s, f"La sorcière {nom} utilise une potion de soin.")
        if not reste_a_faire():
            fin_de_tour(s)
        st.rerun()
    if empoisonne:
        st.session_state[f"poison_{cle}"] = True
        st.rerun()
    if fin:
        if not utilise:
            log(s, f"La sorcière {nom} n'utilise aucune potion.")
        fin_de_tour(s)
        st.rerun()


def _nuit_cupidon(s, nom, cle):
    if s["jour"] > 0:
        plaquette("Ton travail est fait. Dors.", icone="🏹")
        bouton_fin(s, cle)
    else:
        st.markdown("**Qui lies-tu par l'amour ?**")
        k = taille_couple(s)
        st.caption(f"Choisis {'trois' if k == 3 else 'deux'} joueurs (toi compris).")
        couple = selection_et_validation(
            "cupi", cle, list(s["joueurs"].keys()), k, "Décocher la flèche", "Décocher la flèche", f"ok_cup_{cle}",
        )
        if couple:
            s["amoureux"] = couple
            log(s, f"Cupidon {nom} lie {', '.join(couple[:-1])} et {couple[-1]}.")
            for n in couple:
                s["joueurs"][n]["amoureux"] = True
            fin_de_tour(s)
            st.rerun()


def _nuit_salvateur(s, nom, cle):
    if s["jour"] == 0:
        plaquette("Première nuit : personne ne meurt, rien à protéger.", icone="🛡️")
        bouton_fin(s, cle)
        return

    precedent = s.get("protege_precedent")
    st.markdown("**Qui protèges-tu cette nuit ?**")
    if precedent and s["joueurs"][precedent]["vivant"]:
        st.caption(f"Tu ne peux pas protéger {precedent} deux nuits de suite.")
    protege = grille_dalles("salv", cle, [n for n in vivants(s) if n != precedent])
    if protege:
        log(s, f"Le salvateur {nom} protège {protege}.")
        s["protege_nuit"] = protege
        fin_de_tour(s)
        st.rerun()


def _nuit_enfant_sauvage(s, nom, cle):
    mentor = s.get("mentor_enfant")
    if mentor is None:
        st.markdown("**Choisis ton mentor**")
        st.caption("Il ignorera son rôle. S'il meurt, tu deviens loup-garou.")
        choix = grille_dalles("mentor", cle, [n for n in vivants(s) if n != nom])
        if choix:
            log(s, f"{nom} (Enfant sauvage) choisit {choix} comme mentor.")
            s["mentor_enfant"] = choix
            st.rerun()
    else:
        plaquette(f"Ton mentor est {mentor}. S'il meurt, tu deviens loup-garou.", icone="🐾")
        bouton_fin(s, cle)


def _nuit_voleur(s, nom, cle):
    """Première nuit : le voleur prend l'un des deux rôles du milieu, ou reste simple villageois."""
    milieu = s["cartes_milieu"]
    st.markdown("**Deux cartes sont restées au milieu**")
    st.caption("Choisis-en une pour en prendre le rôle, ou garde ton sort : tu seras alors simple Villageois.")

    nouveau_role = None
    garde = False
    with st.container(key=f"dalles_vol_{cle}"):
        cols = st.columns(2)
        for i, role in enumerate(milieu):
            with cols[i % 2]:
                if st.button(
                    f"{ROLES[role].emoji} {ROLES[role].nom}",
                    key=f"pick_vol_{cle}_{i}", use_container_width=True,
                ):
                    nouveau_role = role
    if st.button("Garder mon rôle (Villageois)", key=f"vol_garde_{cle}"):
        nouveau_role = "villageois"
        garde = True

    if nouveau_role:
        if garde:
            log(s, f"{nom} (Voleur) garde son sort et devient simple Villageois.")
        else:
            log(s, f"{nom} (Voleur) prend la carte {ROLES[nouveau_role].nom}.")
        s["joueurs"][nom]["role"] = nouveau_role
        s["joueurs"][nom]["voleur"] = True
        if ROLES[nouveau_role].camp == "loups":
            s["loups"].append(nom)
        s["cartes_milieu"] = []
        st.rerun()


def _nuit_louveteau(s, nom, cle):
    plaquette("Tu es le Louveteau : si tu meurs, la meute dévorera deux victimes la nuit suivante.", icone="🐶")
    _nuit_loup(s, nom, cle)


FRATRIE = {"soeur": ("Ta sœur", "Tes sœurs"), "frere": ("Ton frère", "Tes frères")}


def _nuit_fratrie(s, nom, cle):
    """Sœurs et frères se reconnaissent ; ils n'ont pas d'autre pouvoir."""
    role = s["joueurs"][nom]["role"]
    groupe = [n for n, d in s["joueurs"].items() if d["role"] == role]
    proches = [n for n in groupe if n != nom]
    singulier, pluriel = FRATRIE[role]
    if not proches:
        plaquette("Les autres cartes de ta fratrie sont restées au milieu de la table : tu es seul.", icone=ROLES[role].emoji)
    else:
        liste = ", ".join(n if s["joueurs"][n]["vivant"] else f"{n} (mort)" for n in proches)
        plaquette(f"{singulier if len(proches) == 1 else pluriel} : {liste}.", icone=ROLES[role].emoji, ton="succes")
    bouton_fin(s, cle)


def _nuit_servante(s, nom, cle):
    """Après un vote, la servante peut reprendre en secret le rôle du condamné ; le panneau l'annoncera au réveil."""
    condamnes = condamnes_de_la_veille(s)
    if not condamnes:
        plaquette(
            "Tu es la servante dévouée : la nuit qui suit un vote, tu peux reprendre le rôle du condamné. "
            "Personne n'a été condamné hier : dors.", icone="🧹",
        )
        bouton_fin(s, cle)
        return

    st.markdown("**Reprends-tu le rôle d'un condamné ?**")
    st.caption("Tu découvriras sa carte tout de suite. Le village apprendra demain que tu es intervenue.")
    choix = grille_dalles("serv", cle, condamnes)
    if st.button("Ne rien faire", key=f"servante_rien_{cle}"):
        fin_de_tour(s)
        st.rerun()
    if choix:
        servante_prend_role(s, nom, choix)
        st.rerun()


def _nuit_juge_begue(s, nom, cle):
    """Une fois par partie, le juge exige un second vote lors du prochain conseil."""
    if s["jour"] == 0:
        plaquette("Pas de vote demain : garde ton pouvoir pour plus tard.", icone="⚖️")
        bouton_fin(s, cle)
    elif s.get("juge_utilise"):
        plaquette("Tu as déjà exigé ton second vote. Dors.", icone="⚖️")
        bouton_fin(s, cle)
    else:
        st.markdown("**Exiges-tu un second vote demain ?**")
        st.caption("Une seule fois par partie : après le premier vote, le village en tient aussitôt un second.")
        with st.container(key="juge_boutons", horizontal=True, horizontal_alignment="center"):
            exige = st.button("⚖️ Exiger un second vote", type="primary", key=f"juge_oui_{cle}")
            garde = st.button("Garder mon pouvoir", key=f"juge_non_{cle}")
        if exige:
            s["juge_utilise"] = True
            s["second_vote"] = s["jour"]
            log(s, f"Le juge bègue {nom} exige un second vote au prochain conseil.")
        if exige or garde:
            fin_de_tour(s)
            st.rerun()


def _nuit_montreur_ours(s, nom, cle):
    plaquette(
        "Tu es le Montreur d'ours : chaque matin, ton ours grogne si l'un de tes deux voisins vivants "
        "est un loup-garou. Dors.", icone="🐻",
    )
    bouton_fin(s, cle)


def _nuit_idiot(s, nom, cle):
    plaquette(
        "Tu es l'idiot du village : si le village te condamne, tu révèles ton rôle et tu survis, "
        "mais tu ne votes plus. Dors.", icone="🤡",
    )
    bouton_fin(s, cle)


def _nuit_bouc_emissaire(s, nom, cle):
    plaquette("Tu es le bouc émissaire : en cas d'égalité des voix au vote du village, c'est toi qui es condamné. Dors.",
              icone="🐐")
    bouton_fin(s, cle)


def _nuit_corbeau(s, nom, cle):
    """Chaque nuit, le corbeau désigne un joueur qui recevra deux voix de plus au prochain vote du village."""
    if s["jour"] == 0:
        plaquette("Pas de vote demain : le corbeau attend la nuit prochaine.", icone="🐦")
        bouton_fin(s, cle)
        return
    st.markdown("**Qui le corbeau désigne-t-il ?**")
    st.caption("Il recevra deux voix de plus au prochain vote du village. Le village saura qui est désigné, pas qui l'a fait.")
    choix = selection_et_validation(
        "corb", cle, [n for n in vivants(s) if n != nom], 1, "🐦 Désigner {sel}", "🐦 Désigner", f"corbeau_{cle}",
    )
    if choix:
        cible = choix[0]
        s["corbeau_cible"] = cible
        log(s, f"Le corbeau {nom} désigne {cible} : deux voix de plus contre lui au prochain vote.")
        st.session_state.pop(f"sel_corb_{cle}", None)
        fin_de_tour(s)
        st.rerun()
    if st.button("Ne désigner personne", key=f"corbeau_rien_{cle}"):
        log(s, f"Le corbeau {nom} ne désigne personne.")
        fin_de_tour(s)
        st.rerun()


def _nuit_petite_fille(s, nom, cle):
    """Elle joue après les loups : elle apprend qui ils ont désigné et reconnaît l'un d'eux, au risque d'être surprise."""
    if s["jour"] == 0:
        plaquette("Première nuit : les loups ne chassent pas encore, il n'y a rien à espionner.", icone="👧")
        bouton_fin(s, cle)
        return
    cle_resultat = f"pf_{cle}"
    resultat = st.session_state.get(cle_resultat)
    if resultat is None:
        st.markdown("**Espionner les loups ?**")
        st.caption("Tu apprends qui ils ont désigné et tu aperçois deux silhouettes, dont un loup. Risque : une chance sur trois d'être surprise "
                   "et dévorée à l'aube, sans que rien ne puisse te sauver.")
        col_espionne, col_dort = st.columns(2)
        if col_espionne.button("👁️ Espionner", type="primary", use_container_width=True, key=f"pf_espionne_{cle}"):
            loups = [n for n in vivants(s) if camp(s, n) == "loups" and n != nom]
            innocents = [n for n in vivants(s) if camp(s, n) != "loups" and n != nom]
            surprise = random.random() < 1 / 3
            silhouettes = None
            if loups:
                silhouettes = [random.choice(loups)] + ([random.choice(innocents)] if innocents else [])
                random.shuffle(silhouettes)
            resultat = {
                "surprise": surprise,
                "victimes": sorted(set(s.get("votes_loups", []))),
                "silhouettes": silhouettes,
            }
            st.session_state[cle_resultat] = resultat
            log(s, f"La petite fille {nom} espionne la meute" + (" et se fait surprendre." if surprise else "."))
            if surprise:
                s["petite_fille_surprise"] = nom
            st.rerun()
        if col_dort.button("Dormir", use_container_width=True, key=f"pf_dort_{cle}"):
            fin_de_tour(s)
            st.rerun()
        return
    victimes = " et ".join(resultat["victimes"]) or "personne (les loups ne s'accordent pas)"
    texte = f"Les loups ont désigné {victimes}."
    if resultat["silhouettes"]:
        texte += f" Tu as aperçu deux silhouettes dont l'une est un loup : {' et '.join(resultat['silhouettes'])}."
    plaquette(texte, icone="👁️", ton="succes")
    if resultat["surprise"]:
        plaquette("Mais un loup t'a vue : tu seras dévorée à l'aube.", icone="🩸", ton="danger")
    bouton_fin(s, cle)


def _nuit_chasseur(s, nom, cle):
    plaquette("Tu es le chasseur : si tu meurs, tu pourras tirer une dernière balle. Dors.", icone="🔫")
    bouton_fin(s, cle)


def _nuit_villageois(s, nom, cle):
    plaquette("Tu dors paisiblement.", icone="🌙")
    bouton_fin(s, cle)


# Tour de nuit de chaque rôle (clé de ROLES -> fonction de rendu) ; un rôle absent dort comme un villageois.
NUIT_ROLES = {
    "loup": _nuit_loup,
    "loup_blanc": _nuit_loup_blanc,
    "chien_loup": _nuit_chien_loup,
    "renard": _nuit_renard,
    "voyante": _nuit_voyante,
    "sorciere": _nuit_sorciere,
    "cupidon": _nuit_cupidon,
    "salvateur": _nuit_salvateur,
    "enfant_sauvage": _nuit_enfant_sauvage,
    "voleur": _nuit_voleur,
    "louveteau": _nuit_louveteau,
    "soeur": _nuit_fratrie,
    "frere": _nuit_fratrie,
    "servante": _nuit_servante,
    "juge_begue": _nuit_juge_begue,
    "montreur_ours": _nuit_montreur_ours,
    "idiot": _nuit_idiot,
    "bouc_emissaire": _nuit_bouc_emissaire,
    "corbeau": _nuit_corbeau,
    "petite_fille": _nuit_petite_fille,
    "chasseur": _nuit_chasseur,
    "villageois": _nuit_villageois,
}
