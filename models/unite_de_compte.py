from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from db import Base


class UniteDeCompte(Base):
    __tablename__ = "unite_de_compte"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique de l'unité de compte"
    )

    # =====================================================
    # DONNÉES MÉTIER
    # =====================================================
    libelle = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="Libellé de l'unité de compte (Victime, Infraction, etc.)"
    )

    # =====================================================
    # RELATIONS
    # =====================================================
    faits_securite = relationship(
        "FaitSecurite",
        back_populates="unite_de_compte",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # INDEX
    # =====================================================
    __table_args__ = (
        Index(
            "ix_unite_de_compte_libelle",
            "libelle"
        ),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self) -> str:
        return (
            f"<UniteDeCompte("
            f"id={self.id}, "
            f"libelle='{self.libelle}'"
            f")>"
        )
