import streamlit as st
import altair as alt
import pandas as pd
import json
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
    chart_choropleth,
    chart_vis4_reentry,
)

st.set_page_config(page_title="Story", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, li, div, button, input, label {
        font-family: 'Lora', serif !important;
    }
    </style>
""", unsafe_allow_html=True)

alt.data_transformers.disable_max_rows()

#  Data loading

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

    top6_choropleth = pd.read_csv('all_data/top6.csv', parse_dates=['date'])
    with open('all_data/custom.geo.json') as f:
        world_geojson = json.load(f)
    world_df = pd.DataFrame(world_geojson['features'])
    world_df['name'] = world_df['properties'].apply(lambda x: x['name'])
    world_df['pop'] = world_df['properties'].apply(lambda x: x['pop_est'])
    top6_choropleth.loc[top6_choropleth['region'] == 'Czech Republic', 'region'] = 'Czechia'
    top6_choropleth.loc[top6_choropleth['region'] == 'Dominican Republic', 'region'] = 'Dominican Rep.'
    top6_choropleth.loc[top6_choropleth['region'] == 'United States', 'region'] = 'United States of America'
    top6_choropleth = top6_choropleth[['title', 'date', 'region', 'streams']]
    song_streams_by_country = top6_choropleth.groupby(['title', 'region', 'date'])['streams'].sum().reset_index()
    song_streams_by_country = song_streams_by_country.merge(world_df[['name', 'pop']], left_on='region', right_on='name', how='left')
    song_streams_by_country = song_streams_by_country.drop(columns=['name'])
    song_streams_by_country['streams_per_capita'] = ((song_streams_by_country['streams'] / song_streams_by_country['pop']) * 100000).round(2)
    song_streams_by_country = song_streams_by_country.dropna()
    song_streams_by_country.rename(columns={'region': 'name'}, inplace=True)

    return top20_songs, us_data_20, top6_data, top500_full, genre_density_data, features_clean, song_streams_by_country, world_geojson

top20_songs, us_data_20, top6_data, top500_full, genre_density_data, features_clean, song_streams_by_country, world_geojson = load_all_data()

# Story

st.title("The Anatomy of a Mega-Hit")
st.markdown(
    "**Central question:** *What separates a mega-hit from just a popular song on Spotify — "
    "and do total stream counts tell the whole story?*"
)

st.write(
    """
    We start with the most obvious question: who actually led the charts? From there, the story
    moves in layers — from raw chart dominance, to how hits decay over time, to how far they
    travel globally, to what genre and audio features predict about success — all building toward
    a closer look at Blinding Lights — the most-streamed song in Spotify history,
    and the centerpiece of this analysis.
    """
)

st.header("1) Who Dominated the Charts?")
st.write(
    """
    The bar chart below ranks the 20 most-streamed songs globally. It is accompanied by a rank
    trajectory chart — showing how each song moved through the U.S. Top 200 over time. All bars
    and rank trajectories start gray — click any bar to highlight that song in color and see its
    corresponding rank trajectory. Use the brush selection at the bottom to zoom into a specific
    time window.
    """
)
st.altair_chart(chart_vis1_top20_streams(top20_songs, us_data_20), use_container_width=True)

st.write(
    """
    This first visualization is meant to be primarily exploratory. The data is there to interact with, and the patterns across the top 20 are for discovering on your
    own terms. A few observations about Blinding Lights specifically are worth noting, however:

    - **Blinding Lights is the most-streamed song in the dataset, sitting at around 2.4 billion total streams** — and its rank trajectory
      reflects why: rather than peaking and fading, it holds near the top of the U.S. chart
      for an unusually sustained stretch.
    - **The red dashed mean line puts the distribution in perspective.** Most songs in the top 20
      cluster near or below it, while a select few, including Blinding Lights, pulls ahead by a wide margin, skewing the mean upward. This concentration at the top is not random: it reflects algorithmic amplification, playlist placement, and the compounding effect of sustained chart presence. A song that stays in the top 50 for 18 months accumulates streams in ways that a two-week viral moment simply cannot match.
    """
)

st.header("2) The Decay Curve: Does Every Hit Fade at the Same Rate?")
st.write(
    """
    To isolate what made Blinding Lights structurally different, we normalize each song's
    timeline by days since its U.S. chart debut — removing the distortion of different release
    dates and letting us compare decay curves directly. The five peer songs are the next
    highest-streamed titles globally; all were massive hits by any standard.
    """
)
st.altair_chart(chart_vis2_decay_curve(top6_data), use_container_width=True)
st.write(
    "Many peer songs (Shape of You, bad guy, Dance Monkey) drop below rank 50 within roughly 200–400 days and never recover. "
    "Blinding Lights (red) does dip — but repeatedly resurfaces near the top 50, "
    "sustaining chart presence for over 600 days. This is the fingerprint of a song that kept "
    "finding new audiences rather than simply exhausting its initial one."
)

st.header("3) What the Numbers Alone Obscure")
st.write(
    """
    Stream counts and rank trajectories tell us that Blinding Lights dominated — but they don't
    tell us *why*. From the two charts above, we can observe that it outstreamed its peers and held
    the charts far longer than many comparable hits. What we cannot yet explain is what made it so
    structurally different in the first place.

    To answer that, we need to look beyond the numbers and into the music itself. This is where
    the analysis pivots: from observing dominance to trying to explain it. Specifically, we turn
    to audio features — measurable sonic attributes like tempo, danceability, energy, and valence
    — and genre, and ask whether Blinding Lights occupies an unusual corner of the musical
    landscape relative to other hits.
    """
)
st.info(
    "Blinding Lights' longevity, chart dominance, and global resonance raise a central question: "
    "what truly separates it from the other top songs of its time? "
    "From here, the analysis centers on that question, using genre and audio features "
    "to understand not just what made it successful, but what made it stand apart."
)

st.header("4) Across all songs, what predicts chart success?")
st.write(
    """
    What actually drives a song's popularity in the first place? Is it sonic qualities alone, or
    something else entirely? To find out, we ran a **multiple linear regression** on the
    top 1% most-streamed songs (roughly 500 tracks), including both audio features and genre. The result is striking:
    **genre dominates**. Knowing what genre a song belongs to predicts its popularity score far
    more reliably than any individual audio quality.

    To keep the chart readable, all genre dummy coefficients are collapsed into a single
    bar representing the most impactful genre dummy's magnitude.
    """
)
_, center_col2, _ = st.columns([1, 3, 1])
with center_col2:
    st.altair_chart(chart_feature_importance_genre(top500_full), use_container_width=False)
st.caption(
    "Red bars are audio features; the genre bar shows the maximum "
    "coefficient magnitude across the top 10 genre dummies. "
    "Because all predictors were standardized first, bar lengths are directly comparable."
)
st.info(
    """
    **A note on this model:** You might notice that some of the audio features sound like
    they're measuring the same thing — for example, a loud song is almost always an energetic
    song, and an acoustic song is almost always a quiet one. When two variables are this closely
    related, it becomes difficult for the model to tell which one is actually driving popularity.
    This is called multicollinearity, and it means the individual coefficients may be less
    reliable to interpret on their own, even if the model as a whole is still making good predictions.

    We're keeping all 7 features here because this is an exploratory, big-picture look —
    we're not trying to make precise claims about each feature in isolation. We just want to
    see the overall landscape. In the next section, when we zoom into pop songs specifically
    and make more rigorous claims, we'll clean this up by removing the redundant features.
    """
)
st.write(
    """
    **Key takeaways:**
    - Genre is the single strongest predictor in the model — outranking every individual
      audio feature by an enormous margin. A song's genre carries substantially more information about its expected
      popularity than features like tempo, energy, or loudness alone.
    - Among audio features, valence and danceability have the most meaningful
      relationships with popularity, suggesting mainstream hits lean toward upbeat, feel-good vibes and strong rhythmic qualities. 
    - This does not mean audio features are irrelevant — it means we need to study them
      on the right population. Genre is a confound: pop songs tend to score higher on
      popularity *and* share certain audio profiles, which inflates or distorts audio
      coefficients when all genres are pooled together.
    """
)
st.write(
    """
    But which genre matters most? The chart below breaks out each genre dummy individually,
    with **pop** highlighted in red.
    """
)
st.altair_chart(chart_genre_importance_and_density(genre_density_data), use_container_width=False)
st.caption(
    "**Left:** Pop's regression coefficient is the largest of any genre variable: being classified as pop "
    "is itself a strong positive predictor of popularity, independent of any audio features. "
    "**Right:** This advantage shows up directly in the raw data. Pop songs cluster visibly higher "
    "on the popularity axis than all other genres combined."
)
st.write(
    """
    Pop is clearly the dominant genre, and this is perhaps unsurprising, given that the majority
    of top 20 songs in the dataset, including Blinding Lights itself, are classified as pop.
    This analysis may have confirmed an initial belief you had that pop songs are structurally
    advantaged in popularity metrics. After all, there is a reason the genre is called "pop."
    But this raises an important follow-up: thousands of pop songs entered the Spotify Top 200
    between 2017 and 2021 — most never came close to Blinding Lights. So the real question
    is not just "does being pop help?" but "*within* pop, what actually separates the outliers
    from the rest?"

    To answer that cleanly, we need to **control for genre** — and the right way to do that
    is not to drop genre from the model while keeping all songs pooled together. That approach
    leaves genre-driven variance in the residuals and can distort the audio feature coefficients.
    Instead, we filter the dataset to pop songs **only** and re-run the regression on audio
    features alone. By holding genre constant (studying a single genre), we can isolate what sound
    predicts *within* the pop ecosystem itself.
    """
)

st.header("5) Within Pop, What Does Sound Predict?")
st.write(
    """
    We filter the dataset to pop songs only and plan to run a multiple linear regression
    on audio features. Before doing that, however, we need to address
    multicollinearity within our data, a problem we pointed out earlier. If two predictors are highly correlated with each other, their
    individual coefficients become unreliable — the model can't cleanly separate their effects,
    and small changes in the data can swing the estimates dramatically.

    We ran a correlation matrix across all 7 audio features to check for problematic pairs.
    Three features form a highly collinear cluster:
    - **Energy ↔ Loudness**: *r* = 0.76 — louder tracks are almost always more energetic 
    - **Energy ↔ Acousticness**: *r* = −0.73 — acoustic songs are systematically lower energy
    - **Loudness ↔ Acousticness**: *r* = −0.58 — a moderate but meaningful redundancy

    Keeping all three in the model would inflate standard errors and make the individual
    coefficients difficult to interpret. We therefore drop **loudness** and **acousticness**,
    keeping **energy** as the single representative of this dimension. The remaining five
    features — **tempo, energy, danceability, speechiness, and valence** — are sufficiently
    independent to produce stable estimates.
    """
)
_, center_col, _ = st.columns([1, 3, 1])
with center_col:
    st.altair_chart(chart_feature_importance_pop(genre_density_data), use_container_width=False)
st.caption(
    "Each bar shows how strongly a musical feature predicts popularity "
    "among pop songs specifically, after removing collinear predictors. All features are "
    "standardized, so bar lengths are directly comparable. Every observation is a pop song — "
    "genre is controlled for by design."
)
st.write(
    """
    The top three predictors within pop are **energy**, **danceability**, and **valence**.
    These are the features we'll focus on when we zoom back into Blinding Lights — both
    individually and in combination.

    Even before running any model, you could have made a reasonable
    guess that these three would matter most. Think about what actually makes a song
    popular:

    - **Energy** is essentially how intense and exciting a song feels. High-energy songs
      keep people engaged, get played at parties and gyms, and are far less likely to be
      skipped. A low-energy song might be beautiful, but it's also easy to tune out.
    - **Danceability** captures how easy it is to move to a song. Songs people can dance
      to get played at social gatherings and clubs, they get picked up for workout
      playlists, and — critically for the streaming era — they go viral on TikTok and
      Instagram Reels. Every one of those contexts means more plays.
    - **Valence** measures how positive or happy a song sounds. People generally turn to
      music to feel good, which means upbeat, feel-good songs naturally get more repeat
      listens. They also spread faster. Asong that makes you feel something good is one
      you want to share.

    Tempo and speechiness, by contrast, are more technical or genre-specific. They might not
    connect as directly to the emotional experience that drives someone to replay a song
    or add it to a playlist. 
    """
)

st.header("6) So Where Does Blinding Lights Actually Fit?")
st.write(
    """
    The ridge plot below shows the distribution of each audio feature across the top 1% most
    popular songs on Spotify. Each curve represents the density of songs at a given value:
    the taller the curve, the more songs cluster there. The vertical line shows where a selected
    song falls on each feature. Use the dropdown to swap between songs and compare their audio
    profiles. The bar chart to the right summarizes how far that song sits from the average
    on each feature. Bars extending right mean above average, bars extending left mean below.
    """
)
_, ridge_col = st.columns([0.3, 9.7])
with ridge_col:
    st.altair_chart(chart_ridge_and_deviation(features_clean), use_container_width=False)
st.write(
    """
    **Takeaways:**

    - **Tempo:** Blinding Lights sits at the far right of the tempo distribution — faster than
      virtually every other song in the top 1%. At 171 BPM, it is a genuine outlier, and this is
      likely the single most unusual thing about its audio profile. That tempo is fast enough to anchor a workout routine, sync with TikTok fitness trends, and sustain momentum in a way most pop songs don't.
    - **Danceability:** It also ranks among the most danceable songs in the dataset. Sitting at a value of 0.92, it's well above
      the average danceability for top-tier hits. High danceability is what makes a song feel physically
      irresistible: it invites movement, fits social contexts, and travels well across playlists
      and platforms.
    - **Valence:** Blinding Lights also lands on the highest end of the valence scale at 0.88, meaning it
      sounds distinctly upbeat and feel-good. Songs with high valence are easier to return to,
      easier to share, and more likely to be added to mood-based playlists, all of which
      compound streaming numbers over time.
    - **Energy and speechiness** are closer to the middle of the pack. Blinding Lights is
      energetic but not unusually so relative to its peers, and its low speechiness reflects
      that it is a sung track with minimal spoken or rap elements, typical of the genre.

    You can also compare Blinding Lights against Shape of You or
    Someone You Loved, the next top two songs in terms of total streams, and see how differently their audio profiles are positioned across
    the same distributions.
    """
)

st.header("7) Seeing the Outlier: BL vs. the Full Pop Landscape")
st.write(
    """
    The ridge plot confirmed that Blinding Lights is an outlier on tempo, danceability, and
    valence within the top 1%. But those distributions include all genres. The scatterplots
    below zoom out to the full top 1% and plot each audio feature directly against popularity
    score, letting us see where Blinding Lights sits not just within the distribution,
    but relative to every other song, pop or not.

    Each panel plots one audio feature on the x-axis and popularity on the y-axis. **Gray points**
    are non-pop songs; **pink points** are pop songs, and **dark red points** are the selected song. Use the **Select Song** dropdown to
    highlight one of the three named songs in red while the other two stay visible as gray triangles
    for comparison.
    """
)
st.altair_chart(chart_audio_popularity_scatter(top500_full), use_container_width=True)
st.write(
    """
    A few things stand out. On popularity score alone, Blinding Lights is high, but not
    dramatically separated from the rest of the pink cluster. Dozens of pop songs sit at a
    similar level. If that were the whole story, BL would look like just another successful
    pop track.

    But look across the x-axes. On **tempo**, BL sits far to the right of almost everything
    else — faster than Shape of You, faster than Someone You Loved, faster than the
    vast majority of the pop cluster. On **danceability**, it ranks near the top of the entire
    dataset. On **valence**, it skews upbeat relative to its peers. And on **acousticness**,
    it scores near zero. This is the signature of a fully electronic, synthesizer-driven production
    with no acoustic softness to dampen its momentum.
    """
)
st.info(
    "**A note on acousticness:** Acousticness was dropped from the pop regression model due to "
    "its correlation with energy. It is included here as a descriptive feature because "
    "Blinding Lights scores *exactly* zero — lower than every other song in the top 1% — "
    "reflecting a fully electronic, synthesizer-driven production. That is worth noting "
    "regardless of its predictive value in the model."
)
st.write(
    """
    This combination: extreme tempo, high danceability, positive valence, zero acousticness, *could* be
    what made it *replayable* in contexts its peers couldn't access: workout playlists,
    TikTok fitness trends, sync placements that demanded exactly that energy. For example, Someone You Loved
    is a slower, more acoustic, and less danceable song, which may have made it more likely to be added to "sad songs" playlists rather than "workout jams" or "TikTok hits," limiting its exposure in those high-velocity contexts.  In other words, BL's peers may
    have matched it on popularity score, but not necessarily on the factors that kept pulling it back.
    """
)

st.write(
    """
    Genre set the floor. Audio features set the ceiling. But neither fully explains how
    Blinding Lights stayed near the top for years — returning again and again long after
    every comparable hit had faded. That final piece of the story is in the charts below.
    """
)

st.header("8) A Global Phenomenon: How BL Spread Across the World")
st.write(
    """
    Streaming dominance isn't just about one market. The charts below compare Blinding Lights
    against the other top hits on a per-capita basis, normalizing streams by each country's
    population so that smaller countries aren't drowned out by large ones. Use the dropdown to
    select a comparison song, and click and drag on the timeline to zoom into any time window.
    The maps update to reflect the selected period.
    """
)
st.altair_chart(chart_choropleth(song_streams_by_country, world_geojson), use_container_width=True)
st.write(
    """
    Across the top six most-streamed songs, global reach is a given: these tracks travel far
    beyond their home markets, and each can spike to impressive peaks in per-capita listening.
    But the dashboard makes a less conspicuous point about what actually builds an all-time hit.
    Ed Sheeran's Shape of You briefly towers over the others with roughly 7.5 average streams
    per capita at its height, while Blinding Lights never breaks 5 and arrives later, with
    fewer calendar days to accumulate plays. And yet Blinding Lights ultimately out-streams
    them all — suggesting that the real engine of a "true" top hit is not just its virality,
    but its resilience.

    If you focus on the tail rather than the peak, the picture shifts. Even once it settles
    into its plateau, as all songs eventually do, Blinding Lights maintains its expansive,
    steady footprint — drawing meaningful streams from a broad mix of countries long after the
    initial spike has faded. Meanwhile, most of its peers do the opposite: their plateaus are
    narrow, and the global reach that once defined their peak dims.
    """
)

st.header("9) The Re-entry Fingerprint: How BL Kept Coming Back")

st.write(
    """
    Everything we have seen so far: the decay curve that never fully decayed, the global
    footprint that outlasted its peers, the audio profile built for replayability, points to
    the same underlying pattern: Blinding Lights did not just have a big moment. It had many.

    The chart below makes that literal. Each row represents one of the top 20 most-streamed
    songs on the U.S. chart. Each bar segment is a distinct stretch of consecutive days in the
    top 10; a gap of more than 14 days counts as a true exit and re-entry. The number at the
    end of each row is the total count of separate runs. Most songs have a single bar — one
    continuous top-10 run that ends and never returns.
    """
)
st.altair_chart(chart_vis4_reentry(us_data_20), use_container_width=True)
st.write(
    """
    Blinding Lights sits at the top: more distinct top-10 runs than any other song
    in the top 20 (apart from Sunflower), spread across a longer time window compared to most of its peers. Each re-entry represents
    a moment when the song found its way back into cultural circulation — perhaps a new TikTok trend, or an algorithmic recommendation triggered by a spike in streams. Its
    extreme tempo made it a natural fit for fitness content. Its danceability kept it relevant
    on social platforms. Its high valence made it easy to return to. These were not accidents:
    they are the audio fingerprint of a song structurally built to resurface.

    This is the final piece of the story. Total streams, chart longevity, distinct sonic profile, global reach, and
    re-entry count all converge on the same answer: what separated Blinding Lights from
    every other hit of its era was not a single exceptional quality, but the compounding
    effect of many qualities working together over time.

    The last section summarizes our findings and draws the narrative together.
    """
)

