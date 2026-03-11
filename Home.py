import streamlit as st

st.set_page_config(page_title="Spotify Charts: What Makes a Hit?", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, li, div, button, input, label {
        font-family: 'Lora', serif !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("The Anatomy of a Mega-Hit: What Does It Really Take to Top Spotify's Charts?")
st.image('images/drake_and_weeknd.jpg', use_container_width=True)
st.caption("Drake (left) and The Weeknd (right). Source: Sky News")
st.write(
    """
    Every day from 2017 to 2021, Spotify published its Top 200 chart for over 60 countries —
    a record of which songs people actually chose to listen to, at scale. Behind that data lies
    a deeper question: **what distinguishes a truly dominant song from one that peaked and faded?**
    """
)
st.write(
    """
    To answer that, we combine two complementary datasets. The first is a large-scale Spotify
    audio features dataset that includes detailed musical attributes of over 90,000 songs — among
    them danceability, energy, valence, tempo, and acousticness — along with Spotify's popularity
    score, allowing us to examine the structural "sound" of songs and which musical features are
    statistically associated with success. The second contains Spotify's complete global Top 200
    and Viral 50 chart history since January 1, 2017, providing daily rank trajectories across
    regions to measure longevity, decay patterns, re-entries, and cumulative dominance. Together,
    these datasets comprise 26 million rows of data — the patterns within them, in total streams,
    rank trajectories, sonic profiles, and chart longevity, tell a story about how music achieves
    and sustains cultural dominance in the streaming era.
    """
)

st.info(
    """
    **Sources**
    - Maharshi Pandya. (2022). *Spotify Tracks Dataset* [Data set]. Kaggle. https://doi.org/10.34740/KAGGLE/DSV/4372070
    - Dhruvil Dave. (2021). *Spotify Charts* [Data set]. Kaggle. https://doi.org/10.34740/KAGGLE/DS/1265407
    """
)

st.write(
    "To explore this visual data story, navigate the pages in the sidebar:\n"
    "- **Story**: The central narrative — from who dominated the charts globally, to how genre "
    "and audio features predict success, to how *Blinding Lights* emerged as an all-time anomaly "
    "through its decay curve, unique audio profile, and sustained global chart dominance.\n"
    "- **Conclusion**: What the full picture tells us about how music achieves and sustains "
    "cultural dominance in the streaming era.\n"
)

