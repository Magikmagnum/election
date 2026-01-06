from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from db import Base


class Chomage(Base):
    __tablename__ = "chomage"

    # =====================================================
    # IDENTITÉ (clé primaire composée)
    # =====================================================
    code_dept = Column(
        String(2),
        ForeignKey("departements.code_dept"),
        primary_key=True,
        comment="Code du département (ex: 01, 59, 97)"
    )

    annee = Column(
        Integer,
        primary_key=True,
        comment="Année de référence (ex: 2007)"
    )

    trimestre = Column(
        Integer,
        primary_key=True,
        comment="Trimestre (1 à 4)"
    )

    taux_chomage = Column(
        Float,
        nullable=True,
        comment="Taux de chômage en pourcentage"
    )

    # =====================================================
    # RELATIONS
    # =====================================================
    departement = relationship(
        "Departement",
        back_populates="chomages"
    )

    # =====================================================
    # CONTRAINTES & INDEX
    # =====================================================
    __table_args__ = (
        # Trimestre valide
        CheckConstraint(
            "trimestre BETWEEN 1 AND 4",
            name="ck_chomage_trimestre_valide"
        ),

        # Taux cohérent
        CheckConstraint(
            "taux_chomage IS NULL OR taux_chomage >= 0",
            name="ck_chomage_taux_positif"
        ),

        # Index analytique
        Index(
            "ix_chomage_annee_trimestre",
            "annee",
            "trimestre"
        ),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self):
        return (
            f"<Chomage("
            f"code_dept='{self.code_dept}', "
            f"annee={self.annee}, "
            f"trimestre={self.trimestre}, "
            f"taux={self.taux_chomage})>"
        )
