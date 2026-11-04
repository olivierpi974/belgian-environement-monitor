import pandas as pd
import re
import unicodedata

def normalize_text(value):
    # Minuscules, suppression des accents, alphanumérique uniquement, espaces normalisés
    if pd.isna(value):
        return None
    value = str(value).strip().lower()
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or None