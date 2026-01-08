from sqlalchemy import Column, Integer, Float, Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Immigration(Base):
    __tablename__ = "immigration"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique de l'année d'immigration"
    )

    # =====================================================
    # DONNÉES MÉTIER
    # =====================================================
    annee = Column(
        Integer,
        nullable=False,
        unique=True,
        comment="Année des données d'immigration"
    )

    pct_immigration = Column(
        Float,
        nullable=False,
        comment="Part des immigrés en pourcentage"
    )

    # =====================================================
    # RELATIONS
    # =====================================================


    # =====================================================
    # INDEX
    # =====================================================
    __table_args__ = (
        Index("ix_immigration_annee", "annee"),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self) -> str:
        return (
            f"<Immigration("
            f"annee={self.annee}, "
            f"pct_immigration={self.pct_immigration}"
            f")>"
        )
