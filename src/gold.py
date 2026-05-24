
import pandas as pd
def dim_date():
    """this function retunrs a dataframe containing the dates
     between 2007 to 2024  """
    df=pd.DataFrame({'year':range(2016,2025)})
    df['decade']=(df['year']//10)*10
   
    return df


def dim_pollutant(df,col_pollutant):
    """this function returns a dataframe containing
    the list of pollutants on e-prtr database
    df: should be the dataframe coming from the silver layer
    col_pollutant: columns containg the data to use to create the dimension table
    returns: df_dim"""
    df_dim=df[[col_pollutant]].drop_duplicates().reset_index(drop=True)
    df_dim.index +1
    
    return df_dim
