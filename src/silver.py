import pandas as pd
import os



def transform_data_f1_4(df,col):


    df_transformed=df[col].copy()
    nb_null_in= df_transformed.isnull().sum().sum()
    df_transformed=df_transformed.rename(str.lower,axis='columns').rename(columns={'releases':"emitted_co2_kg"})


    df_transformed=df_transformed.fillna(value={'eprtr_sectorname':'unknown','city':'unknown'})

    nb_null_out=df_transformed.isnull().sum().sum()
    nb_rows_out=len(df_transformed)

    nb_col_out=len(df_transformed.columns)

    monitoring_dic={
    'table_name': 'silver_f1_4',
    'nb_rows_out':nb_rows_out,
    'nb_null_in': nb_null_in,
    'nb_null_out': nb_null_out,
    'nb_col_out': nb_col_out,
    }

    return (df_transformed,monitoring_dic)

def transform_data_f5_2(df,column):

    return df

def load_table(df, table_name, engine,schema):

    return df
