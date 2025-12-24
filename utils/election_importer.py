from datetime import date
from db.session import SessionLocal
from enums.sexe import SexeEnum
from enums.type_election import TypeElection
from models import Departement, Election, ElectionStats, Candidat, ResultatElection


class ElectionImporter:
    """
    Classe pour importer départements, élections, candidats et résultats
    depuis des DataFrames vers la base de données.
    """

    def __init__(self, session=None):
        self.session = session or SessionLocal()
        self.existing_candidates = {}
        self.existing_results = {}

    # =====================================================
    # Normalisation
    # =====================================================
    @staticmethod
    def normalize_code(code):
        code_str = str(code).strip().upper()
        return code_str.zfill(2) if code_str.isdigit() else code_str

    @staticmethod
    def normalize_name(value: str) -> str:
        return value.strip().upper()

    # =====================================================
    # Préchargement
    # =====================================================
    def preload_candidates(self):
        """
        Cache candidats existants
        clé = (nom, prenom, sexe)
        """
        return {
            (
                c.nom.upper(),
                c.prenom.upper(),
                c.sexe
            ): c
            for c in self.session.query(Candidat).all()
        }

    def preload_results(self, election_id):
        """
        Cache résultats existants
        clé = (election_id, candidat_id, code_dept)
        """
        return {
            (
                r.election_id,
                r.candidat_id,
                r.code_dept
            ): r
            for r in self.session.query(ResultatElection)
            .filter_by(election_id=election_id)
            .all()
        }

    # =====================================================
    # Départements
    # =====================================================
    def import_departements(self, df_departement):
        """
        Importe ou met à jour les départements depuis un DataFrame.
        Les codes sont normalisés.
        """
        for _, row in df_departement.iterrows():
            dept = Departement(
                code_dept=self.normalize_code(row.code_dept),
                nom_dept=row.nom_dept
            )
            self.session.merge(dept)  # merge pour insert ou update
        self.session.commit()

    # =====================================================
    # Stats par département
    # =====================================================

    def import_stats(self, df_stats, election_id):
        """
        Importe les statistiques par département.
        Les codes sont normalisés.
        """
        for _, row in df_stats.iterrows():
            code_dept_norm = self.normalize_code(row.code_dept)
            exists = (
                self.session.query(ElectionStats)
                .filter_by(code_dept=code_dept_norm, election_id=election_id)
                .first()
            )
            if exists:
                continue

            stats = ElectionStats(
                code_dept=code_dept_norm,
                election_id=election_id,
                nb_inscrits=int(row.nb_inscrits),
                nb_abstentions=int(row.nb_abstentions),
                nb_votants=int(row.nb_votants),
                nb_blancs=int(row.nb_blancs),
                nb_nuls=int(row.nb_nuls)
            )
            self.session.add(stats)
        self.session.commit()

    # =====================================================
    # Élections
    # =====================================================

    def get_or_create_election(self, election_date, type_election, tour=1, bypass_db_search=False):
        election = None
        if not bypass_db_search:
            election = (
                self.session.query(Election)
                .filter_by(date=election_date, type_election=type_election, tour=tour)
                .first()
            )
        if not election:
            election = Election(date=election_date,
                                type_election=type_election, tour=tour)
            self.session.add(election)
            self.session.commit()
        return election

    # =====================================================
    # Candidats
    # =====================================================
    def get_or_create_candidat(self, nom, prenom, sexe):
        candidat = Candidat(
            nom=nom,
            prenom=prenom,
            sexe=sexe
        )
        self.session.add(candidat)
        self.session.flush()  # garantit candidat.id
        return candidat

    # =====================================================
    # Résultats
    # =====================================================
    def get_or_create_resultat(self, election_id, code_dept, candidat_id, nb_voix):
        resultat = ResultatElection(
            election_id=election_id,
            candidat_id=candidat_id,
            code_dept=code_dept,
            nb_voix=int(nb_voix)
        )
        self.session.add(resultat)
        return resultat

    # =====================================================
    # Import ligne
    # =====================================================
    def import_candidat_resultat_ligne(self, row, election_id):
        sexe = SexeEnum.M if row["Sexe"] == "M" else SexeEnum.F

        nom = self.normalize_name(row["Nom"])
        prenom = self.normalize_name(row["Prenom"])
        code_dept = self.normalize_code(row["Code du département"])
        nb_voix = int(row["Voix"])

        # ---------- CANDIDAT ----------
        key_cand = (nom, prenom, sexe)
        candidat = self.existing_candidates.get(key_cand)

        if not candidat:
            candidat = self.get_or_create_candidat(nom, prenom, sexe)
            self.existing_candidates[key_cand] = candidat

        # ---------- RESULTAT ----------
        key_res = (election_id, candidat.id, code_dept)

        if key_res in self.existing_results:
            return

        resultat = self.get_or_create_resultat(
            election_id,
            code_dept,
            candidat.id,
            nb_voix
        )

        self.existing_results[key_res] = resultat

    # =====================================================
    # Import massif
    # =====================================================
    def import_candidats_resultats(self, df, election_id):
        self.existing_candidates = self.preload_candidates()
        self.existing_results = self.preload_results(election_id)

        for _, row in df.iterrows():
            self.import_candidat_resultat_ligne(row, election_id)

        self.session.commit()
