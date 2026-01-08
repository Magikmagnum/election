from sqlalchemy import Column, Integer, Float, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MenageDepense(Base):
    __tablename__ = "menage_depenses"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique de l'année de dépense"
    )

    # =====================================================
    # DONNÉES MÉTIER
    # =====================================================
    annee = Column(
        Integer,
        nullable=False,
        unique=True,
        comment="Année des données de dépenses de ménage"
    )

    pre_engagees = Column(
        Float,
        nullable=False,
        comment="Part des dépenses pré-engagées en pourcentage"
    )

    logement = Column(
        Float,
        nullable=False,
        comment="Part des dépenses liées au logement en pourcentage"
    )

    service_multimedia = Column(
        Float,
        nullable=False,
        comment="Part des dépenses pour les services de télévision et télécommunications en pourcentage"
    )

    # =====================================================
    # INDEX
    # =====================================================
    __table_args__ = (
        Index("ix_menage_depenses_annee", "annee"),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self) -> str:
        return (
            f"<MenageDepenses("
            f"annee={self.annee}, "
            f"pre_engagees={self.pre_engagees}, "
            f"logement={self.logement}, "
            f"service_multimedia={self.service_multimedia}"
            f")>"
        )
