import pandas as pd
import os



def transform_data_f1_4(df,col):


    df_transformed=df[col].copy()
    nb_null_in= df_transformed.isnull().sum().sum()
    df_transformed=df_transformed.rename(str.lower,axis='columns').rename(columns={'releases':"emitted_co2_kg"})

    print("avant:", df_transformed['city'].isna().sum())
    df_transformed=df_transformed.fillna(value={"eprtr_sectorcode":'unknown','eprtr_sectorname':'unknown','city':'unknown'})
    print("après:", df_transformed['city'].isna().sum())
    nb_null_out=df_transformed.isnull().sum().sum()


    nb_col_out=len(df_transformed.columns)

    monitoring_dic={
    'table': 'silver_f1_4',
    'nb_null_in': nb_null_in,
    'nb_null_out': nb_null_out,
    'nb_col_out': nb_col_out,
    }

    return (df_transformed,monitoring_dic)

def transform_data_f5_2(df,column):

    return df

def load_table(df, table_name, engine,schema):

    return df
