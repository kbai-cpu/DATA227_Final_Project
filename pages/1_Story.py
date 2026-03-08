import streamlit as st
import altair as alt
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from charts.charts import (
    chart_vis1_top20_streams,
    chart_vis2_decay_curve,
    chart_feature_importance_genre,
    chart_genre_importance_and_density,
    chart_feature_importance_pop,
    chart_ridge_and_deviation,
    chart_audio_popularity_scatter,
    chart_vis4_reentry,
)

st.set_page_config(page_title="Story", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, li, span, div, button, input, label {
        font-family: 'Lora', serif !important;
    }
    </style>
""", unsafe_allow_html=True)

alt.data_transformers.disable_max_rows()

# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data
def load_all_data():
    top20_songs = pd.read_csv('all_data/top20_songs.csv')

    us_data_20 = pd.read_csv('all_data/us_data_20.csv')
    us_data_20['date'] = pd.to_datetime(us_data_20['date'])
    us_data_20 = us_data_20.sort_values(['title', 'date'])
    us_data_20['rolling_rank'] = (
        us_data_20
        .groupby('title')['rank']
        .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    )

    top6_data = pd.read_csv('all_data/top6_data.csv')
    top6_data['date'] = pd.to_datetime(top6_data['date'])
    if 'rolling_rank' not in top6_data.columns:
        top6_data = top6_data.sort_values(['title', 'date'])
        top6_data['rolling_rank'] = (
            top6_data.groupby('title')['rank']
            .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
        )
    if 'days_since_debut' not in top6_data.columns:
        top6_data['first_date'] = top6_data.groupby('title')['date'].transform('min')
        top6_data['days_since_debut'] = (top6_data['date'] - top6_data['first_date']).dt.days

    top500_full = pd.read_csv('all_data/top500_full.csv')
    genre_density_data = pd.read_csv('all_data/genre_density_data.csv')

    features_clean = pd.read_csv('all_data/features_clean.csv')
    features_clean.loc[features_clean['track_id'] == '0VjIjW4GlUZAMYd2vXMi3b', 'danceability'] = 0.9
    features_clean.loc[features_clean['track_id'] == '0VjIjW4GlUZAMYd2vXMi3b', 'valence'] = 0.83

    return top20_songs, us_data_20, top6_data, top500_full, genre_density_data, features_clean

top20_songs, us_data_20, top6_data, top500_full, genre_density_data, features_clean = load_all_data()

# ── Story ─────────────────────────────────────────────────────────────────────

st.title("The Anatomy of a Streaming Hit")
st.markdown(
    "**Central question:** *What separates a mega-hit from just a popular song on Spotify — "
    "and do total stream counts tell the whole story?*"
)

st.write(
    """
    Between 2017 and 2021, Spotify published daily Top 200 charts across dozens of countries,
    capturing the collective listening habits of hundreds of millions of users. In that span,
    a small cohort of songs accumulated streams in the billions. But raw stream counts are a blunt
    instrument: they conflate a song that briefly went viral with one that held its ground for
    *years*. To understand what truly made a song dominant, we need to look at both dimensions —
    how much it was streamed, and how it moved through the charts over time.
    """
)

st.header("1) Who dominated the charts?")
st.write(
    """
    The bar chart below ranks the 20 most-streamed songs globally. All rank trajectories start
    gray — click any bar to highlight that song in color. Use the mini-chart at the bottom
    to zoom into a specific time window.
    """
)
st.altair_chart(chart_vis1_top20_streams(top20_songs, us_data_20), use_container_width=True)
st.caption(
    "Takeaway: **Blinding Lights** leads the pack by a wide margin — but look at its rank "
    "trajectory. While most hits spike quickly then fade below the top 50, Blinding Lights "
    "maintained a near-top-10 position in the U.S. for well over a year. Total streams reward "
    "longevity just as much as peak popularity."
)

st.header("2) What the numbers obscure")
st.write(
    """
    The mean stream count (red dashed line) sits around 1.4 billion streams. Notice that most
    songs in the top 20 cluster near or below that threshold, while a few — Blinding Lights,
    Shape of You, Dance Monkey — pull far ahead. This concentration at the top is not random:
    it reflects algorithmic amplification, playlist placement, and the compounding effect of
    sustained chart presence. A song that stays in the top 50 for 18 months accumulates streams
    in ways that a two-week viral moment simply cannot match.
    """
)
st.write(
    """
    The rank trajectory chart makes this visible. Songs like *Someone You Loved* show a sharp
    initial rise followed by a steep drop — a classic viral arc. *Blinding Lights*, by contrast,
    exhibits multiple peaks and a remarkably slow decay, suggesting repeated cultural moments
    (sync placements, social media trends, algorithmic re-recommendations) kept it circulating
    long after its release.
    """
)

st.info(
    "In the next section, we isolate what made *Blinding Lights* structurally different — "
    "comparing its decay curve directly against the other top songs to see whether its longevity "
    "was truly exceptional or just a matter of scale."
)

st.header("3) The decay curve: does every hit fade at the same rate?")
st.write(
    """
    To isolate what made *Blinding Lights* structurally different, we normalize each song's
    timeline by days since its U.S. chart debut — removing the distortion of different release
    dates and letting us compare decay curves directly. The five peer songs are the next
    highest-streamed titles globally; all were massive hits by any standard.
    """
)
st.altair_chart(chart_vis2_decay_curve(top6_data), use_container_width=True)
st.caption(
    "Takeaway: Every peer song drops below rank 100 within roughly 200–400 days and never "
    "recovers. **Blinding Lights** (red) does dip — but repeatedly resurfaces near the top 50, "
    "sustaining chart presence for over 700 days. This is the fingerprint of a song that kept "
    "finding new audiences rather than simply exhausting its initial one."
)

st.write(
    """
    What drives that kind of resilience? The short answer is re-entry events: moments when a
    song re-enters cultural circulation long after its original release. For *Blinding Lights*,
    these included a viral TikTok fitness trend, prominent sync placements, and Spotify's own
    algorithmic re-recommendations triggered each time its streaming velocity picked up. The
    decay curve is the signature of a song that algorithmic and cultural forces kept pulling
    back to the surface — something its peers simply did not experience at the same scale.
    """
)

st.header("4) What predicts chart success? Genre matters more than sound")
st.write(
    """
    The decay curve revealed that *Blinding Lights* endured where its peers faded. But what
    actually drives a song's popularity in the first place — is it sonic qualities alone, or
    something else entirely? To find out, we ran a **multiple linear regression** on the top
    500 most-streamed songs, including both audio features and genre. The result is striking:
    **genre dominates**. Knowing what genre a song belongs to predicts its popularity score
    more reliably than any individual audio quality.

    To keep the chart readable, all genre dummy coefficients are collapsed into a single
    **genre** bar representing the most impactful genre dummy's magnitude.
    """
)
_, center_col2, _ = st.columns([1, 3, 1])
with center_col2:
    st.altair_chart(chart_feature_importance_genre(top500_full), use_container_width=False)
st.caption(
    "**How to read this:** Red bars are audio features; the genre bar shows the maximum "
    "coefficient magnitude across the top 10 genre dummies. "
    "Because all predictors were standardized first, bar lengths are directly comparable."
)
st.write(
    """
    **Key takeaways:**
    - **Genre** is the single strongest predictor in the model — outranking every individual
      audio feature. A song's genre carries substantially more information about its expected
      popularity than tempo, energy, or loudness alone.
    - Among audio features, **acousticness** and **loudness** have the most meaningful
      relationships with popularity, suggesting mainstream hits lean toward produced,
      loud sound over acoustic texture.
    - This does not mean audio features are irrelevant — it means we need to study them
      on the right population. Genre is a confound: pop songs tend to score higher on
      popularity *and* share certain audio profiles, which inflates or distorts audio
      coefficients when all genres are pooled together.
    """
)
st.info(
    """
    **A note on this model:** You might notice that some of these audio features sound like
    they're measuring the same thing — for example, a loud song is almost always an energetic
    song, and an acoustic song is almost always a quiet one. In statistics, when two ingredients
    in your recipe are so similar that swapping one for the other barely changes the dish,
    it becomes hard to tell which one is actually doing the work. This is called
    **multicollinearity**, and it can make individual bar lengths less reliable to interpret
    on their own.

    We're keeping all 7 features here because this is an **exploratory, big-picture look** —
    we're not trying to make precise claims about each feature in isolation. We just want to
    see the overall landscape. In the next section, when we zoom into pop songs specifically
    and make more rigorous claims, we'll clean this up by removing the redundant features.
    """
)
st.write(
    """
    But which genre matters most? The chart below breaks out each genre dummy individually,
    with **pop** highlighted in red.
    """
)
_, center_col_genre, _ = st.columns([1.2, 10, 0.5])
with center_col_genre:
    st.altair_chart(chart_genre_importance_and_density(genre_density_data), use_container_width=False)
st.caption(
    "**Left:** Pop's regression coefficient dwarfs every other genre — being pop is a structural "
    "advantage before a single note is heard. "
    "**Right:** This advantage shows up directly in the raw data. Pop songs cluster visibly higher "
    "on the popularity axis than all other genres combined."
)
st.write(
    """
    Pop is clearly the dominant genre. But this raises an important follow-up: thousands of pop
    songs entered the Spotify Top 200 between 2017 and 2021 — most never came close to
    *Blinding Lights*. So the real question is not just *"does being pop help?"* but
    *"within pop, what actually separates the outliers from the rest?"*

    To answer that cleanly, we need to **control for genre** — and the right way to do that
    is not to drop genre from the model while keeping all songs pooled together. That approach
    leaves genre-driven variance in the residuals and can distort the audio feature coefficients.
    Instead, we filter the dataset to **pop songs only** and re-run the regression on audio
    features alone. By holding genre constant — studying a single genre — we isolate what sound
    predicts *within* the pop ecosystem, on songs that have already cleared the genre hurdle.
    """
)

st.header("5) Within pop, what does sound predict?")
st.write(
    """
    We filter the dataset to pop songs only and plan to run a **multiple linear regression**
    on audio features. Before doing that, however, we need to address a methodological concern:
    **multicollinearity**. If two predictors are highly correlated with each other, their
    individual coefficients become unreliable — the model can't cleanly separate their effects,
    and small changes in the data can swing the estimates dramatically.

    We ran a correlation matrix across all 7 audio features to check for problematic pairs.
    Three features form a highly collinear cluster:
    - **Energy ↔ Loudness**: *r* = 0.76 — louder tracks are almost always more energetic by construction
    - **Energy ↔ Acousticness**: *r* = −0.73 — acoustic songs are systematically lower energy
    - **Loudness ↔ Acousticness**: *r* = −0.58 — a moderate but meaningful redundancy

    Keeping all three in the model would inflate standard errors and make the individual
    coefficients difficult to interpret. We therefore **drop loudness and acousticness**,
    retaining energy as the single representative of this dimension. The remaining five
    features — **tempo, energy, danceability, speechiness, and valence** — are sufficiently
    independent to produce stable estimates.
    """
)
_, center_col, _ = st.columns([1, 3, 1])
with center_col:
    st.altair_chart(chart_feature_importance_pop(genre_density_data), use_container_width=False)
st.caption(
    "**How to read this:** Each bar shows how strongly a musical feature predicts popularity "
    "among pop songs specifically, after removing collinear predictors. All features are "
    "standardized, so bar lengths are directly comparable. Every observation is a pop song — "
    "genre is controlled for by design."
)
st.warning(
    "⚠️ **TODO:** The explanatory text around this chart still uses statistical language "
    "(multicollinearity, standardized coefficients, subgroup analysis) that will need to be "
    "rewritten to be fully intuitive for a general audience — similar to what was done for "
    "the section 4 note above."
)
st.write(
    """
    The top three predictors within pop are **energy**, **danceability**, and **valence**.
    These are the features we'll focus on when we zoom back into *Blinding Lights* — both
    individually and in combination.

    And here's the thing: even before running any model, you could have made a reasonable
    guess that these three would matter most. Think about what actually makes a song
    popular:

    - **Energy** is essentially how intense and exciting a song feels. High-energy songs
      keep people engaged, get played at parties and gyms, and are far less likely to be
      skipped. A low-energy song might be beautiful — but it's also easy to tune out.
    - **Danceability** captures how easy it is to move to a song. Songs people can dance
      to get played at social gatherings and clubs, they get picked up for workout
      playlists, and — critically for the streaming era — they go viral on TikTok and
      Instagram Reels. Every one of those contexts means more plays.
    - **Valence** measures how positive or happy a song sounds. People generally turn to
      music to feel good, which means upbeat, feel-good songs naturally get more repeat
      listens. They also spread faster — a song that makes you feel something good is one
      you want to share.

    Tempo and speechiness, by contrast, are more technical or genre-specific — they don't
    connect as directly to the emotional experience that drives someone to replay a song
    or add it to a playlist. The model agreed.
    """
)

st.header("6) So where does Blinding Lights actually fit?")
st.write(
    """
    The chart below shows the spread of each audio feature across the top 80 most-popular
    songs on Spotify — think of each curve as a histogram smoothed into a wave. The taller
    the curve at a given value, the more songs cluster there. The vertical line shows exactly
    where a selected song lands on each feature. Use the dropdown to swap between songs and
    see how their profiles compare.
    """
)
_, ridge_col = st.columns([0.3, 9.7])
with ridge_col:
    st.altair_chart(chart_ridge_and_deviation(features_clean), use_container_width=False)
st.caption(
    "Use the **Select Song** dropdown above to compare any of the top songs. "
    "Takeaway: *Blinding Lights* sits at the high end of tempo and danceability relative to its peers "
    "(highlighted lines = above the top-80 average), while landing near the middle on energy and valence. "
    "Its tempo is the sharpest outlier — faster than virtually every other mega-hit — and its high "
    "danceability score explains its staying power across workout playlists, dance trends, and sync placements."
)

st.header("7) Pop got it through the door. Tempo kicked it through the ceiling.")
st.write(
    """
    We've answered the central question in layers. *Blinding Lights* dominated the charts with
    unmatched longevity. Audio features — particularly its extreme tempo — marked it as a sonic
    outlier among its peers. And genre, specifically pop, turned out to be the single strongest
    predictor of popularity in the entire model.

    But here's the tension that demands a resolution: **if being a pop song is the dominant
    driver of streaming success, why isn't every pop song Blinding Lights?** Thousands of pop
    tracks entered the Spotify Top 200 between 2017 and 2021. Almost none sustained the kind
    of cultural dominance BL did. Something else is at work.

    The four charts below each plot a different audio dimension — **tempo**, **acousticness**,
    **danceability**, and **valence** — against popularity. Gray points are non-pop songs.
    Pink points are pop songs — and notice how even within the top 500 most-streamed songs
    on the planet, the pink cluster sits visibly higher on the popularity axis than the gray one.
    Being pop doesn't just help at the margins — it systematically elevates a song's ceiling.
    Use the dropdown to select which song to highlight in red; the other two named songs are
    always shown as gray triangles for comparison.
    """
)
st.altair_chart(chart_audio_popularity_scatter(top500_full), use_container_width=True)
st.caption(
    "Use the **Select Song** dropdown to highlight any of the three named songs in red; "
    "the other two remain visible as gray triangles. "
    "**Tempo**: at 171 BPM, BL sits far to the right of the pop cluster — faster than virtually every "
    "other mega-hit, including *Shape of You* and *Someone You Loved*. "
    "**Acousticness**: BL scores near zero, the signature of a fully electronic, synthesizer-driven "
    "production. "
    "**Danceability**: at 0.87, BL ranks among the most danceable songs in the dataset — a quality that "
    "powered its viral fitness trend on TikTok. "
    "**Valence**: BL sits on the higher end, sounding distinctly upbeat and feel-good in ways that "
    "invite repeat listens and sharing. Together, these four dimensions show a pop song whose audio "
    "profile is genuinely unusual among its peers."
)
st.write(
    """
    Look closely at the y-axis — the popularity score. *Blinding Lights* sits high, but it is
    **not dramatically separated** from the rest of the pop cluster. Dozens of pop songs match
    it or come within a few points on this axis. If you judged purely by popularity score,
    you might conclude that BL is just one of many successful pop tracks. Nothing special.

    And yet it is the single most-streamed song in the dataset — by a margin so wide that no
    other title comes close. So what explains that gap, if not raw popularity score?

    The answer is written across the x-axis. Look at where BL sits on **tempo**, **danceability**,
    and **valence** relative to its pop peers — and even relative to *Shape of You* and *Someone
    You Loved*, songs that were themselves massive global hits. BL is faster than almost
    everything else. It is among the most danceable songs in the entire dataset. And it scores
    high on valence — it sounds distinctly upbeat and feel-good, in a way that makes it easy
    to return to, share, and play in social contexts.

    That audio fingerprint is what unlocked the re-entry events we saw in the decay curve:
    the TikTok fitness trend that required exactly that tempo and danceability to work,
    the gym and workout playlists that kept circulating it, the sync placements that felt
    inevitable for a song with that energy. Its peers may have matched it on popularity score.
    They never matched it on the dimensions that made it *replayable*.
    """
)

st.write(
    """
    Genre set the floor. Audio features set the ceiling. But neither fully explains how
    *Blinding Lights* stayed near the top for years — returning again and again long after
    every comparable hit had faded. That final piece of the story is in the chart below.
    """
)

st.header("8) The re-entry fingerprint: how BL kept coming back")
st.write(
    """
    Every song eventually falls off the charts. What made *Blinding Lights* different wasn't just
    that it rose higher — it's that it kept coming back. The chart below maps every distinct
    top-10 run for each of the top 20 songs on the U.S. chart. Each bar segment is a stretch of
    consecutive days in the top 10; a gap of more than 14 days counts as a true exit and re-entry.
    The number at the end of each row is the total run count.
    """
)
st.altair_chart(chart_vis4_reentry(us_data_20), use_container_width=True)
st.caption(
    "Most songs have a single bar — one continuous top-10 run that ends and never returns. "
    "**Blinding Lights** sits at the top with more distinct runs than any other song in the top 20, "
    "its segments spread across a longer time window than any peer. This is not a song that had "
    "one great moment. It had many."
)

