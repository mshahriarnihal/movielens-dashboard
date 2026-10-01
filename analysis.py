"""Small, explicit aggregations used by the MovieLens dashboard."""
from pathlib import Path
import pandas as pd


DATA_PATH = Path(__file__).parent / "data" / "movie_ratings.csv"


def load_data(path=DATA_PATH):
    data = pd.read_csv(path)
    data = data.rename(columns={"movieId": "movie_id", "userId": "user_id"})
    required = {"movie_id", "title", "rating", "year", "genres"}
    if missing := required - set(data.columns):
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    data["rating"] = pd.to_numeric(data["rating"], errors="raise")
    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    if data["movie_id"].isna().any() or not data["rating"].between(1, 5).all():
        raise ValueError("Every row must have a movie ID and a rating from 1 to 5.")
    data["genres"] = data["genres"].fillna("unknown")
    return data


def split_genres(data):
    result = data.assign(genre=data["genres"].str.split("|")).explode("genre")
    result["genre"] = result["genre"].str.strip().replace({"": "unknown"})
    return result


def filter_years(data, years, include_unknown):
    keep = data["year"].between(*years)
    if include_unknown:
        keep |= data["year"].isna()
    return data.loc[keep].copy()


def genre_counts(data):
    # Count distinct movies, not the number of rating rows.
    movies = data.drop_duplicates("movie_id")
    return (split_genres(movies).groupby("genre")["movie_id"].nunique()
            .rename("movies").reset_index()
            .sort_values(["movies", "genre"], ascending=[False, True]))


def genre_ratings(data):
    # Each rating contributes once to every genre assigned to its movie.
    return (split_genres(data).groupby("genre").agg(
        mean_rating=("rating", "mean"), ratings=("rating", "size"),
        movies=("movie_id", "nunique")).reset_index()
        .sort_values(["mean_rating", "genre"], ascending=[False, True]))


def yearly_ratings(data):
    return (data.dropna(subset=["year"]).groupby("year").agg(
        mean_rating=("rating", "mean"), ratings=("rating", "size"),
        movies=("movie_id", "nunique")).reset_index().sort_values("year"))


def movie_ratings(data):
    return data.groupby("movie_id", as_index=False).agg(
        title=("title", "first"), mean_rating=("rating", "mean"),
        ratings=("rating", "size"))


def top_movies(summary, floor):
    # Inclusive threshold. Stable, stated tie-breakers avoid arbitrary top fives.
    return (summary.loc[summary["ratings"] >= floor]
            .sort_values(["mean_rating", "ratings", "title", "movie_id"],
                         ascending=[False, False, True, True]).head(5).copy())
