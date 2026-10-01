from html import escape

import altair as alt
import streamlit as st

from analysis import (filter_years, genre_counts, genre_ratings, load_data,
                      movie_ratings, top_movies, yearly_ratings)

st.set_page_config(page_title="MovieLens · The Audience Cut", page_icon="🎬", layout="wide")
INK = "#29263D"
CORAL = "#BE5036"
BLUE = "#5265AB"
GOLD = "#A36B20"

st.html("""
<style>
.stApp { background: #FAF8F3; }
.block-container { max-width: 1320px; padding-top: 4.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #EFECE4; border-right: 1px solid #DED8CA; }
h1, h2, h3 { letter-spacing: -.025em; }
h3 { font-family: Georgia, serif !important; font-size: 1.55rem !important; }
[data-testid="stMetric"] { background: #FFFDF8; border: 1px solid #E5DED0;
  border-top: 3px solid #BE5036; border-radius: 4px; padding: 18px 22px; }
[data-testid="stMetricValue"] { font-family: Georgia, serif; }
[data-testid="stCaptionContainer"] { color: #656171; }
[data-testid="stVegaLiteChart"] { background: #FFFDF8; border-radius: 5px; padding: 8px; }
.hero { border-top: 5px solid #29263D; border-bottom: 1px solid #CDC4B5;
  padding: 24px 0 25px; margin-bottom: 24px; }
.eyebrow { font-size: 11px; font-weight: 700; letter-spacing: .2em; color: #A44730; }
.hero h1 { font-family: Georgia, serif !important; font-size: clamp(44px, 6vw, 76px);
  font-weight: 500; line-height: 1.05; margin: 12px 0 16px; padding: 0; color: #29263D; }
.hero h1 em { color: #BE5036; font-weight: 400; }
.hero p { max-width: 680px; font-size: 16px; line-height: 1.6; margin-bottom: 18px; }
.credit { font-size: 11px; line-height: 1.7; color: #686172; letter-spacing: .025em; }
.rank-list { border-top: 2px solid #29263D; margin: 5px 0 18px; }
.rank-row { display: grid; grid-template-columns: 25px 1fr 68px; gap: 12px;
  align-items: center; padding: 15px 0; border-bottom: 1px solid #E2DCCF; }
.rank-number { font-family: Georgia, serif; font-size: 22px; color: #A36B20; }
.rank-title { font-size: 14px; line-height: 1.45; color: #29263D; }
.rank-score { text-align: right; font-size: 18px; font-weight: 700; color: #29263D; }
.rank-score small { display: block; font-size: 10px; font-weight: 400; color: #686172; }
@media (max-width: 640px) {
 .block-container { padding-top: 4rem; }
 .hero h1 { font-size: 46px; }
 .rank-row { gap: 7px; }
}
</style>
""")


@st.cache_data
def get_data():
    return load_data()


def bar_chart(frame, value, label, axis_title, rating=False, tooltips=None, color=CORAL):
    base = alt.Chart(frame).encode(
        x=alt.X(f"{value}:Q", title=axis_title,
                scale=alt.Scale(domain=[0, 5]) if rating else alt.Scale(zero=True)),
        y=alt.Y(f"{label}:N", title=None, sort=frame[label].tolist(),
                axis=alt.Axis(labelLimit=300, labelFontSize=11)),
        tooltip=tooltips or [alt.Tooltip(f"{label}:N"), alt.Tooltip(f"{value}:Q")]
    )
    bars = base.mark_bar(cornerRadiusEnd=3, size=14).encode(
        color=alt.condition(alt.datum[label] == "unknown", alt.value("#ABA49A"), alt.value(color)))
    labels = base.mark_text(align="left", dx=5, color=INK, fontSize=10).encode(
        text=alt.Text(f"{value}:Q", format=".2f" if rating else ",.0f"))
    return (bars + labels).properties(height=max(220, len(frame) * 25)).configure_view(
        strokeWidth=0).configure_axis(domain=False, tickSize=0, labelColor="#656171",
                                     titleColor="#656171", gridColor="#E9E3D8", titlePadding=15)


st.html("""
<div class="hero">
  <div class="eyebrow">MOVIELENS / THE AUDIENCE CUT</div>
  <h1>Good movies.<br><em>Better questions.</em></h1>
  <p>What gets watched? What gets loved? And does a top rating still hold up
  when more people have a say? Four questions, straight from the data.</p>
  <div class="credit">Developed By The Supervision of Mubasshir Al Shahriar, Powered By: Codex</div>
</div>
""")

try:
    data = get_data()
except (OSError, ValueError) as error:
    st.error(f"Could not load the course dataset: {error}")
    st.stop()

with st.sidebar:
    st.caption("THE CONTROL ROOM")
    st.header("Make your cut")
    years = st.slider("Movie release years", int(data.year.min()), int(data.year.max()),
                      (int(data.year.min()), int(data.year.max())))
    include_unknown = st.checkbox("Include movies with an unknown release year", value=True)
    floor = st.select_slider("Minimum ratings for the top five", options=[50, 150], value=50)
    st.caption("Release years filter all four sections. The minimum-ratings control only affects the top-five chart.")
    st.caption("Start with the full year range to answer the assignment using the whole dataset.")

filtered = filter_years(data, years, include_unknown)
if filtered.empty:
    st.info("No ratings match these filters. Widen the release-year range.")
    st.stop()

metrics = st.columns(3)
metrics[0].metric("Rated movies", f"{filtered.movie_id.nunique():,}")
metrics[1].metric("Ratings", f"{len(filtered):,}")
metrics[2].metric("Average rating / 5", f"{filtered.rating.mean():.2f}")
st.divider()

left, right = st.columns(2, gap="large")
with left:
    st.caption("01 / THE MIX")
    st.subheader("Which genres show up most?")
    st.caption("Each movie counts once in each of its genres. A movie with three genres appears in three bars, so the counts overlap.")
    counts = genre_counts(filtered)
    st.altair_chart(bar_chart(counts, "movies", "genre", "Distinct rated movies"), width="stretch", theme=None)
    leader = counts.iloc[0]
    st.write(f"**{leader.genre}** has the most rated movies in this selection: **{int(leader.movies):,}**.")

with right:
    st.caption("02 / THE VERDICT")
    st.subheader("Which genres get higher ratings?")
    st.caption("Average of individual ratings, with each rating included in every genre attached to its movie. Hover to check sample sizes.")
    satisfaction = genre_ratings(filtered)
    st.altair_chart(bar_chart(satisfaction, "mean_rating", "genre", "Mean rating (1–5)", True,
        [alt.Tooltip("genre:N", title="Genre"), alt.Tooltip("mean_rating:Q", format=".3f", title="Mean rating"),
         alt.Tooltip("ratings:Q", title="Ratings"), alt.Tooltip("movies:Q", title="Movies")], color=BLUE), width="stretch", theme=None)
    named = satisfaction.loc[~satisfaction.genre.str.lower().isin(["unknown", "(no genres listed)"])]
    if not named.empty:
        highest, lowest = named.iloc[0], named.iloc[-1]
        st.write(f"Among named genres, highest mean: **{highest.genre} ({highest.mean_rating:.2f})**. "
                 f"Lowest mean: **{lowest.genre} ({lowest.mean_rating:.2f})**.")
    st.caption("Genres share some of the same movies. Small samples can produce unstable averages; “unknown” is an uncategorized label.")

st.divider()
st.caption("03 / THROUGH THE YEARS")
st.subheader("Does the release year tell a story?")
st.caption("The x-axis is the year the movie came out. Each individual rating has equal weight, so frequently rated movies contribute more to the year's average.")
yearly = yearly_ratings(filtered)
if yearly.empty:
    st.info("The selected movies have no known release years.")
else:
    line = alt.Chart(yearly).mark_line(point=alt.OverlayMarkDef(size=35, filled=True), color=BLUE, strokeWidth=2.5).encode(
        x=alt.X("year:Q", title="Movie release year", axis=alt.Axis(format="d"), scale=alt.Scale(zero=False)),
        y=alt.Y("mean_rating:Q", title="Mean rating (1–5)", scale=alt.Scale(domain=[0, 5])),
        tooltip=[alt.Tooltip("year:Q", format="d", title="Release year"),
                 alt.Tooltip("mean_rating:Q", format=".3f", title="Mean rating"),
                 alt.Tooltip("ratings:Q", title="Ratings"), alt.Tooltip("movies:Q", title="Movies")]
    ).properties(height=310).configure_view(strokeWidth=0).configure_axis(
        domain=False, tickSize=0, gridColor="#E9E3D8", labelColor="#656171", titleColor="#656171")
    st.altair_chart(line, width="stretch", theme=None)
unknown_count = int(filtered.year.isna().sum())
st.caption(f"{unknown_count:,} selected ratings have no release year and are excluded from this chart. Hover to inspect sample sizes; no smoothing or minimum yearly sample size is applied.")

st.divider()
st.caption("04 / THE SHORTLIST")
st.subheader("Great ratings. Enough votes?")
st.caption(f"Top five movies with at least {floor} ratings. Ranked by mean rating; ties use rating count, then title and movie ID.")
summary = movie_ratings(filtered)
top = top_movies(summary, floor)
if top.empty:
    st.info(f"No movies have at least {floor} ratings in this selection. Widen the year range or lower the floor.")
else:
    top["movie_label"] = top["title"] + " · #" + top["movie_id"].astype(str)
    st.altair_chart(bar_chart(top, "mean_rating", "movie_label", "Mean rating (1–5)", True,
        [alt.Tooltip("title:N", title="Movie"), alt.Tooltip("mean_rating:Q", format=".3f", title="Mean rating"),
         alt.Tooltip("ratings:Q", title="Ratings")], color=GOLD), width="stretch", theme=None)

st.markdown("**What changes from 50 to 150 ratings?**")
top50, top150 = top_movies(summary, 50), top_movies(summary, 150)
for column, threshold, ranking in zip(st.columns(2), (50, 150), (top50, top150)):
    with column:
        st.markdown(f"**At least {threshold} ratings**")
        if ranking.empty:
            st.caption("No qualifying movies in this selection.")
        else:
            rows = []
            for rank, item in enumerate(ranking.itertuples(), 1):
                rows.append(f'<div class="rank-row"><div class="rank-number">{rank:02}</div>'
                            f'<div class="rank-title">{escape(item.title)}</div>'
                            f'<div class="rank-score">{item.mean_rating:.3f}'
                            f'<small>{item.ratings:,} ratings</small></div></div>')
            st.html('<div class="rank-list">' + ''.join(rows) + '</div>')

if not top50.empty:
    retained = len(set(top50.movie_id) & set(top150.movie_id))
    st.write(f"**{retained} of the {len(top50)} movies** from the 50-rating list stay in the 150-rating list.")
    departures = top50.loc[~top50.movie_id.isin(top150.movie_id), "title"].tolist()
    arrivals = top150.loc[~top150.movie_id.isin(top50.movie_id), "title"].tolist()
    if departures:
        st.write("Leave the top five: " + "; ".join(departures) + ".")
    if arrivals:
        st.write("Enter the top five: " + "; ".join(arrivals) + ".")
st.caption("A higher floor requires more rating evidence. It does not prove that a movie is better or remove selection bias.")
st.divider()
st.caption("Source: GroupLens MovieLens, using the CSV supplied by CUNY Tech Prep · Ratings are on a 1–5 scale.")
st.markdown("[Course dataset](https://github.com/CUNYTechPrep/ds-dev-fall-2026/blob/main/Week-04-Vibe-Coding-101/data/movie_ratings.csv)")
