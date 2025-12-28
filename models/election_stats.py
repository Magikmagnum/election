from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from db import Base


class ElectionStats(Base):
    __tablename__ = "election_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code_dept = Column(
        String(3),
        ForeignKey("departements.code_dept", ondelete="CASCADE"),
        nullable=False
    )

    election_id = Column(
        Integer,
        ForeignKey("elections.id", ondelete="CASCADE"),
        nullable=False
    )

    nb_inscrits = Column(Integer, nullable=False)
    nb_abstentions = Column(Integer, nullable=False)
    nb_votants = Column(Integer, nullable=False)
    nb_blancs_nuls = Column(Integer, nullable=False)

    departement = relationship(
        "Departement",
        back_populates="stats"
    )

    election = relationship(
        "Election",
        back_populates="stats"
    )

    __table_args__ = (
        # Un seul enregistrement par département et par élection
        UniqueConstraint(
            "code_dept",
            "election_id",
            name="uq_electionstats_dept_election"
        ),

        # Règles de cohérence métier
        CheckConstraint("nb_inscrits >= 0", name="ck_inscrits_pos"),
        CheckConstraint("nb_votants >= 0", name="ck_votants_pos"),
        CheckConstraint("nb_abstentions >= 0", name="ck_abstentions_pos"),
        CheckConstraint("nb_blancs_nuls >= 0", name="ck_blancs_pos"),

        # Cohérence électorale basique
        CheckConstraint(
            "nb_votants <= nb_inscrits",
            name="ck_votants_le_inscrits"
        ),

        # Index analytiques
        Index("ix_stats_election", "election_id"),
        Index("ix_stats_dept", "code_dept"),
    )

    def __repr__(self):
        return (
            f"<ElectionStats("
            f"election={self.election_id}, "
            f"dept={self.code_dept}, "
            f"inscrits={self.nb_inscrits}, "
            f"votants={self.nb_votants})>"
        )
