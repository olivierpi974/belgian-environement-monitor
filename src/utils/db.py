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
    HOST=os.getenv('HOST')
    PORT=os.getenv('PORT')

    params={"User":DB_USER,
            "password":DB_PASSWORD,
            "database":DATABASE,
            "host":HOST,
            "port":PORT
    }

    for key in params:
        if params[key] is None:
            raise ValueError (f"the parameter {key} is not defined in .env")

    print("parameters of DATABASE sucessfuly loaded ")

    #instanciation of the engine
    engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{HOST}:{PORT}/{DATABASE}')

    #test of connection
    with engine.connect() as conn:
        print("connection sucessful")

    return engine


def get_table(query,engine):

    df = pd.read_sql(query, con=engine)

    return df

def load_table(df,table_name,schema,engine,truncate=True):
   
    if truncate==True: 
            sql_state=text(f"TRUNCATE TABLE {schema}.{table_name};")

            with engine.connect()as conn:
                conn.execute(sql_state)
                conn.commit()

            
    df.to_sql(table_name,con=engine,schema=schema, if_exists='append',index=False, chunksize=1000)
    print( f"load of {schema}.{table_name} done")

def log_monitoring(df,table_name,schema, engine):
    
    load_table(df,table_name,schema, engine,truncate=True)

    print("monitoring is done")
