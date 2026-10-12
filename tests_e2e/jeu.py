"""Pilote d'une partie dans le navigateur : les mêmes gestes qu'un joueur, repérés par les clés de l'interface."""

from playwright.sync_api import Page, expect

NOMS = ["Alice", "Bastien", "Camille", "Dina", "Eliott", "Farah", "Gaspard"]


def sans_erreur(page: Page):
    """Aucun bloc d'exception Streamlit à l'écran."""
    assert page.locator('[data-testid="stException"]').count() == 0, page.locator('[data-testid="stException"]').first.inner_text()


def attendre_calme(page: Page):
    """Laisse Streamlit finir sa relance (l'indicateur d'exécution est masqué par le thème : on guette l'état des éléments)."""
    page.wait_for_timeout(350)
    page.wait_for_function("() => !document.querySelector('[data-stale=\"true\"]')", timeout=15_000)
    sans_erreur(page)


def cliquer(page: Page, selecteur: str):
    page.locator(selecteur).first.click()
    attendre_calme(page)


def creer_partie(page: Page, url: str, nb_joueurs: int = 7):
    """Accueil, puis l'assistant : table, rôles (tous décochés : loups et villageois seulement), options, noms."""
    page.goto(url, wait_until="domcontentloaded")
    cliquer(page, ".st-key-accueil_btn_nouvelle button")
    for _ in range(nb_joueurs - 7):
        cliquer(page, ".st-key-nb_joueurs_setup_plus button")
    cliquer(page, ".st-key-etape_suivant button")  # table -> rôles
    for case in page.locator('[data-testid="stCheckbox"]').all():
        if case.locator("input").is_checked():
            case.click()
            attendre_calme(page)
    cliquer(page, ".st-key-etape_suivant button")  # rôles -> options
    cliquer(page, ".st-key-etape_suivant button")  # options -> joueurs
    for i in range(nb_joueurs):
        page.get_by_label(f"Joueur {i + 1}", exact=True).fill(NOMS[i % len(NOMS)] + (str(i // len(NOMS) or "")))
    page.get_by_role("button", name="Distribuer les rôles").click()
    attendre_calme(page)


def finir_le_tour(page: Page):
    cliquer(page, '[class*="st-key-fin_"] button')


def nom_du_prochain(page: Page):
    """Nom lu sur le bouton « Je vais chercher X » de l'écran de passage."""
    return page.locator('[class*="st-key-validation_transfert_"] button').first.inner_text().replace("Je vais chercher ", "").strip()


def nuit_complete(page: Page, nb_joueurs: int, premiere_nuit: bool):
    """Joue toute une nuit sans pouvoirs spéciaux : chaque joueur passe, le loup désigne le premier de sa grille.
    Renvoie {nom: texte de la fenêtre qui s'est ouverte pour lui} (ici : seulement le loup, qui découvre la meute)."""
    fenetres = {}
    for _ in range(nb_joueurs):
        nom = nom_du_prochain(page)
        cliquer(page, '[class*="st-key-validation_transfert_"] button')
        cliquer(page, '[class*="st-key-validation_pret_"] button')
        expect(page.get_by_text("Ta carte")).to_be_visible()
        dialogue = page.locator('[data-testid="stDialog"]')
        if premiere_nuit and page.locator(".badge-meute").count():
            # Un loup qui découvre sa carte pour la première fois : la fenêtre de la meute doit s'ouvrir (le navigateur la peint avec retard).
            dialogue.first.wait_for(state="visible", timeout=10_000)
        if dialogue.count():
            fenetres[nom] = dialogue.first.inner_text()
            fond = page.evaluate("getComputedStyle(document.querySelector('[data-testid=\"stDialog\"] > div')).backgroundImage")
            assert "gradient" in fond, f"la fenêtre n'a pas son fond (CSS non appliqué) : {fond}"  # régression Streamlit 1.65
            page.screenshot(path="tests_e2e/captures/00_fenetre_meute.png")
            dialogue.get_by_role("button", name="Compris").click()
            expect(dialogue).to_have_count(0)  # « Compris » ferme pour de bon
            attendre_calme(page)
        if not premiere_nuit and page.locator('[class*="st-key-dalles_loup_"] button').count():
            cliquer(page, '[class*="st-key-dalles_loup_"] button')
            cliquer(page, '[class*="st-key-validation_devorer_"] button')
        else:
            finir_le_tour(page)
    return fenetres


def sans_defilement_horizontal(page: Page):
    return page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
