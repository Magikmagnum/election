from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from db import Base


class Indicateur(Base):
    __tablename__ = "indicateur"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique de l'indicateur de sécurité"
    )

    # =====================================================
    # DONNÉES MÉTIER
    # =====================================================
    libelle = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Libellé officiel de l'indicateur de sécurité"
    )

    # =====================================================
    # RELATIONS
    # =====================================================
    faits_securite = relationship(
        "FaitSecurite",
        back_populates="indicateur",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # INDEX
    # =====================================================
    __table_args__ = (
        Index(
            "ix_indicateur_libelle",
            "libelle"
        ),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self) -> str:
        return (
            f"<Indicateur("
            f"id={self.id}, "
            f"libelle='{self.libelle}'"
            f")>"
        )
