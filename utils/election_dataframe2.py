import pandas as pd
from typing import List, Dict, Optional


class ElectionDataFrame:
    """
    Classe généralisée de gestion des données électorales.

    Elle permet de travailler avec des scrutins variés et des fichiers
    différents (Excel, CSV, SQL…) en utilisant une configuration externe.
    """

    def __init__(self, df: pd.DataFrame, config: Dict):
        self.df = df.copy()
        self.config = config

        self._normalize_schema()
        self._prepare_infos_generales()
        self._prepare_candidats()

    # =====================================================
    # 0️⃣ NORMALISATION DU SCHÉMA
    # =====================================================
    def _normalize_schema(self):
        filter_col = self.config.get("filter_column", "etat_saisie")
        filter_default = self.config.get("filter_value", "Complet")

        if filter_col not in self.df.columns:
            self.df.insert(2, filter_col, filter_default)

        self.df[filter_col] = (
            self.df[filter_col].fillna(
                filter_default).astype(str).str.capitalize()
        )

    # =====================================================
    # 🔹 Normalisation code département
    # =====================================================
    @staticmethod
    def normalize_code(code):
        """
        Normalise un code de département en string sur 2 caractères.
        Gère les codes numériques et les codes spéciaux comme 2A, 2B.
        """
        code_str = str(code).strip().upper()
        if code_str.isdigit():
            return code_str.zfill(2)
        return code_str

    # =====================================================
    # 1️⃣ INFOS GÉNÉRALES
    # =====================================================
    def _prepare_infos_generales(self):
        n_gen = self.config.get("n_general_cols", 17)
        self.df_infos_general = self.df.iloc[:, :n_gen].copy()

        # Renommage si fourni dans config
        general_info_cols = self.config.get(
            "general_info_cols", self.df_infos_general.columns.tolist()
        )
        self.df_infos_general.columns = general_info_cols

        # Filtrage selon la colonne configurée
        filter_col = self.config.get("filter_column", "etat_saisie")
        filter_val = self.config.get("filter_value", "Complet")
        self.df_infos_general = self.df_infos_general.loc[
            self.df_infos_general[filter_col] == filter_val
        ].copy()

        # DataFrame avec colonnes chiffrées
        numeric_cols = self.config.get(
            "numeric_cols",
            ["nb_inscrits", "nb_abstentions", "nb_votants", "nb_blancs", "nb_nuls"]
        )
        self.df_infos_general_base = self.df_infos_general.loc[:, [
            "code_dept", "nom_dept"] + numeric_cols].copy()

        # Normaliser les codes de département
        self.df_infos_general_base.loc[:, "code_dept"] = \
            self.df_infos_general_base["code_dept"].map(self.normalize_code)

        # Liste unique des départements
        self.df_departement = self.df_infos_general_base.loc[:, [
            "code_dept", "nom_dept"]].drop_duplicates().copy()

        # Stats globales pour requêtes
        self.df_stat_elections = self.df_infos_general_base.drop(
            columns=["nom_dept"]).copy()

    # =====================================================
    # 2️⃣ CANDIDATS / RÉSULTATS
    # =====================================================
    def _prepare_candidats(self):
        cols_globales = self.config.get(
            "cols_globales", ["Code du département", "Libellé du département"]
        )
        candidate_cols = self.config.get(
            "candidate_columns", ["Sexe", "Nom", "Prenom",
                                  "Voix", "% Voix/Ins", "% Voix/Exp"]
        )
        n_cols_per_candidate = self.config.get("n_cols_per_candidate", 6)

        df_candidates = self.df.iloc[:, self.config.get("n_general_cols", 17):]
        num_candidates = df_candidates.shape[1] // n_cols_per_candidate
        dfs = []

        for i in range(num_candidates):
            start = i * n_cols_per_candidate
            end = start + n_cols_per_candidate
            df_cand = df_candidates.iloc[:, start:end].copy()
            df_cand.columns = candidate_cols
            df_cand = pd.concat(
                [self.df[cols_globales].copy(), df_cand], axis=1)

            # Normaliser les codes de département
            df_cand.loc[:, cols_globales[0]] = df_cand[cols_globales[0]].map(
                self.normalize_code)

            dfs.append(df_cand)

        self.df_candidat_resultat = pd.concat(
            dfs, ignore_index=True).loc[:, cols_globales + candidate_cols[:4]].copy()

    # =====================================================
    # 3️⃣ MÉTHODES MÉTIER
    # =====================================================
    def get_candidats(self):
        return (
            self.df_candidat_resultat.loc[:, ["Sexe", "Nom", "Prenom"]]
            .drop_duplicates()
            .sort_values(["Nom", "Prenom"])
            .reset_index(drop=True)
        )

    def get_voix_par_departement(self, nom: str, prenom: str):
        cols_globales = self.config.get(
            "cols_globales", ["Code du département", "Libellé du département"]
        )
        df_cand = self.df_candidat_resultat.loc[
            (self.df_candidat_resultat["Nom"] == nom) &
            (self.df_candidat_resultat["Prenom"] == prenom),
            cols_globales + ["Voix"]
        ].copy()

        # Tri prenant en compte les codes alphanumériques
        def code_sort_key(code):
            num_part = ''.join(filter(str.isdigit, code))
            letter_part = ''.join(filter(str.isalpha, code))
            return (int(num_part) if num_part else 0, letter_part)

        df_cand = df_cand.sort_values(
            by=cols_globales[0], key=lambda x: x.map(code_sort_key))
        return df_cand

    def get_stats_departement(self, code_dept: str):
        code_dept = self.normalize_code(code_dept)
        return self.df_stat_elections.loc[
            self.df_stat_elections["code_dept"] == code_dept
        ].copy()

    def get_stats_departement_candidat(self, code_dept: str, nom: str, prenom: str):
        code_dept = self.normalize_code(code_dept)
        stats = self.get_stats_departement(code_dept)
        cols_globales = self.config.get(
            "cols_globales", ["Code du département", "Libellé du département"]
        )
        voix = self.df_candidat_resultat.loc[
            (self.df_candidat_resultat[cols_globales[0]] == code_dept) &
            (self.df_candidat_resultat["Nom"] == nom) &
            (self.df_candidat_resultat["Prenom"] == prenom),
            ["Voix"]
        ].copy()
        return {"stats_departement": stats, "voix_candidat": voix}
