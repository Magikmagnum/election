from sqlalchemy import (
    Column, Integer, String, Enum,
    UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from db import Base
from enums.sexe import SexeEnum


class Candidat(Base):
    __tablename__ = "candidats"

    id = Column(Integer, primary_key=True, autoincrement=True)

    sexe = Column(
        Enum(SexeEnum, name="sexe_enum", native_enum=True),
        nullable=False
    )

    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)

    resultats = relationship(
        "ResultatElection",
        back_populates="candidat",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Unicité logique d’un candidat
        UniqueConstraint(
            "nom",
            "prenom",
            "sexe",
            name="uq_candidat_identite"
        ),

        # Empêche les chaînes vides
        CheckConstraint("length(nom) > 0", name="ck_nom_non_vide"),
        CheckConstraint("length(prenom) > 0", name="ck_prenom_non_vide"),

        # Index utiles pour recherches fréquentes
        Index("ix_candidat_nom", "nom"),
        Index("ix_candidat_prenom", "prenom"),
    )

    def __repr__(self):
        return (
            f"<Candidat("
            f"id={self.id}, "
            f"prenom='{self.prenom}', "
            f"nom='{self.nom}', "
            f"sexe={self.sexe.name})>"
        )
