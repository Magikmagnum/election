from sqlalchemy import (
    Column,
    String,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from db import Base


class Departement(Base):
    __tablename__ = "departements"

    # =====================================================
    # IDENTITÉ
    # =====================================================
    code_dept = Column(
        String(2),
        primary_key=True,
        comment="Code officiel du département (ex: 01, 59, 75)"
    )

    nom_dept = Column(
        String(100),
        nullable=False,
        comment="Nom du département"
    )

    # =====================================================
    # RELATIONS
    # =====================================================

    # Statistiques globales d'une élection par département
    stats = relationship(
        "ElectionStats",
        back_populates="departement",
        cascade="all, delete-orphan"
    )

    # Résultats détaillés par candidat et par élection
    resultats = relationship(
        "ResultatElection",
        back_populates="departement",
        cascade="all, delete-orphan"
    )

    # Populations par sexe / tranche d'âge / année
    populations = relationship(
        "PopulationDepartement",
        back_populates="departement",
        cascade="all, delete-orphan"
    )

    chomages = relationship(
        "Chomage",
        back_populates="departement",
        cascade="all, delete-orphan"
    )

    # Faits de sécurité liés au département
    faits_securite = relationship(
        "FaitSecurite",
        back_populates="departement",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # CONTRAINTES & INDEX
    # =====================================================
    __table_args__ = (
        # Empêche un nom vide ou uniquement composé d'espaces
        CheckConstraint(
            "length(trim(nom_dept)) > 0",
            name="ck_nom_dept_non_vide"
        ),

        # Index pour requêtes analytiques (recherche par nom)
        Index(
            "ix_departements_nom",
            "nom_dept"
        ),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self):
        return (
            f"<Departement("
            f"code_dept='{self.code_dept}', "
            f"nom_dept='{self.nom_dept}')>"
        )
