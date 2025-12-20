from sqlalchemy import (
    Column,
    String,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from db import Base


class Departement(Base):
    __tablename__ = "departements"

    code_dept = Column(
        String(2),
        primary_key=True
    )

    nom_dept = Column(
        String(100),
        nullable=False
    )

    # Relation vers les stats électorales
    stats = relationship(
        "ElectionStats",
        back_populates="departement",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Empêche nom vide
        CheckConstraint("length(nom_dept) > 0", name="ck_nom_dept_non_vide"),

        # Index pour requêtes analytiques
        Index("ix_departements_nom", "nom_dept"),
    )

    def __repr__(self):
        return f"<Departement(code='{self.code_dept}', nom='{self.nom_dept}')>"
