# election_pipeline.py
import pandas as pd
from datetime import date
from tqdm import tqdm
from db import SessionLocal
from utils.election_importer import ElectionImporter
from enums.type_election import TypeElection

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

BASE_PATH = "./data/elections"

ELECTIONS = {
    2012: {
        "file_pattern": "presidentielles-2012-{}.xlsx",
        "dates": {1: date(2012, 4, 22), 2: date(2012, 5, 6)},
        "infos_cols": 13
    },
    2017: {
        "file_pattern": "presidentielles-2017-{}.xlsx",
        "dates": {1: date(2017, 4, 23), 2: date(2017, 5, 7)},
        "infos_cols": 16
    },
    2022: {
        "file_pattern": "presidentielles-2022-{}.xlsx",
        "dates": {1: date(2022, 4, 10), 2: date(2022, 4, 24)},
        "infos_cols": 16
    }
}

TOURS = [1, 2]

def run_election_pipeline(elections=None, show_progress=True):
    """
    Pipeline d'import des élections présidentielles.
    
    elections: liste d'années à traiter. Si None, traite toutes.
    show_progress: afficher les barres de progression pour les candidats.
    """
    session = SessionLocal()
    importer = ElectionImporter()

    elections_to_run = elections if elections else ELECTIONS.keys()

    for year in elections_to_run:
        config = ELECTIONS[year]
        print(f"\n🎯 Traitement élections présidentielles {year}")

        for tour in TOURS:
            print(f"\n🚀 Tour {tour} ({year})")

            file_path = f"{BASE_PATH}/{config['file_pattern'].format(tour)}"
            df = pd.read_excel(file_path)

            # Correction spécifique 2012 tour 2
            if year == 2012 and tour == 2 and 107 in df.index:
                df.drop(index=107, inplace=True)

            # Nettoyage
            df.drop(columns=["Etat saisie"], errors="ignore", inplace=True)

            # Infos générales
            infos_cols = config['infos_cols']
            df_infos = df.iloc[:, :infos_cols].copy()

            if year == 2012:
                df_infos.columns = [
                    "code_dept", "nom_dept", "nb_inscrits", "nb_abstentions",
                    "pct_abstentions", "nb_votants", "pct_votants",
                    "nb_blancs_nuls", "pct_blancs_nuls_inscrits",
                    "pct_blancs_nuls_votants", "nb_exprimes",
                    "pct_exprimes_inscrits", "pct_exprimes_votants"
                ]
                base_cols = ["code_dept", "nom_dept", "nb_inscrits", "nb_abstentions", "nb_votants", "nb_blancs_nuls"]
            else:
                df_infos.columns = [
                    "code_dept", "nom_dept", "nb_inscrits", "nb_abstentions",
                    "pct_abstentions", "nb_votants", "pct_votants",
                    "nb_blancs", "pct_blancs_inscrits", "pct_blancs_votants",
                    "nb_nuls", "pct_nuls_inscrits", "pct_nuls_votants",
                    "nb_exprimes", "pct_exprimes_inscrits", "pct_exprimes_votants"
                ]
                base_cols = ["code_dept", "nom_dept", "nb_inscrits", "nb_abstentions", "nb_votants", "nb_blancs", "nb_nuls"]

            df_base = df_infos[base_cols].copy()

            if {"nb_blancs", "nb_nuls"}.issubset(df_base.columns):
                df_base["nb_blancs_nuls"] = df_base["nb_blancs"].fillna(0) + df_base["nb_nuls"].fillna(0)
                df_base.drop(columns=["nb_blancs", "nb_nuls"], inplace=True)

            df_departement = df_base[["code_dept", "nom_dept"]]
            df_stat_elections = df_base.drop(columns=["nom_dept"])

            # Résultats candidats
            df_candidates = df.iloc[:, infos_cols:]
            COLS_PER_CANDIDATE = 6
            num_candidates = df_candidates.shape[1] // COLS_PER_CANDIDATE

            dfs = []
            iterator = range(num_candidates)
            if show_progress:
                iterator = tqdm(iterator, desc="Traitement candidats", ncols=100)

            for i in iterator:
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

            # Import DB
            election_date = config["dates"][tour]

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

            print(f"✅ Élection {year} – Tour {tour} importé")

    print("\n🎉 Import complet des présidentielles terminé")
