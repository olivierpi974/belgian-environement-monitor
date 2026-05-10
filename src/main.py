from utils.db import connect_to_db
from bronze import load_bronze
from utils.db import get_table, load_table,log_monitoring
from silver import transform_data_f1_4,transform_data_f5_2
import time
from datetime import datetime

#path to csv
f1_path = "data/raw/F1_4_Air_Releases_Facilities.csv"
f5_path = "data/raw/F5_2_LCP_Energy_Emissions.csv"
f6_1_path="data/raw/F6_1_IED_Installations.csv"

#instantication of engine
engine=connect_to_db()

# #loading to bronze
# load_bronze(f1_path,engine)
# load_bronze(f5_path,engine)

# print("starting F6_1...")
# try:
#     load_bronze(f6_1_path, engine)
# except Exception as e:
#     print(f"Erreur F6_1 : {e}")

#getting_table
query_f1_4="""SELECT * FROM bronze.f1_4_air_releases_facilities
    WHERE "countryName"  = 'Belgium' AND "Pollutant"='Carbon dioxide (CO2)' AND "reportingYear" BETWEEN 2016 AND 2024
"""
query_f5_2= """SELECT * FROM bronze.f5_2_lcp_energy_emissions 
WHERE "countryName"='Belgium' """

f1_4_silver=get_table(query_f1_4,engine=engine)
f5_2_silver=get_table(query_f5_2,engine=engine)

#transforming f1_4_silver
col_to_keep=['reportingYear', 'EPRTR_SectorCode',
       'EPRTR_SectorName', 'FacilityInspireId',
       'facilityName', 'city', 'Longitude', 'Latitude',
       'Releases']


start_trans=time.perf_counter()
f1_4_emission, monitoring_dict= transform_data_f1_4(f1_4_silver,col_to_keep)

elapsed= time.perf_counter()-start_trans
monitoring_dict['duration_sec'] = round(elapsed, 2)
monitoring_dict['date_transform'] = datetime.now()

#transforming f5_2_silver
col_f5_2_to_keep=['reportingYear', 'LCPInspireId',
       'installationPartName',
       'City_Of_Facility', 'Longitude',
       'Latitude', 'featureType', 'unit', 'featureValue']
combustible=['NaturalGas', 'LiquidFuels', 'OtherGases', 'Biomass', 'Lignite', 'Coal', 'OtherSolidFuels', 'Peat']
col_filter='featureType'
index=['reportingYear','LCPInspireId','installationPartName',
       'City_Of_Facility', 'Longitude', 'Latitude']
col_rename=['installationpartname','city_of_facility']
col_pivot='featureType'
value_pivot='featureValue'

f5_2_energy_emission,f5_2_monitoring_dict=transform_data_f5_2(f5_2_silver,col=col_f5_2_to_keep,col_filter=col_filter,col_combustible=combustible,index=index,col_pivot=col_pivot,value_pivot=value_pivot,normalize_col=col_rename)
print(f5_2_energy_emission)
print(f5_2_monitoring_dict)
# #loading transformed table to postgresql server
# load_table(f1_4_emission,table_name="f1_emission", schema="silver",engine=engine)

# #loading monitoring table to postgresql server
# log_monitoring(monitoring_dict,"silver_monitoring", "monitoring", engine=engine)

#getting_table

#transforming F5_2
