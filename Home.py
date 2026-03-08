import streamlit as st

st.set_page_config(page_title="Spotify Charts: What Makes a Hit?", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, li, span, div, button, input, label {
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
    a record of which songs people actually chose to listen to, at scale. This project treats
    that dataset as a lens for a deeper question: **what distinguishes a truly dominant song
    from one that simply had a good week?**
    """
)
st.write(
    """
    We approach this as a data journalism exercise. Good analysis starts with a well-motivated
    problem, moves through evidence-backed findings, and ends with inferences that can be drawn
    from the patterns uncovered. Here, the evidence is 26 million rows of daily streaming data
    spanning dozens of markets. The patterns — in total streams, rank trajectories, regional
    spread, and chart longevity — tell a story about how music achieves and sustains cultural
    dominance in the streaming era.
    """
)

st.write(
    "To explore this visual data story, navigate the pages in the sidebar:\n"
    "- **Central Narrative**: We begin by establishing which songs led the charts globally "
    "and examine what their rank trajectories reveal about staying power.\n"
    "- **Exploration**: Reader-driven tools for comparing songs, regions, and time windows.\n"
    "- **Methodology**: Key details about the dataset, filtering decisions, and limitations.\n"
)

st.info("Dataset: Spotify Daily Top 200 Charts (2017–2021) via `charts.csv`")
