import pandas as pd

class ElectionDataFrame:
    def __init__(self, excel_path: str):
        self.df = pd.read_excel(excel_path)

        # Nettoyage initial
        self._prepare_infos_generales()
        self._prepare_candidats()

    # =====================================================
    # 1️⃣ INFOS GÉNÉRALES
    # =====================================================
    def _prepare_infos_generales(self):
        self.df_infos_general = self.df.iloc[:, :17].copy()
        self.df_infos_general.columns = [
            "code_dept", "nom_dept", "etat_saisie", "nb_inscrits",
            "nb_abstentions", "pct_abstentions", "nb_votants",
            "pct_votants", "nb_blancs", "pct_blancs_inscrits",
            "pct_blancs_votants", "nb_nuls", "pct_nuls_inscrits",
            "pct_nuls_votants", "nb_exprimes",
            "pct_exprimes_inscrits", "pct_exprimes_votants"
        ]

        # On garde uniquement les départements complets
        self.df_infos_general = self.df_infos_general[
            self.df_infos_general["etat_saisie"] == "Complet"
        ]

        self.df_infos_general_base = self.df_infos_general[
            ["code_dept", "nom_dept",
             "nb_inscrits", "nb_abstentions",
             "nb_votants", "nb_blancs", "nb_nuls"]
        ]

        self.df_departement = self.df_infos_general_base[
            ["code_dept", "nom_dept"]
        ].drop_duplicates()

        self.df_stat_elections = self.df_infos_general_base.drop(
            columns=["nom_dept"]
        )

    # =====================================================
    # 2️⃣ CANDIDATS / RÉSULTATS
    # =====================================================
    def _prepare_candidats(self):
        cols_globales = ["Code du département", "Libellé du département"]
        df_candidates = self.df.iloc[:, 17:]
        cols_per_candidate = 6
        num_candidates = df_candidates.shape[1] // cols_per_candidate

        dfs = []

        for i in range(num_candidates):
            start = i * cols_per_candidate
            end = start + cols_per_candidate

            df_cand = df_candidates.iloc[:, start:end].copy()
            df_cand.columns = [
                "Sexe", "Nom", "Prenom", "Voix",
                "% Voix/Ins", "% Voix/Exp"
            ]

            df_cand = pd.concat(
                [self.df[cols_globales], df_cand],
                axis=1
            )

            dfs.append(df_cand)

        self.df_candidat_resultat = (
            pd.concat(dfs, ignore_index=True)
            [["Code du département", "Libellé du département",
              "Sexe", "Nom", "Prenom", "Voix"]]
        )

    # =====================================================
    # 3️⃣ MÉTHODES MÉTIER (REQUÊTES)
    # =====================================================
    def get_candidats(self):
        """Liste unique des candidats"""
        return (
            self.df_candidat_resultat
            [["Sexe", "Nom", "Prenom"]]
            .drop_duplicates()
            .sort_values(["Nom", "Prenom"])
            .reset_index(drop=True)
        )

    def get_voix_par_departement(self, nom, prenom):
        """Voix d’un candidat par département"""
        return (
            self.df_candidat_resultat[
                (self.df_candidat_resultat["Nom"] == nom) &
                (self.df_candidat_resultat["Prenom"] == prenom)
            ]
            [["Code du département", "Libellé du département", "Voix"]]
            .sort_values("Code du département")
        )

    def get_stats_departement(self, code_dept):
        """Stats globales d’un département"""
        return self.df_stat_elections[
            self.df_stat_elections["code_dept"] == code_dept
        ]

    def get_stats_departement_candidat(self, code_dept, nom, prenom):
        """Stats + voix pour un département et un candidat"""
        stats = self.get_stats_departement(code_dept)
        voix = self.df_candidat_resultat[
            (self.df_candidat_resultat["Code du département"] == code_dept) &
            (self.df_candidat_resultat["Nom"] == nom) &
            (self.df_candidat_resultat["Prenom"] == prenom)
        ][["Voix"]]

        return {
            "stats_departement": stats,
            "voix_candidat": voix
        }
