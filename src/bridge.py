from utils.text import normalize_text



def build_lcp_representative(df_5,cols):
    
    tmp=df_5.copy()
    tmp["name_norm"]=tmp[cols["name"]].map(normalize_text)
    tmp["city_norm"]=tmp[cols["city"]].map(normalize_text)

    rep= (
        tmp.groupby(cols["id"])
        .agg(
            country=(cols["country"],"first"),
            installationPartName=(cols["name"],lambda s:s.dropna().iloc[0] if s.dropna().size else None),
            name_norm=("name_norm", lambda s: s.dropna().iloc[0] if s.dropna().size else None),
            City_Of_Facility=(cols["city"], lambda s: s.dropna().mode().iloc[0] if s.dropna().size else None),
            city_norm=("city_norm", lambda s: s.dropna().mode().iloc[0] if s.dropna().size else None),
            Longitude=(cols["longitude"], "median"),
            Latitude=(cols["latitude"], "median"),
            min_reportingYear=(cols["year"], "min"),
            max_reportingYear=(cols["year"], "max"),
        )
        .reset_index()
        )
    
    return rep

def build_installation_representative(df_6,cols):
    tmp=df_6.copy()
    tmp["name_norm"]=tmp[cols["name"]].map(normalize_text)
    tmp["city_norm"]=tmp[cols["city"]].map(normalize_text)
    rep=(
        tmp.groupby(cols["id"])
                .agg(
                    country=(cols["country"], "first"),
                    parent_facilityInspireId=(cols["parent_id"], lambda s: s.dropna().iloc[0] if s.dropna().size else None),
                    installationName=(cols["name"], lambda s: s.dropna().iloc[0] if s.dropna().size else None),
                    name_norm=("name_norm", lambda s: s.dropna().iloc[0] if s.dropna().size else None),
                    City_of_Facility=(cols["city"], lambda s: s.dropna().mode().iloc[0] if s.dropna().size else None),
                    city_norm=("city_norm", lambda s: s.dropna().mode().iloc[0] if s.dropna().size else None),
                    Longitude=(cols["longitude"], "median"),
                    Latitude=(cols["latitude"], "median"),
                    min_reportingYear=(cols["year"], "min"),
                    max_reportingYear=(cols["year"], "max"),
                )
                .reset_index()
    )
    return rep