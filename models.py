from sqlalchemy import Column, String, Integer, ForeignKey, Date, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

# Enum pour le type d'élection
class TypeElection(enum.Enum):
    PRESIDENTIELLE = "Présidentielle"
    LEGISLATIVE = "Législative"
    MUNICIPALE = "Municipale"
    REGIONALE = "Régionale"
    AUTRE = "Autre"


# Enum pour le sexe
class SexeEnum(enum.Enum):
    M = "Masculin"
    F = "Féminin"


class Departement(Base):
    __tablename__ = 'departements'
    
    code_dept = Column(String(2), primary_key=True)
    nom_dept = Column(String(100), nullable=False)
    
    stats = relationship("ElectionStats", back_populates="departement")
    
    def __repr__(self):
        return f"<Departement(code_dept='{self.code_dept}', nom_dept='{self.nom_dept}')>"
    

class Election(Base):
    __tablename__ = 'elections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    type_election = Column(Enum(TypeElection), nullable=False)
    tour = Column(Integer, nullable=False, default=1)
    
    stats = relationship("ElectionStats", back_populates="election")
    candidats = relationship("Candidat", back_populates="election")
    
    def __repr__(self):
        return f"<Election(id={self.id}, date={self.date}, type_election={self.type_election})>"
    

class ElectionStats(Base):
    __tablename__ = 'election_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code_dept = Column(String(2), ForeignKey('departements.code_dept'), nullable=False)
    election_id = Column(Integer, ForeignKey('elections.id'), nullable=False)
    
    nb_inscrits = Column(Integer, nullable=False)
    nb_abstentions = Column(Integer, nullable=False)
    nb_votants = Column(Integer, nullable=False)
    nb_blancs = Column(Integer, nullable=False)
    nb_nuls = Column(Integer, nullable=False)
    
    departement = relationship("Departement", back_populates="stats")
    election = relationship("Election", back_populates="stats")
    
    def __repr__(self):
        return (f"<ElectionStats(code_dept='{self.code_dept}', election_id={self.election_id}, "
                f"nb_inscrits={self.nb_inscrits}, nb_abstentions={self.nb_abstentions}, "
                f"nb_votants={self.nb_votants}, nb_blancs={self.nb_blancs}, nb_nuls={self.nb_nuls})>")

class Candidat(Base):
    __tablename__ = 'candidats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    election_id = Column(Integer, ForeignKey('elections.id'), nullable=False)
    
    sexe = Column(Enum(SexeEnum), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    nb_voix = Column(Integer, nullable=False)
    
    election = relationship("Election", back_populates="candidats")
    
    def __repr__(self):
        return (f"<Candidat(nom='{self.nom}', prenom='{self.prenom}', sexe={self.sexe}, "
                f"election_id={self.election_id}, nb_voix={self.nb_voix})>")