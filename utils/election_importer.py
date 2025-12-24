from datetime import date
from db.session import SessionLocal
from enums.sexe import SexeEnum
from enums.type_election import TypeElection
from models import (
    Departement,
    Election,
    ElectionStats,
    Candidat,
    ResultatElection,
)


class ElectionImporter:
    """
    Classe pour importer les départements, élections, candidats et résultats
    depuis des DataFrames vers la base de données.

    Cette classe utilise des caches en mémoire pour optimiser les insertions massives
    et éviter les requêtes répétitives sur la base.
    """

    def __init__(self, session=None):
        """
        Initialise l'importer avec une session SQLAlchemy.

        Args:
            session: session SQLAlchemy. Si None, une nouvelle session est créée.
        """
        self.session = session or SessionLocal()
        self.existing_candidates = {}  # cache des candidats déjà en base
        self.existing_results = {}     # cache des résultats déjà en base

    # ===============================
    # Départements
    # ===============================
    def import_departements(self, df_departement):
        """
        Importe ou met à jour les départements depuis un DataFrame.

        Args:
            df_departement: DataFrame avec colonnes ['code_dept', 'nom_dept']
        """
        for _, row in df_departement.iterrows():
            dept = Departement(
                code_dept=str(row.code_dept).zfill(2),
                nom_dept=row.nom_dept
            )
            self.session.merge(dept)  # merge pour insert ou update
        self.session.commit()

    # ===============================
    # Élections
    # ===============================
    def get_or_create_election(self, election_date, type_election, tour=1, bypass_db_search=False):
        """
        Retourne une élection existante ou la crée.

        Args:
            election_date: date de l'élection
            type_election: TypeElection
            tour: numéro du tour (par défaut 1)
            bypass_db_search: si True, ne cherche pas en base

        Returns:
            Election: objet SQLAlchemy
        """
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

    # ===============================
    # Candidats
    # ===============================
    def get_or_create_candidat(self, nom: str, prenom: str, sexe: SexeEnum, bypass_db_search=False):
        """
        Retourne un candidat existant ou le crée.

        Args:
            nom: nom du candidat
            prenom: prénom du candidat
            sexe: SexeEnum
            bypass_db_search: si True, ne cherche pas en base

        Returns:
            Candidat: objet SQLAlchemy
        """
        candidat = None
        if not bypass_db_search:
            candidat = (
                self.session.query(Candidat)
                .filter_by(nom=nom, prenom=prenom, sexe=sexe)
                .one_or_none()
            )

        if candidat:
            return candidat

        candidat = Candidat(nom=nom, prenom=prenom, sexe=sexe)
        self.session.add(candidat)
        self.session.flush()  # pour obtenir l'id immédiatement
        return candidat

    # ===============================
    # Résultats
    # ===============================
    def get_or_create_resultat(self, election_id, code_dept, candidat_id, nb_voix, bypass_db_search=False):
        """
        Retourne un résultat existant ou le crée.

        Args:
            election_id: ID de l'élection
            code_dept: code du département
            candidat_id: ID du candidat
            nb_voix: nombre de voix
            bypass_db_search: si True, ne cherche pas en base

        Returns:
            ResultatElection: objet SQLAlchemy
        """
        code_dept = str(code_dept).zfill(2)
        nb_voix = int(nb_voix)

        resultat = None
        if not bypass_db_search:
            resultat = (
                self.session.query(ResultatElection)
                .filter_by(election_id=election_id, candidat_id=candidat_id, code_dept=code_dept)
                .one_or_none()
            )

        if resultat:
            # Mise à jour si nécessaire
            resultat.nb_voix = nb_voix
            return resultat

        resultat = ResultatElection(
            election_id=election_id,
            candidat_id=candidat_id,
            code_dept=code_dept,
            nb_voix=nb_voix
        )
        self.session.add(resultat)
        return resultat

    # ===============================
    # Stats par département
    # ===============================
    def import_stats(self, df_stats, election_id):
        """
        Importe les statistiques par département.

        Args:
            df_stats: DataFrame avec colonnes ['code_dept', 'nb_inscrits', 'nb_abstentions', ...]
            election_id: ID de l'élection
        """
        for _, row in df_stats.iterrows():
            exists = (
                self.session.query(ElectionStats)
                .filter_by(code_dept=str(row.code_dept).zfill(2), election_id=election_id)
                .first()
            )
            if exists:
                continue

            stats = ElectionStats(
                code_dept=str(row.code_dept).zfill(2),
                election_id=election_id,
                nb_inscrits=int(row.nb_inscrits),
                nb_abstentions=int(row.nb_abstentions),
                nb_votants=int(row.nb_votants),
                nb_blancs=int(row.nb_blancs),
                nb_nuls=int(row.nb_nuls)
            )
            self.session.add(stats)
        self.session.commit()

    # ===============================
    # Préchargement (pour performance)
    # ===============================
    def preload_candidates(self):
        """
        Précharge tous les candidats existants dans un dictionnaire.

        Returns:
            dict: {(nom, prenom, sexe): Candidat}
        """
        return {(c.nom, c.prenom, c.sexe): c for c in self.session.query(Candidat).all()}

    def preload_results(self, election_id):
        """
        Précharge tous les résultats existants pour une élection dans un set.

        Returns:
            set: {(candidat_id, code_dept)}
        """
        return {(r.candidat_id, r.code_dept) for r in self.session.query(ResultatElection)
                .filter_by(election_id=election_id).all()}

    # ===============================
    # Import ligne par ligne
    # ===============================
    def import_candidat_resultat_ligne(self, row, election_id):
        """
        Importe une seule ligne du DataFrame pour un candidat et son résultat.

        Args:
            row: ligne du DataFrame
            election_id: ID de l'élection
        """
        sexe = SexeEnum.M if row["Sexe"] == "M" else SexeEnum.F
        nom = row["Nom"].strip()
        prenom = row["Prenom"].strip()
        code_dept = str(row["Code du département"]).zfill(2)
        nb_voix = int(row["Voix"])

        # Candidat
        key_cand = (nom, prenom, sexe)
        if key_cand in self.existing_candidates:
            candidat = self.existing_candidates[key_cand]
        else:
            candidat = self.get_or_create_candidat(
                nom, prenom, sexe, bypass_db_search=True)
            self.existing_candidates[key_cand] = candidat

        # Résultat
        key_res = (election_id, candidat.id, code_dept)
        if key_res in self.existing_results:
            return  # déjà présent

        resultat = self.get_or_create_resultat(
            election_id=election_id,
            code_dept=code_dept,
            candidat_id=candidat.id,
            nb_voix=nb_voix,
            bypass_db_search=True
        )
        self.existing_results[key_res] = resultat

    # ===============================
    # Import massif
    # ===============================
    def import_candidats_resultats(self, df_candidats_resultats, election_id):
        """
        Importe un DataFrame complet de candidats et résultats.

        Args:
            df_candidats_resultats: DataFrame avec colonnes
                ['Code du département', 'Libellé du département', 'Sexe', 'Nom', 'Prenom', 'Voix']
            election_id: ID de l'élection
        """
        # Préchargement pour performance
        self.existing_candidates = self.preload_candidates()
        self.existing_results = self.preload_results(election_id)

        for _, row in df_candidats_resultats.iterrows():
            self.import_candidat_resultat_ligne(row, election_id)

        self.session.commit()
