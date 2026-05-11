import pandas as pd
import os
from utils.text import normalize_text



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

def transform_data_f5_2(df,col, col_filter, col_combustible, index, col_pivot, value_pivot,normalize_col):
    #filtering by combustible
    
    df=df[col].copy()
    mask=df[col_filter].isin(col_combustible)
    df_transformed=df[mask]

    #pivoting
    df_transformed=df_transformed.pivot_table(index=index, columns=col_pivot,values=value_pivot)
    df_transformed=df_transformed.reset_index()
    df_transformed.rename(str.lower,axis='columns',inplace=True)
   
    df_transformed[normalize_col]=df_transformed[normalize_col].map(normalize_text)
    

    #modification of col_combustible to transform  unit in combustible columns
    col_combustible=[combustible.lower() for combustible in col_combustible]
    # TJ → GWh (facteur IPCC : 1 TJ = 0.2778 GWh)
    df_transformed[col_combustible] = df_transformed[col_combustible] * 0.2778
    
    nb_null_in=df.isnull().sum().sum()
    nb_null_out=df_transformed.isnull().sum().sum()
    nb_rows_out=len(df_transformed)
    
    nb_col_out=len(df_transformed.columns)

    monitoring_dic={
    'table_name': 'silver_f5_2',
    'nb_rows_out':nb_rows_out,
    'nb_null_in': nb_null_in,
    'nb_null_out': nb_null_out,
    'nb_col_out': nb_col_out,
    }
    return (df_transformed, monitoring_dic)

def transform_f6(df,f6_col_to_keep,col_to_normalize,col_fill_na):
    
    df_transformed=df[f6_col_to_keep].copy()
    df_transformed=df_transformed.drop_duplicates()
    df_transformed=df_transformed.rename(str.lower,axis='columns')
    df_transformed[col_to_normalize]= df_transformed[col_to_normalize].map(normalize_text)
    df_transformed=df_transformed.fillna({col_fill_na:'unknown'})
    
    nb_null_in=df.isnull().sum().sum()
    nb_null_out=df_transformed.isnull().sum().sum()
    nb_rows_out=len(df_transformed)
    
    nb_col_out=len(df_transformed.columns)
    
    monitoring_dic={
    'table_name': 'silver_f6_1',
    'nb_rows_out':nb_rows_out,
    'nb_null_in': nb_null_in,
    'nb_null_out': nb_null_out,
    'nb_col_out': nb_col_out,
    }
    return (df_transformed,monitoring_dic)




