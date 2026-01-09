from sqlalchemy import Column, Integer, Float, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Menage(Base):
    __tablename__ = "menage_contexte"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique de l'année de contexte ménage"
    )

    # =====================================================
    # DONNÉES MÉTIER
    # =====================================================
    annee = Column(
        Integer,
        nullable=False,
        unique=True,
        comment="Année des données"
    )

    # Dépenses des ménages
    pre_engagees = Column(
        Float,
        nullable=True,
        comment="Part des dépenses pré-engagées en pourcentage"
    )

    logement = Column(
        Float,
        nullable=True,
        comment="Part des dépenses liées au logement en pourcentage"
    )

    service_multimedia = Column(
        Float,
        nullable=True,
        comment="Part des dépenses pour les services de télévision et télécommunications en pourcentage"
    )

    # Épargne des ménages
    taux_epargne = Column(
        Float,
        nullable=True,
        comment="Taux d'épargne des ménages en pourcentage"
    )

    # Prix à la consommation
    prix_consommation = Column(
        Float,
        nullable=True,
        comment="Inflation ou évolution des prix à la consommation en pourcentage"
    )

    # =====================================================
    # INDEX
    # =====================================================
    __table_args__ = (
        Index("ix_menage_contexte_annee", "annee"),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self) -> str:
        return (
            f"<Menage("
            f"annee={self.annee}, "
            f"pre_engagees={self.pre_engagees}, "
            f"logement={self.logement}, "
            f"service_multimedia={self.service_multimedia}, "
            f"taux_epargne={self.taux_epargne}, "
            f"prix_consommation={self.prix_consommation}"
            f")>"
        )
