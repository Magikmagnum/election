import os
import pandas as pd
from sqlalchemy import inspect
from db.session import SessionLocal

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

engine = SessionLocal().bind
inspector = inspect(engine)

tables = inspector.get_table_names()

print(f"📦 Tables trouvées : {tables}")

for table in tables:
    print(f"➡️ Export de {table}...")
    df = pd.read_sql_table(table, con=engine)
    df.to_csv(f"{EXPORT_DIR}/{table}.csv", index=False)

print("✅ Export CSV complet terminé")