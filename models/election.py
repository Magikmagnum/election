from sqlalchemy import (
    Column,
    Integer,
    Date,
    Enum,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from db import Base
from enums.type_election import TypeElection


class Election(Base):
    __tablename__ = "elections"

    id = Column(Integer, primary_key=True, autoincrement=True)

    date = Column(Date, nullable=False)

    type_election = Column(
        Enum(
            TypeElection,
            name="type_election_enum",
            native_enum=True
        ),
        nullable=False
    )

    tour = Column(Integer, nullable=False)

    stats = relationship(
        "ElectionStats",
        back_populates="election",
        cascade="all, delete-orphan"
    )

    resultats = relationship(
        "ResultatElection",
        back_populates="election",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Une seule élection par date / type / tour
        UniqueConstraint(
            "date",
            "type_election",
            "tour",
            name="uq_election_unique"
        ),

        # Règle métier : tour >= 1
        CheckConstraint("tour >= 1", name="ck_tour_min"),

        # Index pour requêtes analytiques
        Index("ix_election_date", "date"),
        Index("ix_election_type", "type_election"),
    )

    def __repr__(self):
        return (
            f"<Election("
            f"id={self.id}, "
            f"type={self.type_election.name}, "
            f"date={self.date}, "
            f"tour={self.tour})>"
        )
