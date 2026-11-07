from utils.text import normalize_text
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
from rapidfuzz.fuzz import token_set_ratio
import time
from datetime import datetime

def prepare_balltree(df_points):
    """Index spatial haversine sur (Latitude, Longitude) converties en radians"""
    coords = np.deg2rad(df_points[["Latitude", "Longitude"]].to_numpy())
    return BallTree(coords, metric="haversine")

def candidate_from_lcp_id(lcp_id):
    """ Heuristique : LCPInspireId se terminant par .PART → remplace par .INSTALLATION """
    if pd.isna(lcp_id):
        return None
    s = str(lcp_id)
    if s.endswith(".PART"):
        return s[:-5] + ".INSTALLATION"
    return None


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


def compute_bridge_candidate(lcp_rep, inst_rep, top_k=5, max_distance_km=3.0):
    inst_all = inst_rep.copy().reset_index(drop=True)
    tree_all = prepare_balltree(inst_all)
    
    results = []
    
    for _, row in lcp_rep.iterrows():
        # Filtrage city_norm : candidats de la même ville → sinon tout le pays
        city_candidates = (
            inst_all[inst_all["city_norm"] == row["city_norm"]].reset_index(drop=True)
            if row["city_norm"] else pd.DataFrame()
        )

        if len(city_candidates) > 0:
            search_df = city_candidates
            search_tree = prepare_balltree(search_df)
            same_city_search_used = True
        else:
            search_df = inst_all
            search_tree = tree_all
            same_city_search_used = False

        k = min(top_k, len(search_df))
        distances, indices = search_tree.query(
            np.deg2rad([[row["Latitude"], row["Longitude"]]]),
            k=k
        )

        for rank, (dist_rad, idx) in enumerate(zip(distances[0], indices[0]), start=1):
            cand = search_df.iloc[int(idx)]
            distance_km = float(dist_rad * 6371.0088)

            name_similarity = float(
                token_set_ratio(str(row["name_norm"] or ""), str(cand["name_norm"] or ""))
            )
            same_city_flag = bool(row["city_norm"] and row["city_norm"] == cand["city_norm"])
            id_guess_match = bool(candidate_from_lcp_id(row["LCPInspireId"]) == cand["InstallationInspireId"])

            distance_score = max(0.0, 100.0 * (1 - min(distance_km, max_distance_km) / max_distance_km))
            city_score = 100.0 if same_city_flag else 0.0
            id_score = 100.0 if id_guess_match else 0.0

            match_score = (
                0.55 * distance_score +
                0.30 * name_similarity +
                0.10 * city_score +
                0.05 * id_score
            )

            results.append({
                "LCPInspireId": row["LCPInspireId"],
                "InstallationInspireId": cand["InstallationInspireId"],
                "parent_facilityInspireId": cand["parent_facilityInspireId"],
                "lcp_name": row["installationPartName"],
                "installation_name": cand["installationName"],
                "lcp_city": row["City_Of_Facility"],
                "installation_city": cand["City_of_Facility"],
                "lcp_longitude": row["Longitude"],
                "lcp_latitude": row["Latitude"],
                "installation_longitude": cand["Longitude"],
                "installation_latitude": cand["Latitude"],
                "distance_km": distance_km,
                "name_similarity": name_similarity,
                "same_city_flag": same_city_flag,
                "id_guess_match": id_guess_match,
                "same_city_search_used": same_city_search_used,
                "candidate_rank": rank,
                "match_score": round(match_score, 2),
            })

    return pd.DataFrame(results).sort_values(
        ["LCPInspireId", "match_score"], ascending=[True, False]
    )

def select_best_match(candidate,confidence_bins,min_score_gap):
    """keep the best candidate by lcp 
    then compute the gap beteween the first and second among best canditate for 1 LCP,
    classify the confidence and decide manual reviews to apply"
    """
    bridge_best=candidate.groupby("LCPInspireId", as_index=False).first()
    
    score_gap=(
        candidate.groupby("LCPInspireId")["match_score"]
        .agg(lambda s: s.iloc[0] - s.iloc[1] if len(s) > 1 else np.nan)
        .rename('top1_minus_top2')
        .reset_index()
    )
    bridge_best=bridge_best.merge(score_gap, on="LCPInspireId",how='left')
    bridge_best['confidence_level']=pd.cut(
        bridge_best['match_score'],
        bins=confidence_bins,
        labels=['faible','moyenne','forte']
        )
    bridge_best['manual_review_required']=(
        (bridge_best['confidence_level'] !="forte")
        | (bridge_best['top1_minus_top2'].fillna(999)< min_score_gap)
    )

   
    

    return  (bridge_best
        .sort_values('match_score',ascending=False)
        .reset_index(drop=True))

def build_bridge_lcp_installation(df_5,df_6,bridge_config):
    start=time.perf_counter()
    lcp_rep=(
        build_lcp_representative(df_5,bridge_config["lcp_columns"])
        .dropna(subset=["Latitude", "Longitude"])
        .reset_index(drop=True)
        )
    inst_rep = (build_installation_representative(df_6,bridge_config["installation_columns"])
    .dropna(subset=["Latitude", "Longitude"])
    .reset_index(drop=True)
    )

    bridge_candidate=compute_bridge_candidate(
        lcp_rep=lcp_rep, 
        inst_rep=inst_rep,
        top_k=bridge_config['top_k'],
        max_distance_km=bridge_config["max_distance_km"]
        )

    best_bridge= select_best_match(
        candidate=bridge_candidate,
        confidence_bins=bridge_config['confidence_bins'],
        min_score_gap=bridge_config['min_score_gap'])
    
    best_bridge=best_bridge.rename(str.lower,axis="columns")

    monitoring_dic={
        'table_name':'silver_bridge_lcp_installation',
        'nb_rows_out':len(best_bridge),
        'nb_null_in':df_5.isnull().sum().sum() +df_6.isnull().sum().sum(),
        'nb_null_out':best_bridge.isnull().sum().sum(),
        'nb_col_out':len(best_bridge.columns),
        'bridge_manual_verification':int(best_bridge['manual_review_required'].sum()),
        'duration_sec':round(time.perf_counter()-start,2),
        'date_transform':datetime.now()
    }
    
    return best_bridge,monitoring_dic

