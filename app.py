import streamlit as st
import pandas as pd
import joblib

# ================================
# Fonction de prédiction
# ================================
def predire_votes_departement(
    population_totale,
    pct_femmes,
    pct_hommes,
    pct_jeunes,
    pct_seniors,
    taux_chomage,
    taux_pour_mille,
    croissance_total_entreprises,
    solde_commercial,
    taux_epargne,
    prix_consommation,
    pre_depenses,
    pct_immigration,
    model_path="modele_votes_departement_best.pkl"
):
    model = joblib.load(model_path)
    FEATURES = [
        'population_totale','pct_femmes','pct_hommes','pct_jeunes','pct_seniors',
        'taux_chomage','taux_pour_mille','croissance_total_entreprises','solde_commercial',
        'taux_epargne','prix_consommation','pre_depenses','pct_immigration'
    ]
    X_new = pd.DataFrame([[
        population_totale,
        pct_femmes,
        pct_hommes,
        pct_jeunes,
        pct_seniors,
        taux_chomage,
        taux_pour_mille,
        croissance_total_entreprises,
        solde_commercial,
        taux_epargne,
        prix_consommation,
        pre_depenses,
        pct_immigration
    ]], columns=FEATURES)

    y_pred = model.predict(X_new)[0]

    CANDIDATS_COLS = [
        'DF', 'EELV', 'LFI', 'LO', 'LR', 'LREM', 'MoDem',
        'NPA', 'PCF', 'PS', 'RN', 'Reconquête',
        'Résistons !', 'SP', 'UPR'
    ]
    resultats = pd.Series(y_pred, index=CANDIDATS_COLS)
    resultats = resultats.clip(lower=0)
    resultats = resultats / resultats.sum() * 100
    return resultats.sort_values(ascending=False)

# ================================
# Interface Streamlit
# ================================
st.title("Prédiction des votes par département")
st.write("Entrez les caractéristiques socio-économiques du département pour obtenir les pourcentages de votes par candidat.")

# Inputs utilisateur
population_totale = st.number_input("Population totale", value=650000)
pct_femmes = st.number_input("% Femmes", value=51.5)
pct_hommes = st.number_input("% Hommes", value=48.5)
pct_jeunes = st.number_input("% Jeunes (0-19 ans)", value=24.0)
pct_seniors = st.number_input("% Seniors (60+ ans)", value=27.0)
taux_chomage = st.number_input("Taux de chômage (%)", value=8.9)
taux_pour_mille = st.number_input("Taux pour mille", value=45.2)
croissance_total_entreprises = st.number_input("Croissance totale entreprises", value=0.03)
solde_commercial = st.number_input("Solde commercial", value=-0.12)
taux_epargne = st.number_input("Taux d'épargne (%)", value=15.5)
prix_consommation = st.number_input("Prix consommation", value=112.4)
pre_depenses = st.number_input("Pré-dépenses", value=98.1)
pct_immigration = st.number_input("% Immigration", value=9.4)

# Bouton pour prédire
if st.button("Prédire les votes"):
    resultats = predire_votes_departement(
        population_totale,
        pct_femmes,
        pct_hommes,
        pct_jeunes,
        pct_seniors,
        taux_chomage,
        taux_pour_mille,
        croissance_total_entreprises,
        solde_commercial,
        taux_epargne,
        prix_consommation,
        pre_depenses,
        pct_immigration
    )
    st.subheader("Résultats de la prédiction (%)")
    st.table(resultats.head(10))  # top 10 candidats pour plus de lisibilité
