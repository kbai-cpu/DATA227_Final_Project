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

st.header("What the data tells us — and what happened next")
st.write(
    """
    This is the anatomy of a streaming phenomenon, fully assembled:

    - **A pop song** — with the playlist access, algorithmic priority, and mainstream visibility
      that label confers. Genre is the floor, and BL stood on solid ground.
    - **An outlier audio profile** — faster, more electric, and more danceable than virtually any
      of its pop peers. At 171 BPM, near-zero acousticness, and a danceability score of 0.87,
      it occupies a corner of the pop audio space that *Shape of You* and *Someone You Loved* —
      themselves global hits — never came close to.
    - **A longevity engine** — re-entry events that kept resurfacing it long after typical hits
      had faded: a viral fitness trend, sync placements, algorithmic re-recommendations, each one
      triggering another cycle of streams.

    Total streams reward scale. Chart position rewards recurrence. But the rarest achievement
    in the streaming era is a song that earns both — repeatedly, across years and cultures.
    Genre explains why *Blinding Lights* was in the conversation. Everything else explains why
    it never left.
    """
)
st.write(
    """
    And the story didn't end when our dataset did. At the close of the 2017–2021 window we
    analyzed, *Blinding Lights* had accumulated approximately **2.4 billion streams**. A
    staggering number — and yet only the beginning. As of today, it sits at **5.3 billion
    streams**, and it remains the most-streamed song in Spotify's entire history. No song
    released since has surpassed it.

    That trajectory — more than doubling its stream count *after* the period we studied —
    is itself the final proof of everything the data showed us. The re-entry events didn't
    stop. The playlists kept circulating it. New listeners kept finding it. A song with the
    right audio fingerprint, in the right genre, with the right longevity engine behind it,
    doesn't just top the charts. It compounds. Five years after its release, *Blinding Lights*
    is still accumulating streams at a pace that most songs will never reach in their entire
    lifetime. That is not luck. That is structure.
    """
)
