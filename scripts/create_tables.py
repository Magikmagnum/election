from db import engine
from db import Base

# Importer les modèles pour les enregistrer
import models

# Supprime toutes les tables (pour environnement de test)
Base.metadata.drop_all(bind=engine)

# Crée toutes les tables selon le nouveau schéma
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès")
