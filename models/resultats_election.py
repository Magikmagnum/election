from sqlalchemy import (
    Column, Integer, ForeignKey,
    UniqueConstraint, CheckConstraint, Index, String
)
from sqlalchemy.orm import relationship
from db import Base


class ResultatElection(Base):
    __tablename__ = "resultats_election"

    id = Column(Integer, primary_key=True, autoincrement=True)

    election_id = Column(Integer, ForeignKey("elections.id"), nullable=False)
    candidat_id = Column(Integer, ForeignKey("candidats.id"), nullable=False)
    code_dept = Column(
        String(2),
        ForeignKey("departements.code_dept", ondelete="CASCADE"),
        nullable=False
    )

    nb_voix = Column(Integer, nullable=False)

    election = relationship("Election", back_populates="resultats")
    candidat = relationship("Candidat", back_populates="resultats")
    departement = relationship("Departement")

    __table_args__ = (
        UniqueConstraint(
            "election_id",
            "candidat_id",
            "code_dept",
            name="uq_resultat_election_candidat_dept"
        ),
        CheckConstraint(
            "nb_voix >= 0",
            name="ck_nb_voix_positive"
        ),
        Index("ix_resultat_election", "election_id"),
        Index("ix_resultat_candidat", "candidat_id"),
        Index("ix_resultat_departement", "code_dept"),
    )

    def __repr__(self):
        return (
            f"<ResultatElection("
            f"election_id={self.election_id}, "
            f"candidat_id={self.candidat_id}, "
            f"nb_voix={self.nb_voix})>"
        )
