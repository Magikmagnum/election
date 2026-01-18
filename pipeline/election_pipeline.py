# %% [markdown]
# # Préparation des résultats électoraux

# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sqlalchemy.orm import Session
from db import SessionLocal
from models import ResultatElection, Candidat, Departement, Election, ElectionStats

# Création de la session
session = SessionLocal()

# %% [markdown]
# ## 1. Récupération des résultats avec relations

# %%
results = session.query(
    ResultatElection.id.label("resultat_id"),
    ResultatElection.nb_voix,
    ResultatElection.code_dept,
    Departement.nom_dept,
    ResultatElection.election_id,
    Election.date.label("date_election"),
    Election.type_election,
    Election.tour,
    Candidat.id.label("candidat_id"),
    Candidat.nom.label("nom_candidat"),
    Candidat.prenom.label("prenom_candidat"),
    Candidat.sexe,
).join(Candidat, ResultatElection.candidat_id == Candidat.id
).join(Departement, ResultatElection.code_dept == Departement.code_dept
).join(Election, ResultatElection.election_id == Election.id
).all()

# Conversion en DataFrame et transformation Enum en string
df_resultats = pd.DataFrame([r._asdict() for r in results])
df_resultats["sexe_candidat"] = df_resultats["sexe"].apply(lambda x: x.value)
df_resultats.drop(columns=["sexe"], inplace=True)
df_resultats["type_election"] = df_resultats["type_election"].apply(lambda x: x.value)

# %% [markdown]
# ## 2. Mapping candidats → partis

# %%
partis = {
    'JOLY': 'EELV', 'LE PEN': 'RN', 'SARKOZY': 'LR', 'MÉLENCHON': 'LFI', 'POUTOU': 'NPA',
    'ARTHAUD': 'LO', 'CHEMINADE': 'SP', 'BAYROU': 'MoDem', 'DUPONT-AIGNAN': 'DF', 
    'HOLLANDE': 'PS', 'MACRON': 'LREM', 'FILLON': 'LR', 'HAMON': 'PS', 'LASSALLE': 'Résistons !',
    'ASSELINEAU': 'UPR', 'ROUSSEL': 'PCF', 'ZEMMOUR': 'Reconquête', 'HIDALGO': 'PS', 'JADOT': 'EELV',
    'PÉCRESSE': 'LR'
}
df_resultats['parti'] = df_resultats['nom_candidat'].map(partis)

# %% [markdown]
# ## 3. Récupération des statistiques électorales par département

# %%
stats = session.query(
    ElectionStats.election_id,
    ElectionStats.code_dept,
    ElectionStats.nb_inscrits,
    ElectionStats.nb_votants,
    ElectionStats.nb_abstentions,
    ElectionStats.nb_blancs_nuls
).all()
df_stats = pd.DataFrame([s._asdict() for s in stats])

# Merge avec les résultats
df_resultats = df_resultats.merge(df_stats, on=["election_id", "code_dept"], how="left")

# %% [markdown]
# ## 4. Calcul du pourcentage de voix

# %%
df_resultats['pct_voix'] = (df_resultats['nb_voix'] / df_resultats['nb_votants']) * 100
df_resultats['pct_voix'] = df_resultats['pct_voix'].round(2)

# %% [markdown]
# ## 5. Extraction de l'année et fusion prénom + nom

# %%
df_resultats['date_election'] = pd.to_datetime(df_resultats['date_election'])
df_resultats['annee'] = df_resultats['date_election'].dt.year

df_resultats['nom_candidat'] = df_resultats['prenom_candidat'] + ' ' + df_resultats['nom_candidat']

# %% [markdown]
# ## 6. Calcul des pourcentages d'abstentions et de votes blancs/nuls

# %%
df_resultats['pct_abstentions'] = (df_resultats['nb_abstentions'] / df_resultats['nb_votants']) * 100
df_resultats['pct_blancs_nuls'] = (df_resultats['nb_blancs_nuls'] / df_resultats['nb_votants']) * 100


# %% [markdown]
# ## 7. Suppression des colonnes inutiles

# %%
colonnes_a_supprimer = [
    "nom_dept",
    "election_id",
    "prenom_candidat",
    "type_election",
    "sexe_candidat",
    'nb_votants',
    'nb_voix',
    'nb_inscrits',
    'date_election',
    'nb_abstentions',
    'nb_blancs_nuls',
    'nb_votants'
]
df_resultats = df_resultats.drop(columns=colonnes_a_supprimer)


# %% [markdown]
# ## 8. Pivot pour avoir une colonne par parti

# %%
df_pivot = df_resultats.pivot_table(
    index=['code_dept', 'tour', 'annee'],  # ligne = département + tour + année
    columns='parti',                        # colonne par parti
    values='pct_voix',                      # valeur = pourcentage de voix
    fill_value=0                             # si un parti n’a pas de voix = 0
).reset_index()

# Vérification
df_pivot.head()
