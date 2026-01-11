# =====================================================
# Élections présidentielles 2012 – Import DB (Tours 1 & 2)
# =====================================================

import pandas as pd
from datetime import date

from db import SessionLocal
from utils.election_importer import ElectionImporter
from enums.type_election import TypeElection

# =====================================================
# CONFIGURATION
# =====================================================
TOURS = [1, 2]
BASE_PATH = "./data/elections"

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

# =====================================================
# INIT DB & IMPORTER
# =====================================================
session = SessionLocal()
importer = ElectionImporter()

# =====================================================
# BOUCLE SUR LES TOURS
# =====================================================
for tour in TOURS:

    print(f"\n🚀 Traitement du tour {tour}")

    file_path = f"{BASE_PATH}/presidentielles-2012-{tour}.xlsx"
    df = pd.read_excel(file_path)

    # Correction spécifique tour 2
    if tour == 2 and 107 in df.index:
        df.drop(index=107, inplace=True)

    # Nettoyage colonnes
    df.drop(columns=["Etat saisie"], errors="ignore", inplace=True)

    # =================================================
    # INFOS GÉNÉRALES PAR DÉPARTEMENT
    # =================================================
    df_infos = df.iloc[:, :13].copy()
    df_infos.columns = [
        "code_dept", "nom_dept", "nb_inscrits", "nb_abstentions",
        "pct_abstentions", "nb_votants", "pct_votants",
        "nb_blancs_nuls", "pct_blancs_nuls_inscrits",
        "pct_blancs_nuls_votants", "nb_exprimes",
        "pct_exprimes_inscrits", "pct_exprimes_votants"
    ]

    df_infos_base = df_infos[
        ["code_dept", "nom_dept", "nb_inscrits", "nb_abstentions", "nb_votants", "nb_blancs_nuls"]
    ]

    df_departement = df_infos_base[["code_dept", "nom_dept"]]
    df_stat_elections = df_infos_base.drop(columns=["nom_dept"])

    # =================================================
    # RÉSULTATS PAR CANDIDAT
    # =================================================
    df_candidates = df.iloc[:, 13:]
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
    election_date = date(2012, 4, 22) if tour == 1 else date(2012, 5, 6)

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

    print(f"✅ Tour {tour} importé avec succès")

print("\n🎉 Import des tours 1 et 2 terminé")
