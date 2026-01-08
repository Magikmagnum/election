from sqlalchemy import Column, Integer, Float, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MenageEpargne(Base):
    __tablename__ = "epargne"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique de l'année d'épargne"
    )

    # =====================================================
    # DONNÉES MÉTIER
    # =====================================================
    annee = Column(
        Integer,
        nullable=False,
        unique=True,
        comment="Année des données d'épargne"
    )

    taux_epargne = Column(
        Float,
        nullable=False,
        comment="Taux d'épargne des ménages en pourcentage"
    )

    # =====================================================
    # RELATIONS
    # =====================================================


    # =====================================================
    # INDEX
    # =====================================================
    __table_args__ = (
        Index("ix_epargne_annee", "annee"),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self) -> str:
        return (
            f"<Epargne("
            f"annee={self.annee}, "
            f"taux_epargne={self.taux_epargne}"
            f")>"
        )
