"""Une partie jouée dans un vrai navigateur : ce que les tests AppTest ne voient pas (CSS, fenêtres, fragments, rechargement)."""

import re

from playwright.sync_api import expect

from jeu import cliquer, creer_partie, nuit_complete, sans_defilement_horizontal, sans_erreur, attendre_calme

NB = 7


def _ouvrir_le_conseil_et_voter(page, loup):
    """Réveil, élection du maire, puis vote contre un innocent (le premier joueur qui n'est pas `loup`) : la partie continue."""
    expect(page.get_by_text("Le village se réveille")).to_be_visible()
    expect(page.get_by_text("Avis à la population")).to_be_visible()
    cliquer(page, page_bouton(page, "Ouvrir le conseil du village"))
    cliquer(page, '[class*="st-key-dalles_maire_"] button')
    cliquer(page, '[class*="st-key-validation_valider_maire"] button')
    tuiles = page.locator('[class*="st-key-dalles_vote_"] button')
    for i in range(tuiles.count()):
        if loup not in tuiles.nth(i).inner_text():
            tuiles.nth(i).click()
            break
    attendre_calme(page)
    cliquer(page, '[class*="st-key-validation_valider_vote"] button')
    expect(page.get_by_text("Sentence du village")).to_be_visible()


def page_bouton(page, texte):
    """Sélecteur CSS d'un bouton par son texte (les boutons de l'app n'ont pas tous une clé stable)."""
    page.get_by_role("button", name=texte).first.wait_for()
    return f'button:has-text("{texte}")'


def test_une_partie_de_bout_en_bout(serveur, page):
    creer_partie(page, serveur, NB)
    sans_erreur(page)
    assert page.locator("audio").count() == 0  # le son est désactivé par défaut

    # Nuit 0 : tout le monde passe ; le loup découvre sa meute dans une fenêtre qui se ferme pour de bon.
    fenetres = nuit_complete(page, NB, premiere_nuit=True)
    assert len(fenetres) == 1
    (loup, texte), = fenetres.items()
    assert re.search("dernier loup", texte, re.I) and "Tu chasses seul" in texte
    page.screenshot(path="tests_e2e/captures/01_fenetre_meute_fermee.png")

    # Premier jour sans vote, puis la nuit retombe.
    expect(page.get_by_text("Le village se réveille")).to_be_visible()
    cliquer(page, page_bouton(page, "Passer au premier conseil"))
    cliquer(page, page_bouton(page, "La nuit retombe"))

    # Nuit 1 : le loup dévore quelqu'un.
    fenetres = nuit_complete(page, NB, premiere_nuit=False)
    assert fenetres == {}  # la fenêtre de la meute ne se rouvre pas
    page.screenshot(path="tests_e2e/captures/02_reveil.png")

    # Jour 1 : avis du village, maire, vote contre un innocent, la nuit tombe.
    _ouvrir_le_conseil_et_voter(page, loup)
    page.screenshot(path="tests_e2e/captures/03_sentence.png")
    cliquer(page, page_bouton(page, "La nuit tombe"))
    expect(page.get_by_text(re.compile("Nuit 2 — joueur 1 sur"))).to_be_visible()
    sans_erreur(page)


def test_la_partie_se_reprend_apres_un_rechargement(serveur, page):
    creer_partie(page, serveur, NB)
    nuit_complete(page, NB, premiere_nuit=True)
    expect(page.get_by_text("Le village se réveille")).to_be_visible()
    page.reload(wait_until="domcontentloaded")
    cliquer(page, ".st-key-accueil_btn_reprendre button")
    expect(page.get_by_text("Le village se réveille")).to_be_visible()  # reprise exactement où l'on s'était arrêté
    sans_erreur(page)


def test_le_theme_sombre_et_l_accueil(serveur, page):
    page.goto(serveur, wait_until="domcontentloaded")
    expect(page.get_by_text("Projet Gévaudan")).to_be_visible()
    fond = page.evaluate("getComputedStyle(document.querySelector('.stApp')).backgroundColor")
    r, g, b = [int(x) for x in re.findall(r"\d+", fond)[:3]]
    assert max(r, g, b) < 80, fond  # thème sombre
    assert page.evaluate("document.documentElement.lang") == "fr"
    page.screenshot(path="tests_e2e/captures/00_accueil.png")


def test_pas_de_defilement_horizontal_sur_telephone(serveur, navigateur):
    contexte = navigateur.new_context(viewport={"width": 375, "height": 812}, is_mobile=True, locale="fr-FR")
    page = contexte.new_page()
    page.set_default_timeout(20_000)
    page.goto(serveur, wait_until="domcontentloaded")
    expect(page.get_by_text("Projet Gévaudan")).to_be_visible()
    assert sans_defilement_horizontal(page), "accueil"
    cliquer(page, ".st-key-accueil_btn_nouvelle button")
    assert sans_defilement_horizontal(page), "étape Table"
    cliquer(page, ".st-key-etape_suivant button")
    assert sans_defilement_horizontal(page), "étape Rôles"
    page.screenshot(path="tests_e2e/captures/04_mobile_roles.png")
    contexte.close()
