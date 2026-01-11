# =====================================================
# Élections présidentielles 2017 – Import DB (Tours 1 & 2)
# =====================================================

import pandas as pd
from datetime import date

from db import SessionLocal
from utils.election_importer import ElectionImporter
from enums.type_election import TypeElection

# =====================================================
# CONFIG
# =====================================================
TOURS = [1, 2]
BASE_PATH = "./data/elections"

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

# =====================================================
# INIT
# =====================================================
session = SessionLocal()
importer = ElectionImporter()

# =====================================================
# BOUCLE SUR LES TOURS
# =====================================================
for tour in TOURS:

    print(f"\n🚀 Traitement présidentielle 2017 – Tour {tour}")

    df = pd.read_excel(f"{BASE_PATH}/presidentielles-2017-{tour}.xlsx")

    # Nettoyage
    df.drop(columns=["Etat saisie"], errors="ignore", inplace=True)

    # =================================================
    # INFOS GÉNÉRALES DÉPARTEMENT
    # =================================================
    df_infos = df.iloc[:, :16].copy()
    df_infos.columns = [
        "code_dept", "nom_dept", "nb_inscrits", "nb_abstentions",
        "pct_abstentions", "nb_votants", "pct_votants",
        "nb_blancs", "pct_blancs_inscrits", "pct_blancs_votants",
        "nb_nuls", "pct_nuls_inscrits", "pct_nuls_votants",
        "nb_exprimes", "pct_exprimes_inscrits", "pct_exprimes_votants"
    ]

    df_base = df_infos[
        [
            "code_dept", "nom_dept",
            "nb_inscrits", "nb_abstentions",
            "nb_votants", "nb_blancs", "nb_nuls"
        ]
    ]

    # Fusion blancs + nuls
    df_base["nb_blancs_nuls"] = (
        df_base["nb_blancs"].fillna(0)
        + df_base["nb_nuls"].fillna(0)
    )
    df_base.drop(columns=["nb_blancs", "nb_nuls"], inplace=True)

    df_departement = df_base[["code_dept", "nom_dept"]]
    df_stat_elections = df_base.drop(columns=["nom_dept"])

    # =================================================
    # RÉSULTATS CANDIDATS
    # =================================================
    df_candidates = df.iloc[:, 16:]
    COLS_PER_CANDIDATE = 6
    num_candidates = df_candidates.shape[1] // COLS_PER_CANDIDATE

    dfs = []

    for i in range(num_candidates):
        start = i * COLS_PER_CANDIDATE
        end = start + COLS_PER_CANDIDATE

        df_cand = df_candidates.iloc[:, start:end].copy()
        df_cand.columns = ["sexe", "nom", "prenom", "voix", "pct_voix_ins", "pct_voix_exp"]

        df_cand = pd.concat(
            [df[["Code du département", "Libellé du département"]], df_cand],
            axis=1
        )

        dfs.append(df_cand)

    df_candidat_resultat = pd.concat(dfs, ignore_index=True)[
        ["Code du département", "Libellé du département", "sexe", "nom", "prenom", "voix"]
    ]

    # =================================================
    # IMPORT EN BASE
    # =================================================
    election_date = date(2017, 4, 23) if tour == 1 else date(2017, 5, 7)

    election = importer.get_or_create_election(
        election_date=election_date,
        type_election=TypeElection.PRESIDENTIELLE,
        tour=tour
    )

    if not df_departement.empty:
        importer.import_departements(df_departement)

    if not df_stat_elections.empty:
        importer.import_stats(df_stat_elections, election.id)

    if not df_candidat_resultat.empty:
        importer.import_candidats_resultats(df_candidat_resultat, election.id)

    print(f"✅ Présidentielle 2017 – Tour {tour} importé")

print("\n🎉 Import présidentielles 2017 (tours 1 & 2) terminé")
