# MovieLens · The Audience Cut

A Streamlit dashboard for CUNY Tech Prep's Week 4 assignment. Built with AI assistance and the course-provided MovieLens data.

The dashboard answers four questions:

1. Which genres appear most often among rated movies?
2. Which genres have the highest and lowest average ratings?
3. How does average rating vary by movie release year?
4. Which five movies rank highest with at least 50 ratings, and what changes at 150?

## Run locally

Use Python 3.14 (the version tested locally), or a compatible Python supported by the dependencies.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Choices behind the charts

- Genre counts use unique movie IDs. A movie counts once in each of its genres, so the bars overlap and are not parts of a single whole.
- Genre and release-year averages give each rating equal weight. These are not averages of movie-level averages.
- The year chart uses `year`, the movie's release year, not `rating_year` or `timestamp`. The 30 rows with missing release years remain available to the other charts through an explicit checkbox.
- `unknown` remains visible as an uncategorized label. The highest/lowest named-genre summary excludes it.
- Movie rankings use mean rating and an inclusive floor: at least 50 or at least 150. Ties use more ratings, then title, then movie ID.
- All charts follow the release-year filter. The rating floor only affects the top-five chart; both threshold lists remain visible for comparison.
- Hover over rating charts to inspect sample sizes. Older years and smaller genres can have little evidence; the charts describe this dataset rather than all audiences.

## Data

Source: [CUNY Tech Prep course CSV](https://github.com/CUNYTechPrep/ds-dev-fall-2026/blob/main/Week-04-Vibe-Coding-101/data/movie_ratings.csv), based on GroupLens MovieLens. The original course CSV is included without changes.

This file has 100,000 ratings, 1,682 rated movies, and known release years from 1922 to 1998. Its actual column names include `movie_id` and `user_id`; the loader also accepts the camelCase spellings shown in the assignment.

SHA-256: `a94b2f45766f49911985efdc5eb2e5c266be5bf4c0dac7872c2cc7ed6f29358d`.

## Deployment

Push this project to a public GitHub repository. In Streamlit Community Cloud, choose that repository, branch `main`, and main file `app.py`. Use Python 3.14 in Advanced settings to match the tested environment. Test the deployed URL in a private browser window before submitting it.

The build log is kept locally in `BUILD_LOG.md` and is excluded from Git. Keep it for the next assignment.
