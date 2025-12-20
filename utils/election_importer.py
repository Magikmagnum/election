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
    def __init__(self, session=None):
        self.session = session or SessionLocal()

    # -------------------------
    # Départements
    # -------------------------
    def import_departements(self, df_departement):
        for _, row in df_departement.iterrows():
            dept = Departement(
                code_dept=str(row.code_dept).zfill(2),
                nom_dept=row.nom_dept
            )
            self.session.merge(dept)
        self.session.commit()

    # -------------------------
    # Élection
    # -------------------------
    def get_or_create_election(self, election_date, type_election, tour=1):
        election = (
            self.session.query(Election)
            .filter_by(date=election_date, type_election=type_election, tour=tour)
            .first()
        )
        if not election:
            election = Election(date=election_date, type_election=type_election, tour=tour)
            self.session.add(election)
            self.session.commit()
        return election

    # -------------------------
    # Stats par département
    # -------------------------
    def import_stats(self, df_stats, election_id):
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

    # -------------------------
    # Candidats et résultats
    # -------------------------
    def import_candidats_resultats(self, df_candidats_resultats, election_id):
        existing_candidates = {
            (c.nom, c.prenom, c.sexe): c for c in self.session.query(Candidat).all()
        }
        existing_results = {
            (r.election_id, r.candidat_id): r for r in self.session.query(ResultatElection).all()
        }

        for _, row in df_candidats_resultats.iterrows():
            sexe = SexeEnum.M if row["Sexe"] == "M" else SexeEnum.F
            key_cand = (row["Nom"], row["Prenom"], sexe)

            # Candidat
            if key_cand in existing_candidates:
                candidat = existing_candidates[key_cand]
            else:
                candidat = Candidat(nom=row["Nom"], prenom=row["Prenom"], sexe=sexe)
                self.session.add(candidat)
                self.session.flush()
                existing_candidates[key_cand] = candidat

            # Résultat
            key_res = (election_id, candidat.id)
            if key_res in existing_results:
                continue
            resultat = ResultatElection(
                election_id=election_id,
                candidat_id=candidat.id,
                nb_voix=int(row["Voix"])
            )
            self.session.add(resultat)
            existing_results[key_res] = resultat

        self.session.commit()
