from sqlalchemy import (
    Column,
    Integer,
    String,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from db import Base


class Sexe(Base):
    __tablename__ = "sexe"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique du sexe"
    )

    # =====================================================
    # DONNÉES MÉTIER
    # =====================================================
    code = Column(
        String(10),
        nullable=False,
        unique=True,
        comment="Code du sexe : ENSEMBLE, H, F"
    )

    # =====================================================
    # RELATIONS
    # =====================================================
    populations = relationship(
        "PopulationDepartement",
        back_populates="sexe",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # CONTRAINTES
    # =====================================================
    __table_args__ = (
        CheckConstraint(
            "code IN ('ENSEMBLE', 'H', 'F')",
            name="ck_sexe_code_valide"
        ),
    )

    def __repr__(self) -> str:
        return f"<Sexe(code='{self.code}')>"
