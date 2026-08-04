from utils.db import connect_to_db
from bronze import load_bronze
from utils.db import get_table, load_table,log_monitoring
from silver import transform_data_f1_4,transform_data_f5_2,transform_f6
import time
from datetime import datetime
from gold import create_dim_date,create_dim_pollutant,create_dim_sector,create_dim_site,create_fact_emission_air
import pandas as pd
from utils.logger import get_logger

#path to csv
f1_path = "data/raw/F1_4_Air_Releases_Facilities.csv"
f5_path = "data/raw/F5_2_LCP_Energy_Emissions.csv"
f6_1_path="data/raw/F6_1_IED_Installations.csv"

#instantication of engine
engine=connect_to_db()


def main():

       logger=get_logger()
       #######################
       # BRONZE layer loading#
       #######################
       #loading to bronze
       logger.info("Start the loading of raw data in the database")
       load_bronze(f1_path,engine,logger=logger)
       logger.info("load of table f1_4 done")
       load_bronze(f5_path,engine,logger=logger)
       logger.info("load of table f5_2 done")
       logger.debug("starting F6_1...")
       try:
              load_bronze(f6_1_path, engine,logger=logger)
              logger.info("Load of F6_1 done")
       except Exception as e:
              logger.error(f"Erreur F6_1 : {e}")
              return
       logger.info("Bronze layer step ended")
       #######################
       # Silver_Tranformation#
       #######################

       #getting_table
       #----------------------------------------------------------------
       query_f1_4="""SELECT * FROM bronze.f1_4_air_releases_facilities
       WHERE "countryName"  = 'Belgium' AND "reportingYear" BETWEEN 2007 AND 2024
       """
       query_f5_2= """SELECT * FROM bronze.f5_2_lcp_energy_emissions 
       WHERE "countryName"='Belgium' """

       query_f6_1="""SELECT * FROM bronze.f6_1_ied_installations
       WHERE "CountryName"='Belgium' AND "installationStatus"='functional'
       """
       logger.info("Getting table from the bronze layer ")
       try: 
              f1_4_silver=get_table(query_f1_4,engine=engine)
              f5_2_silver=get_table(query_f5_2,engine=engine)
              f6_1_silver=get_table(query_f6_1,engine=engine)
       except Exception as e: 
             logger.error(f"❌ failed to get tables from bronze layer: {e}")
             return       
       logger.info("✅  succeeded to get the tables ")
       logger.info("Starting the transformation of f1_4_air_releases_facilities ")

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

       logger.info("Transformation of f1_4_air_releases_facilities done")
       logger.info("Starting the transformation of f5_2_lcp_energy_emission ")
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
       logger.info("Transformation of f5_2_lcp_energy_emission done")
       
       #transrforming f6_1_installation
       logger.info("Starting the transformation of f6_1_installation")
       start_trans=time.perf_counter() #monitoring
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

       elapsed= time.perf_counter()-start_trans #monitoring
       f6_1_monitoring_dict['duration_sec'] = round(elapsed, 2)#monitoring
       f6_1_monitoring_dict['date_transform'] = datetime.now()#monitoring

       #creating monitoring tables
       silver_monitoring=pd.concat([pd.DataFrame([f1_4_monitoring_dict]),
       pd.DataFrame([f5_2_monitoring_dict]),
       pd.DataFrame([f6_1_monitoring_dict])])
       logger.info("Transformation of f6_1_installation done")
       logger.info("Silver layer step ended")
       #######################
       # Gold_layer operation#
       #######################


       #getting table from silver layer
       try: 
              query_silver_table=""" SELECT * FROM silver.f1_emission""" 
              gold_f1_4=get_table(query_silver_table,engine)
       except Exception as e:
             logger.error(f"❌ failed to get the table from silver layer:{e}")
             return

       logger.info("✅  succeeded to get the table from silver layer")

       #create dim date
       logger.info("starting the creation of dim_date table")
       start_create=time.perf_counter()
       dim_date, date_monitoring= create_dim_date()
       elapsed=time.perf_counter() - start_create
       date_monitoring['duration_sec']=elapsed
       date_monitoring['date_transform'] = datetime.now()
       logger.info("✅  succeeded the creation of dim_date table")
       
       #create dim_pollutant
       logger.info("starting the creation of dim_pollutant table")
       start_create=time.perf_counter()
       dim_pollutant,mapping_pollutant,pollutant_monitoring= create_dim_pollutant(gold_f1_4) 
       elapsed=time.perf_counter() - start_create
       pollutant_monitoring['duration_sec']=elapsed
       pollutant_monitoring['date_transform'] = datetime.now()
       logger.info("✅  succeeded the creation of dim_pollutant table")
     
       #create dim_site
       logger.info("starting the creation of dim_site table")
       start_create=time.perf_counter()
       dim_site,mapping_site, site_monitoring= create_dim_site(gold_f1_4)
       elapsed=time.perf_counter() - start_create
       site_monitoring['duration_sec']=elapsed
       site_monitoring['date_transform'] = datetime.now()
       logger.info("✅ succeeded the creation of dim_site table")
       
       #create dim_sector
       logger.info("starting the creation of dim_sector table")
       start_create=time.perf_counter()
       dim_sector, sector_monitoring= create_dim_sector(gold_f1_4)
       elapsed=time.perf_counter() - start_create
       sector_monitoring['duration_sec']=elapsed
       sector_monitoring['date_transform'] = datetime.now()
       logger.info("✅ succeeded the creation of dim_sector table")
       
       #create fact_emission_air
       logger.info("starting the creation of fact_air_emission table")
       start_create=time.perf_counter()
       fact_emission_air, fact_air_monitoring= create_fact_emission_air(gold_f1_4,mapping_site,mapping_pollutant)
       elapsed=time.perf_counter() - start_create
       fact_air_monitoring['duration_sec']=elapsed
       fact_air_monitoring['date_transform'] = datetime.now()
       logger.info("✅ succeeded the creation of fact_air_emission table")
       
       #creating monitoring tables
       logger.info("starting the creation of monitoring table")
       gold_monitoring=pd.concat([pd.DataFrame([date_monitoring]),
       pd.DataFrame([pollutant_monitoring]),
       pd.DataFrame([site_monitoring]),
       pd.DataFrame([sector_monitoring]),
       pd.DataFrame([fact_air_monitoring])])
       logger.info("✅ succeeded the creation of monitoring table")
       logger.info("gold layer steps ended")
 # #################################################
# loading transformed table to postgresql server #
###################################################
       #loading table in silver layer SQL 
       load_table(f1_4_emission,table_name="f1_emission", schema="silver",logger=logger,engine=engine)
       load_table(f5_2_energy_emission,"f5_energy",schema="silver",logger=logger,engine=engine)
       load_table(f6_1_installation,"f6_installation",schema="silver",logger=logger,engine=engine)

       #loading table in gold layer SQL 
       try: 
              load_table(dim_date, 'dim_date','gold',logger=logger,engine=engine)
              load_table(dim_pollutant, 'dim_pollutant','gold',logger=logger,engine=engine)
              load_table(dim_site, 'dim_site','gold',logger=logger,engine=engine)
              load_table(dim_sector, 'dim_sector','gold',logger=logger,engine=engine)
              load_table(fact_emission_air,'fact_emissions_air','gold',logger=logger,engine=engine)
       except Exception as e: 
              logger.error(f"Failed to load table :{e}")
              return
# #################################################
# monitoring                                      #
###################################################      
       
       silver_monitoring['run_timestamp'] = pd.Timestamp.now()
       gold_monitoring['run_timestamp'] = pd.Timestamp.now()

#
       try:
              #monitoring silver
              log_monitoring(silver_monitoring,"silver_monitoring", "monitoring", logger=logger,engine=engine, truncate=False, if_exist="append")

              #monitoring gold
              log_monitoring(gold_monitoring,'gold_monitoring','monitoring',logger=logger,engine=engine, truncate=False,if_exist="append")
       except Exception as e: 
              logger.warning(f"failed to load monitoring table: {e}")

       logger.info("pipeline done")
if __name__ == "__main__":
    main()