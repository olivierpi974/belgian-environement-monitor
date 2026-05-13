from utils.db import connect_to_db
from bronze import load_bronze
from utils.db import get_table, load_table,log_monitoring
from silver import transform_data_f1_4,transform_data_f5_2,transform_f6
import time
from datetime import datetime

#path to csv
f1_path = "data/raw/F1_4_Air_Releases_Facilities.csv"
f5_path = "data/raw/F5_2_LCP_Energy_Emissions.csv"
f6_1_path="data/raw/F6_1_IED_Installations.csv"

#instantication of engine
engine=connect_to_db()

#######################
# BRONZE layer loading#
#######################
#loading to bronze
print("starting loading of table")
load_bronze(f1_path,engine)
print("load of table f1_4 done")
load_bronze(f5_path,engine)
print("load of table f5_2 done")
print("starting F6_1...")
try:
    load_bronze(f6_1_path, engine)
except Exception as e:
    print(f"Erreur F6_1 : {e}")
print("Load of F6_1 done")
#######################
# Silver_Tranformation#
#######################

#getting_table
#----------------------------------------------------------------
query_f1_4="""SELECT * FROM bronze.f1_4_air_releases_facilities
    WHERE "countryName"  = 'Belgium' AND "reportingYear" BETWEEN 2016 AND 2024
"""
query_f5_2= """SELECT * FROM bronze.f5_2_lcp_energy_emissions 
WHERE "countryName"='Belgium' """

query_f6_1="""SELECT * FROM bronze.f6_1_ied_installations
WHERE "CountryName"='Belgium' AND "installationStatus"='functional'
"""

f1_4_silver=get_table(query_f1_4,engine=engine)
f5_2_silver=get_table(query_f5_2,engine=engine)
f6_1_silver=get_table(query_f6_1,engine=engine)


#transforming f1_4_silver
#---------------------------------------------------------------------
col_to_keep=['reportingYear', 'EPRTR_SectorCode',
       'EPRTR_SectorName', 'FacilityInspireId',
       'facilityName', 'city', 'Longitude', 'Latitude', 'Pollutant',
       'Releases']

start_trans=time.perf_counter() #monitoring
f1_4_emission, f1_4_monitoring_dict= transform_data_f1_4(f1_4_silver,col_to_keep)

elapsed= time.perf_counter()-start_trans #monitoring
f1_4_monitoring_dict['duration_sec'] = round(elapsed, 2)#monitoring
f1_4_monitoring_dict['date_transform'] = datetime.now()#monitoring

#transforming f5_2_silver
#---------------------------------------------------------------------
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

start_trans=time.perf_counter() #monitoring

f5_2_energy_emission,f5_2_monitoring_dict=transform_data_f5_2(f5_2_silver,
                                                              col=col_f5_2_to_keep,
                                                              col_filter=col_filter,
                                                              col_combustible=combustible,
                                                              index=index,
                                                              col_pivot=col_pivot,
                                                              value_pivot=value_pivot,
                                                              normalize_col=col_rename)

elapsed= time.perf_counter()-start_trans #monitoring
f5_2_monitoring_dict['duration_sec'] = round(elapsed, 2)#monitoring
f5_2_monitoring_dict['date_transform'] = datetime.now()#monitoring

#transrforming f6_1_installation
f6_col_to_keep=['reportingYear',
       'parent_facilityInspireId',
       'InstallationInspireId',
       'City_of_Facility',
       'Longitude', 'Latitude']

col_to_normalize='city_of_facility'
col_to_fill_na='city_of_facility'
f6_1_installation, f6_1_monitoring_dict=transform_f6(
                            f6_1_silver,
                            f6_col_to_keep,
                            col_to_normalize,
                            col_to_fill_na)

# #################################################
# loading transformed table to postgresql server #
###################################################

load_table(f1_4_emission,table_name="f1_emission", schema="silver",engine=engine)
load_table(f5_2_energy_emission,"f5_energy",schema="silver",engine=engine)
load_table(f6_1_installation,"f6_installation",schema="silver",engine=engine)


# #################################################
# monitoring                                      #
###################################################

log_monitoring(f1_4_monitoring_dict,"silver_monitoring", "monitoring", engine=engine)
log_monitoring(f5_2_monitoring_dict,"silver_monitoring","monitoring",engine=engine)
log_monitoring(f6_1_monitoring_dict,"silver_monitoring","monitoring",engine=engine)