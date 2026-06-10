import pandas as pd
import time
import os
import datetime

def load_bronze(path,engine, logger):
    date= datetime.datetime.now()
    start=time.perf_counter()
    #loading the dataframe from the csv file
    table_name=os.path.splitext(os.path.basename(path))[0].lower()
    logger.debug(f"reading {table_name}.csv...")
    df=pd.read_csv(path,sep=',',low_memory=False)
    logger.info(f"{table_name}.csv ✅successfully loaded : {len(df)} lignes")

    # sending the dataframe to the database
    df.to_sql(table_name, con=engine,schema="bronze", if_exists="replace",index=False,chunksize=10000)

    #coubting the ingestion time
    elapsed= time.perf_counter()-start
    logger.info("✅loading done")
    logger.info(f"{table_name}|nombre de colonnes:{len(df.columns)}|{len(df)} lignes| {elapsed:.2f} s|date_ingest:{date}")

    log_dict={'table':table_name,
              "nb_lines":len(df),
              "date_ingest":date,
              "duration_sec":round(elapsed,2),
              "nb_cols":len(df.columns)}
    logger.debug("creating the monitoring table")
    df_log=pd.DataFrame([log_dict])

    df_log.to_sql("bronze_monitoring", con=engine,schema="monitoring", if_exists="append",index=False,chunksize=10000)
    logger.debug("loading the monitoring table")
    return log_dict
