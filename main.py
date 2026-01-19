# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import missingno as msno
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

# %%
def load_and_describe(file_path, n_rows=5):

    try:
        # Détection du type de fichier
        if file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            raise ValueError("Format de fichier non supporté. Utiliser .xlsx, .xls ou .csv")
        
        # Affichage du DataFrame et infos
        print("\n--- Aperçu des premières lignes ---")
        print(df.head(n_rows))
        
        print("\n--- Informations générales ---")
        print(df.info())
        
        print("\n--- Statistiques descriptives ---")
        print(df.describe(include='all'))
        
        # Affichage du pourcentage de valeurs manquantes
        missing_pct = df.isnull().mean() * 100
        print("\n--- Pourcentage de valeurs manquantes par colonne ---")
        print(missing_pct[missing_pct > 0])
        
        return df
    
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_path}' est introuvable.")
    except ValueError as ve:
        print(f"Erreur : {ve}")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

# Exemple d'utilisation
df = load_and_describe('./data/securite/securite.xlsx')



# %%
