from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Float,
    CheckConstraint,
    Index
)
from sqlalchemy.orm import relationship
from db import Base


class FaitSecurite(Base):
    __tablename__ = "fait_securite"

    # =====================================================
    # IDENTIFIANT
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant technique du fait de sécurité"
    )

    # =====================================================
    # DONNÉES MÉTIER
    # =====================================================
    nombre = Column(
        Integer,
        nullable=False,
        comment="Nombre brut de faits observés pour l'indicateur"
    )

    taux_pour_mille = Column(
        Float,
        nullable=False,
        comment="Taux pour 1000 habitants (normalisé par la population INSEE)"
    )

    # =====================================================
    # CLÉS ÉTRANGÈRES
    # =====================================================
    indicateur_id = Column(
        Integer,
        ForeignKey("indicateur.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Référence vers l'indicateur de sécurité"
    )

    unite_de_compte_id = Column(
        Integer,
        ForeignKey("unite_de_compte.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Référence vers l'unité de compte (Victime, Infraction, etc.)"
    )

    # =====================================================
    # RELATIONS ORM
    # =====================================================
    indicateur = relationship(
        "Indicateur",
        back_populates="faits_securite"
    )

    unite_de_compte = relationship(
        "UniteDeCompte",
        back_populates="faits_securite"
    )

    # =====================================================
    # CONTRAINTES & INDEX
    # =====================================================
    __table_args__ = (
        CheckConstraint(
            "nombre >= 0",
            name="ck_fait_securite_nombre_positif"
        ),
        CheckConstraint(
            "taux_pour_mille >= 0",
            name="ck_fait_securite_taux_positif"
        ),
        Index(
            "ix_fait_securite_indicateur",
            "indicateur_id"
        ),
        Index(
            "ix_fait_securite_unite",
            "unite_de_compte_id"
        ),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self) -> str:
        return (
            f"<FaitSecurite("
            f"id={self.id}, "
            f"indicateur_id={self.indicateur_id}, "
            f"unite_de_compte_id={self.unite_de_compte_id}, "
            f"nombre={self.nombre}, "
            f"taux_pour_mille={self.taux_pour_mille}"
            f")>"
        )
