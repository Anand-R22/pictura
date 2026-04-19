import pandas as pd
import os

RAW = "data/TMDB_movie_dataset_v11.csv"
OUT = "data/movies_clean.csv"

print("Reading dataset...")
df = pd.read_csv(RAW, low_memory=False, encoding="utf-8", encoding_errors="replace")
print(f"Loaded {len(df):,} rows")

# Rename id to movieId
df = df.rename(columns={"id": "movieId"})

# Keep only useful columns
cols = ["movieId", "title", "release_date", "genres", "vote_average",
        "vote_count", "popularity", "overview", "poster_path", "status", "adult"]
df = df[[c for c in cols if c in df.columns]].copy()

# Convert numeric columns
df["movieId"]      = pd.to_numeric(df["movieId"],      errors="coerce")
df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0)
df["vote_count"]   = pd.to_numeric(df["vote_count"],   errors="coerce").fillna(0)
df["popularity"]   = pd.to_numeric(df["popularity"],   errors="coerce").fillna(0)

# Drop rows with no movieId or title
df = df.dropna(subset=["movieId", "title"])
df["movieId"] = df["movieId"].astype(int)
df = df[df["movieId"] > 0]

# Keep only released movies with enough votes
if "status" in df.columns:
    df = df[df["status"] == "Released"]
if "adult" in df.columns:
    df = df[df["adult"].astype(str).str.lower() != "true"]
df = df[df["vote_count"] >= 20]
df = df[df["vote_average"] > 0]

# Fix genres: "Action, Comedy" -> "Action|Comedy"
def fix_genres(g):
    if pd.isna(g) or not str(g).strip():
        return "(no genres listed)"
    parts = [x.strip() for x in str(g).split(",") if x.strip()]
    return "|".join(parts) if parts else "(no genres listed)"

df["genres"] = df["genres"].apply(fix_genres)

# Fix poster_path: ensure leading slash
def fix_poster(p):
    if pd.isna(p) or not str(p).strip():
        return ""
    p = str(p).strip()
    return p if p.startswith("/") else "/" + p

df["poster_path"] = df["poster_path"].apply(fix_poster)

# Add year to title
def fmt_title(row):
    title = str(row["title"]).strip()
    date  = str(row.get("release_date", ""))
    year  = date[:4] if date and len(date) >= 4 and date[:4].isdigit() else ""
    if year and f"({year})" not in title:
        return f"{title} ({year})"
    return title

df["title"]    = df.apply(fmt_title, axis=1)
df["overview"] = df["overview"].fillna("")
df             = df.drop_duplicates(subset="movieId")

# Save final columns only
final = df[["movieId", "title", "genres", "vote_average", "popularity",
            "overview", "poster_path"]].reset_index(drop=True)

os.makedirs("data", exist_ok=True)
final.to_csv(OUT, index=False, encoding="utf-8")

print(f"\nDone! Saved {len(final):,} movies to {OUT}")
print(f"\nSample:")
print(final[["title", "genres", "vote_average"]].head(5).to_string())

# Quick search test
print("\nSearch test - batman:")
mask = final["title"].str.lower().str.contains("batman", na=False, regex=False)
print(final[mask][["title", "vote_average"]].head(5).to_string())
