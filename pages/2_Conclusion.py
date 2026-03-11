import streamlit as st

st.set_page_config(page_title="Conclusion", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, li, div, button, input, label {
        font-family: 'Lora', serif !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Conclusion")

st.header("Revisiting Our Central Questions")

st.write(
    """
    **Question 1: Does total stream count tell the whole story — or is something else driving
    the gap between a mega-hit and just a popular song?**

    Total stream count does not tell the whole story. Shape of You peaked higher in per-capita
    listening — roughly 7.5 average streams per 100,000 people at its height — while Blinding
    Lights never broke 5, and arrived later with fewer calendar days to accumulate plays. By
    the logic of peak virality alone, Shape of You should be the all-time leader. It is not.
    What separates Blinding Lights is not how high it spiked, but how long it held. Its global
    footprint remained broad and active long after its initial peak faded, while its peers'
    plateaus narrowed. The real engine of an all-time streaming record is not virality: it is
    resilience.
    """
)

st.write(
    """
    **Question 2: What truly separates Blinding Lights from the other top songs of its time?**

    Three things, working together:

    - **Genre.** Being classified as pop is itself a structural advantage — our regression showed
      it outweighs every individual audio feature as a predictor of popularity. Blinding Lights
      cleared that hurdle before a single note was heard.
    - **An outlier audio profile.** Within pop, the features that matter most are energy,
      danceability, and valence. On all three, Blinding Lights scores at or near the top of
      the entire dataset. At a tempo of 171 BPM, near-zero acousticness, valence of 0.88, and a danceability score of 0.92,
      it occupies a corner of the pop audio space that Shape of You and Someone You Loved
      — themselves massive global hits — didn't achieve. That profile is what made it
      structurally suited for fitness playlists, TikTok trends, and the social contexts that
      generate re-streams.
    - **Longevity.** More distinct top-10 re-entries than any other song in the top 20. A decay
      curve that dipped but never flatlined. A global footprint that outlasted every peer. These
      are not separate facts, but rather the compounding result of the audio fingerprint above.
    """
)

st.header("Ultimately, What is the Anatomy of a Streaming Phenomenon?")
st.write(
    """
    Fully assembled, we think the picture looks like this:

    - **A pop song** — with the playlist access, algorithmic priority, and mainstream visibility
      that label confers. Genre sets the floor, and Blinding Lights stood on solid ground.
    - **An outlier audio profile** — faster, more electric, and more danceable than virtually
      any of its pop peers, occupying a corner of the audio space that made it uniquely
      suited to the contexts that drive repeat streaming.
    - **A longevity engine** — re-entry events that kept resurfacing it long after typical hits
      had faded: a viral fitness trend, sync placements, algorithmic re-recommendations, each
      one triggering another influx of streams.

    Total streams reward scale. Chart position rewards recurrence. The rarest achievement in
    the streaming era is a song that earns both — repeatedly, across years and markets. Genre
    explains why Blinding Lights was in the conversation. Everything else explains why it
    never left.
    """
)

st.write(
    """
    And the story didn't end when our dataset did. At the close of the 2017–2021 window we
    analyzed, Blinding Lights had accumulated approximately **2.4 billion streams**, already a staggering number. As of today, it sits at **5.3 billion streams**, and it remains the most-streamed song in Spotify's entire history. **No song
    released since has surpassed it.**

    That trajectory — more than doubling its stream count after the period we studied —
    is itself the final proof of everything the data showed us. The re-entry events didn't
    stop. The playlists kept circulating it. New listeners kept finding it. A song with the
    right audio fingerprint, in the right genre, with the right longevity engine behind it,
    doesn't just top the charts. It compounds. We believe that isn't just luck, but structure.
    """
)

st.header("Limitations and Future Work")
st.write(
    """
    - **Correlation, not causation.** Rank trajectories, audio features, and global streaming
      patterns can reveal associations, but they cannot establish what actually caused Blinding
      Lights to succeed. Popularity is shaped by forces our dataset does not capture: marketing
      budgets, algorithmic promotion, audience demographics, cultural context, and timing. Any
      conclusions here should be read as observational, not causal.
    - **Popularity is a narrow measure.** Our analysis defines success strictly as Spotify streams
      within the 2017–2021 window. This excludes radio play, sales, social media reach, and
      cultural impact by any other metric. A song highly successful by those measures might look
      unremarkable in this dataset, and vice versa.
    - **Spotify's geographic gaps introduce systemic bias.** Spotify is unavailable in a number
      of countries and territories — most significantly China. Global stream counts and per-capita
      maps therefore reflect Spotify's user base, not global music consumption. Any conclusions
      about worldwide reach are limited to markets where Spotify operates.
    - **Future work.** A natural extension of this analysis would incorporate cross-platform data
      — YouTube views, TikTok engagement, radio airplay, and sales figures — to test whether the
      patterns observed here hold beyond Spotify. On the methodology side, a more rigorous causal
      framework, such as a difference-in-differences design around specific re-entry events like
      the TikTok fitness trend, could move the analysis from correlation toward a more defensible
      claim about what actually drove Blinding Lights' longevity.
    """
)

