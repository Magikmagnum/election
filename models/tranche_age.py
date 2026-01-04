from sqlalchemy import Column, Integer, CheckConstraint, Index
from sqlalchemy.orm import relationship
from db import Base


class TrancheAge(Base):
    __tablename__ = "tranche_age"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique de la tranche d'âge"
    )

    # =====================================================
    # BORNES D'ÂGE
    # =====================================================
    age_min = Column(
        Integer,
        nullable=False,
        comment="Âge minimum inclus"
    )

    age_max = Column(
        Integer,
        nullable=True,
        comment="Âge maximum inclus (NULL si tranche ouverte)"
    )


    # =====================================================
    # RELATIONS
    # =====================================================
    populations = relationship(
        "PopulationDepartement",
        back_populates="tranche_age",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # CONTRAINTES & INDEX
    # =====================================================
    __table_args__ = (
        CheckConstraint(
            "age_min >= 0",
            name="ck_tranche_age_min_positive"
        ),
        CheckConstraint(
            "age_max IS NULL OR age_max >= age_min",
            name="ck_tranche_age_max_superieur_min"
        ),
        Index(
            "ix_tranche_age_min_max",
            "age_min",
            "age_max"
        ),
    )

    def __repr__(self) -> str:
        return f"<TrancheAge(id={self.id}, age_min={self.age_min}, age_max={self.age_max})>"
