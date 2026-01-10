from sqlalchemy import Column, Integer, Float, Index
from db import Base

class Entreprise(Base):
    __tablename__ = "entreprise_contexte"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique du contexte entrepreneurial"
    )

    # =====================================================
    # DONNÉES TEMPORELLES
    # =====================================================
    annee = Column(
        Integer,
        nullable=False,
        unique=True,
        comment="Année des données économiques"
    )

    # =====================================================
    # DYNAMIQUE ENTREPRENEURIALE
    # =====================================================
    croissance_total_entreprises = Column(
        Float,
        nullable=True,
        comment="Taux de croissance annuel du nombre total d'entreprises"
    )

    ratio_micro = Column(
        Float,
        nullable=True,
        comment="Part des micro-entrepreneurs dans le total des entreprises"
    )

    # =====================================================
    # COMMERCE EXTÉRIEUR
    # =====================================================
    solde_commercial = Column(
        Float,
        nullable=True,
        comment="Solde commercial (exportations - importations)"
    )

    croissance_export = Column(
        Float,
        nullable=True,
        comment="Taux de croissance annuel des exportations"
    )

    # =====================================================
    # INDEX
    # =====================================================
    __table_args__ = (
        Index("ix_entreprise_contexte_annee", "annee"),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self) -> str:
        return (
            f"<Entreprise("
            f"annee={self.annee}, "
            f"croissance_total_entreprises={self.croissance_total_entreprises}, "
            f"ratio_micro={self.ratio_micro}, "
            f"solde_commercial={self.solde_commercial}, "
            f"croissance_export={self.croissance_export}"
            f")>"
        )
