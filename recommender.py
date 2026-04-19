import pandas as pd
import numpy as np

DATA_FILE = "data/movies_clean.csv"
_cache = None


def load_data():
    global _cache
    if _cache is not None:
        return _cache
    print("Loading movies...")
    df = pd.read_csv(DATA_FILE, low_memory=False,
                     encoding="utf-8", encoding_errors="replace")
    df["movieId"]      = pd.to_numeric(df["movieId"],      errors="coerce").fillna(0).astype(int)
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0)
    df["popularity"]   = pd.to_numeric(df["popularity"],   errors="coerce").fillna(0)
    df["overview"]     = df["overview"].fillna("")
    df["poster_path"]  = df["poster_path"].fillna("")
    df["genres"]       = df["genres"].fillna("(no genres listed)")
    # Bayesian score: balances quality vs popularity
    C = df["vote_average"].mean()
    m = 100
    df["_score"] = (df["popularity"] / (df["popularity"] + m)) * df["vote_average"] + \
                   (m / (df["popularity"] + m)) * C
    _cache = df
    print(f"Loaded {len(df):,} movies.")
    return df


def search_movies(query, movies, limit=8):
    q = query.strip().lower()
    mask = movies["title"].str.lower().str.contains(q, na=False, regex=False)
    hits = movies[mask].copy()
    if hits.empty:
        return hits
    hits["_exact"] = hits["title"].str.lower().str.startswith(q).astype(int)
    return hits.sort_values(["_exact", "_score"], ascending=[False, False]).head(limit)


def get_recommendations(movie_id, movies, n=12):
    row = movies[movies["movieId"] == int(movie_id)]
    if row.empty:
        return pd.DataFrame()
    target_genres = set(str(row.iloc[0]["genres"]).split("|"))
    pattern = "|".join(target_genres)
    mask = (movies["movieId"] != int(movie_id)) & \
           movies["genres"].str.contains(pattern, case=False, na=False, regex=True)
    cands = movies[mask].copy()
    if cands.empty:
        return pd.DataFrame()
    cands["_overlap"] = cands["genres"].apply(
        lambda g: len(target_genres & set(str(g).split("|")))
    )
    cands["_final"] = cands["_score"] + cands["_overlap"] * 0.1
    top = cands.sort_values("_final", ascending=False).head(n)
    return top[["movieId", "title", "genres", "poster_path", "vote_average"]].reset_index(drop=True)
