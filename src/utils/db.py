import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

#loading of .env
def connect_to_db():
    load_dotenv() #loading of the .env

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
