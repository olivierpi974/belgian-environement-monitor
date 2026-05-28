
import pandas as pd

#column to pass in the fucntions
dim_pollutant_col=['pollutant']
dim_sector_col= ['eprtr_sectorcode', 'eprtr_sectorname']
dim_site_col= ['facilityinspireid',	'facilityname',	'city'	,'longitude',	'latitude']
fact_emission_col=['reportingyear', 'eprtr_sectorcode', 'fk_site_id','fk_pollutant_id',
       'emitted_pollutant_kg']

def dim_date():
    """this function returns a dataframe containing the dates
     between 2007 to 2024  """
    df=pd.DataFrame({'year':range(2007,2025)})
    
    df['decade']=(df['year']//10)*10
   
    return df


def dim_pollutant(df):
    """this function returns a dataframe containing
    the list of pollutants on e-prtr database
    df: should be the dataframe coming from the silver layer
    col_pollutant: columns containg the data to use to create the dimension table
    returns: df"""
    
    df=df[dim_pollutant_col].drop_duplicates().reset_index(drop=True)
    df['pollutant_id']=df.index +1
    
    return df
 
def dim_sector(df):
    
    df= df[dim_sector_col]
    df=df.drop_duplicates()
    df=df.reset_index(drop=True)
    
    return df

def dim_site(df):
    df=df[dim_site_col].copy()
    df['site_id']=df.index + 1

    return df

def fact_emission_air(df):
    
    df.rename(columns={'reportingyear':'year'},inplace=True)
        
    df['emitted_pollutant_kg']=df['emitted_pollutant_kg']//1000
    df.rename(columns={'emitted_pollutant_kg':'emitted_pollutant_tons'}, inplace=True)
            
    return df 
