import pandas as pd

def normalize_text(x):
    if pd.isna(x):
        return None
    x = str(x).lower().strip()
    for ch in ["-", "/", "(", ")", ",", ".", ";", ":", "'"]:
        x = x.replace(ch, " ")
    x = " ".join(x.split())
    return x