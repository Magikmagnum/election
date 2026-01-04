from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import relationship
from db import Base


class PopulationDepartement(Base):
    __tablename__ = "population_departement"

    # =====================================================
    # IDENTIFIANT TECHNIQUE
    # =====================================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique de la population par département, sexe et tranche d'âge"
    )

    # =====================================================
    # RELATIONS
    # =====================================================
    departement_code = Column(
        String(2),
        ForeignKey("departements.code_dept", ondelete="CASCADE"),
        nullable=False,
        comment="Référence au département"
    )

    sexe_id = Column(
        Integer,
        ForeignKey("sexe.id", ondelete="CASCADE"),
        nullable=False,
        comment="Référence au sexe (ENSEMBLE, H, F)"
    )

    tranche_age_id = Column(
        Integer,
        ForeignKey("tranche_age.id", ondelete="CASCADE"),
        nullable=False,
        comment="Référence à la tranche d'âge"
    )

    annee = Column(
        Integer,
        nullable=False,
        comment="Année de la population"
    )

    population = Column(
        Integer,
        nullable=False,
        comment="Nombre de personnes"
    )

    # =====================================================
    # RELATIONS ORM
    # =====================================================
    departement = relationship("Departement", back_populates="populations")
    sexe = relationship("Sexe")
    tranche_age = relationship("TrancheAge")

    # =====================================================
    # CONTRAINTES
    # =====================================================
    __table_args__ = (
        UniqueConstraint(
            "departement_code",
            "sexe_id",
            "tranche_age_id",
            "annee",
            name="uq_population_departement"
        ),
    )

    # =====================================================
    # REPRÉSENTATION
    # =====================================================
    def __repr__(self):
        return (
            f"<PopulationDepartement("
            f"departement='{self.departement_code}', "
            f"sexe='{self.sexe.code}', "
            f"tranche_age_id={self.tranche_age_id}, "
            f"annee={self.annee}, "
            f"population={self.population})>"
        )
