import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import pandas as pd


def connect_to_db():

    #loading of the .env
    load_dotenv()

    #paramters
    DB_USER=os.getenv('DB_USER')
    DB_PASSWORD=os.getenv('DB_PASSWORD')
    DATABASE=os.getenv('DATABASE')
    DB_HOST=os.getenv('DB_HOST')
    DB_PORT=os.getenv('DB_PORT')

    params={"User":DB_USER,
            "password":DB_PASSWORD,
            "database":DATABASE,
            "host":DB_HOST,
            "port":DB_PORT
    }

    for key in params:
        if params[key] is None:
            raise ValueError (f"the parameter {key} is not defined in .env")

    print("parameters of DATABASE sucessfuly loaded ")

    #instanciation of the engine
    engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE}')

    #test of connection
    with engine.connect() as conn:
        print("connection sucessful")

    return engine


def get_table(query,engine):

    df = pd.read_sql(query, con=engine)

    return df

def load_table(df,table_name,schema,engine,logger, truncate=True,if_exist="append"):
   
    if truncate==True: 
            sql_state=text(f"TRUNCATE TABLE {schema}.{table_name} CASCADE;")

            with engine.connect()as conn:
                conn.execute(sql_state)
                conn.commit()

            
    df.to_sql(table_name,con=engine,schema=schema, if_exists=if_exist,index=False, chunksize=1000)
    logger.info( f"succeeded to load  {schema}.{table_name}")

def log_monitoring(df,table_name,schema, engine, logger, if_exist="append", truncate=False):
    
    load_table(df,table_name,schema, engine,logger, truncate=truncate, if_exist=if_exist)

    logger.info(f"succeeded to add {table_name}monitoring table in database")
