
import pandas as pd

#column to pass in the fucntions
dim_pollutant_col=['pollutant']
dim_sector_col= ['eprtr_sectorcode', 'eprtr_sectorname']
dim_site_col= ['facilityinspireid',	'facilityname',	'city'	,'longitude',	'latitude']
fact_emission_col=['reportingyear', 'eprtr_sectorcode', 'fk_site_id','fk_pollutant_id',
       'emitted_pollutant_tons']

def create_dim_date():
    """this function returns a dataframe containing the dates
     between 2007 to 2024  """
    df=pd.DataFrame({'year':range(2007,2025)})
    
    df['decade']=(df['year']//10)*10

    nb_rows_out=len(df)


    monitoring_dict={'table_name': 'dim_date',
    'nb_rows_out':nb_rows_out,
    }
    return df,monitoring_dict


def create_dim_pollutant(df):
    """this function returns a dataframe containing
    the list of pollutants on e-prtr database
    df: should be the dataframe coming from the silver layer
    col_pollutant: columns containg the data to use to create the dimension table
    returns: df"""
    
    df=df[dim_pollutant_col].drop_duplicates().reset_index(drop=True)
    df['pollutant_id']=df.index +1
    mapping_id= df.set_index('pollutant')['pollutant_id'].to_dict()
    
    nb_rows_out=len(df)
    nb_duplicates=df.duplicated(subset=['pollutant']).sum()
    nb_null= df['pollutant'].isnull().sum()
    
    monitoring_dict={'table_name': 'dim_pollutant',
    'nb_rows_out':nb_rows_out,
    'nb_duplicates':nb_duplicates,
    'nb_null':nb_null}
    return df,mapping_id, monitoring_dict
 
def create_dim_sector(df):
    
    df= df[dim_sector_col]
    df=df.drop_duplicates()
    df=df.reset_index(drop=True)
    
    nb_rows_out=len(df)
    nb_duplicates=df.duplicated(subset=['eprtr_sectorcode']).sum()
    nb_null=df['eprtr_sectorcode'].isnull().sum()

    monitoring_dict={'table_name': 'dim_sector',
    'nb_rows_out':nb_rows_out,
    'nb_duplicates':nb_duplicates,
    'nb_null':nb_null}
    
    return df,monitoring_dict

def create_dim_site(df):
    df=df[dim_site_col].copy()
    df['site_id']=df.index + 1
    mapping_key=df.set_index('facilityinspireid')['site_id'].to_dict()
    
    nb_rows_out=len(df)
    nb_null= df['facilityinspireid'].isnull().sum()
    nb_duplicates=df.duplicated(subset=['facilityinspireid']).sum()
    
    monitoring_dict={'table_name': 'dim_site',
    'nb_duplicates':nb_duplicates,
    'nb_rows_out':nb_rows_out,
    'nb_null':nb_null
        }
    
    return df,mapping_key,monitoring_dict

def create_fact_emission_air(df,mapping_site_id, mapping_pollutant_id):
    
    df.rename(columns={'reportingyear':'year'},inplace=True)
        
    df['emitted_pollutant_kg']=df['emitted_pollutant_kg']/1000
    df.rename(columns={'emitted_pollutant_kg':'emitted_pollutant_tons'}, inplace=True)
    df['fk_site_id']= df['facilityInspireid'].map(mapping_site_id)
    df['fk_pollutant_id']=df['pollutant'].map(mapping_pollutant_id)     
    df=df[fact_emission_col]

    nb_rows_out=len(df)
    nb_duplicates=df.duplicated(subset=['year', 'fk_site_id','fk_pollutant_id']).sum()
    year_null=df['year'].isnull().sum()
    sector_null=df['eprtr_sectorcode'].isnull().sum()
    site_null=df['fk_site_id'].isnull().sum()
    pollutant_null=df['fk_pollutant_id'].isnull().sum()
    
    monitoring_dict={'table_name': 'fact_emission_air',
    'nb_rows_out':nb_rows_out,
    'nb_duplicates':nb_duplicates,
    'nb_year_null':year_null,
    'nb_sector_null':sector_null,
    'nb_site_null':site_null,
    'nb_pollutant_null':pollutant_null,
    } 
    return df, monitoring_dict
