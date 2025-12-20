from utils.election_dataframe import ElectionDataFrame
from utils.election_importer import ElectionImporter
from datetime import date
from enums.type_election import TypeElection

# Préparation des données
edf = ElectionDataFrame("./elections/presidentielles-2022-2.xlsx")

# Importer BDD
importer = ElectionImporter()

importer.import_departements(edf.df_departement)

election = importer.get_or_create_election(
    date(2022, 4, 24),
    TypeElection.PRESIDENTIELLE,
    tour=2
)

importer.import_stats(edf.df_stat_elections, election.id)
importer.import_candidats_resultats(edf.df_candidat_resultat, election.id)

print("✅ Import terminé avec succès")
