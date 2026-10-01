from loup_garou.moteur.journal import etapes_chronologie, log, prendre_instantane


def base(**extra):
    s = {"jour": 0, "phase": "nuit", "journal": []}
    s.update(extra)
    return s


def test_log_utilise_la_phase_courante():
    s = base()
    log(s, "Il se passe quelque chose.")
    assert s["journal"] == [{"jour": 0, "moment": "nuit", "texte": "Il se passe quelque chose."}]


def test_log_accepte_un_moment_explicite():
    s = base()
    log(s, "Début.", "debut")
    assert s["journal"][0]["moment"] == "debut"


def test_instantane_copie_l_etat_sans_les_instantanes():
    s = base(joueurs={"A": {"vivant": True}})
    prendre_instantane(s, "nuit")
    s["joueurs"]["A"]["vivant"] = False
    inst = s["instantanes"][0]
    assert inst["id"] == "nuit_0"
    assert inst["etat"]["joueurs"]["A"]["vivant"] is True
    assert "instantanes" not in inst["etat"]


def test_instantane_rejoue_remplace_la_version_precedente_et_les_suivantes():
    s = base()
    prendre_instantane(s, "nuit")
    s["jour"] = 1
    prendre_instantane(s, "jour")
    s["jour"] = 0
    prendre_instantane(s, "nuit")
    assert [i["id"] for i in s["instantanes"]] == ["nuit_0"]


def test_etapes_chronologie_au_depart():
    assert etapes_chronologie(base()) == [("start", 0)]


def test_etapes_chronologie_nuit_en_cours_sans_jour_correspondant():
    assert etapes_chronologie(base(jour=2, phase="nuit")) == [
        ("start", 0), ("nuit", 1), ("jour", 1), ("nuit", 2),
    ]


def test_etapes_chronologie_jour_en_cours():
    assert etapes_chronologie(base(jour=1, phase="conseil")) == [("start", 0), ("nuit", 1), ("jour", 1)]
