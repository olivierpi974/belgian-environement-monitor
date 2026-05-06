from utils.db import connect_to_db
from bronze import load_bronze

#path to csv
f1_path = "data/raw/F1_4_Air_Releases_Facilities.csv"
f5_path = "data/raw/F5_2_LCP_Energy_Emissions.csv"
f6_1_path="data/raw/F6_1_IED_Installations.csv"

#instantication of engine
engine=connect_to_db()

#loading to bronze
load_bronze(f1_path,engine)
load_bronze(f5_path,engine)

print("starting F6_1...")
try:
    load_bronze(f6_1_path, engine)
except Exception as e:
    print(f"Erreur F6_1 : {e}")
