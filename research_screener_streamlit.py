import json
import pandas as pd
import streamlit as st
from datetime import datetime
import io
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="DHSC Research Screener",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Data Parsing for the Specific JSON Structure ---
def parse_serpapi_paper(paper: dict) -> dict:
    """
    Parses a single paper object from the SerpApi JSON structure
    and returns a standardized, clean dictionary.
    """
    # Extract authors
    authors_list = paper.get('publication_info.authors', [])
    if isinstance(authors_list, list) and authors_list:
        authors = ", ".join([author.get('name', 'N/A') for author in authors_list])
    else:
        # Fallback to the summary if author list is empty
        authors_summary = paper.get('publication_info.summary', '').split(' - ')[0]
        authors = authors_summary

    # Extract year from summary using regex
    summary = paper.get('publication_info.summary', '')
    year_match = re.search(r'\b(19|20)\d{2}\b', summary)
    year = year_match.group(0) if year_match else "N/A"

    return {
        "title": paper.get('title', 'No Title Provided'),
        "authors": authors,
        "year": year,
        "abstract": paper.get('snippet', 'No abstract or snippet available.'),
        "link": paper.get('link', '#'),
        "original_data": paper # Keep original data for export if needed
    }


# --- Dynamic, Themed CSS ---
def get_themed_css(theme):
    if theme == "Dark":
        bg_color, text_color, card_bg_color, card_border_color, meta_text_color, badge_keep_bg, badge_discard_bg = (
            "#1e2124", "#f1f1f1", "#2b2d31", "#404246", "#a0a3a8", "rgba(0, 173, 147, 0.2)", "rgba(204, 9, 47, 0.2)")
    else:
        bg_color, text_color, card_bg_color, card_border_color, meta_text_color, badge_keep_bg, badge_discard_bg = (
            "#f3f2f1", "#0b0c0c", "#ffffff", "#dee0e2", "#505a5f", "#e5f0ed", "#fae6e9")

    css = f"""
    <style>
        :root {{ --dhsc-teal: #00ad93; --dhsc-forest-green: #006652; --dhsc-red: #cc092f; }}
        html, body, [class*="st-"] {{ font-family: Arial, sans-serif; }}
        .stApp {{ background-color: {bg_color}; }}
        .app-header {{ display: flex; align-items: center; border-bottom: 1px solid {card_border_color}; padding-bottom: 20px; margin-bottom: 20px; }}
        .header-line {{ width: 5px; height: 50px; background-color: var(--dhsc-teal); margin-right: 20px; }}
        .header-text h1 {{ font-weight: 700; font-size: 1.8rem; color: {text_color}; margin: 0; }}
        .header-text p {{ font-size: 1rem; color: {meta_text_color}; margin: 0; }}
        .stMarkdown, .stMetric, .stRadio {{ color: {text_color}; }}
        .stButton>button {{ border-radius: 5px; font-weight: 700; padding: 10px 25px; border: 2px solid transparent; width: 100%; }}
        .paper-card {{ background-color: {card_bg_color}; border: 1px solid {card_border_color}; border-radius: 5px; padding: 25px; margin-top: 20px; min-height: 400px; }}
        .paper-title {{ font-size: 1.4rem; font-weight: 700; color: {text_color}; line-height: 1.3; }}
        .paper-meta {{ font-size: 0.9rem; color: {meta_text_color}; }}
        .abstract-text {{ line-height: 1.6; color: {text_color}; text-align: justify; }}
        .decision-badge {{ padding: 8px 15px; border-radius: 5px; font-weight: 700; margin-bottom: 15px; font-size: 0.9rem; display: inline-block; }}
        .badge-keep {{ background: {badge_keep_bg}; color: var(--dhsc-forest-green); }}
        .badge-discard {{ background: {badge_discard_bg}; color: var(--dhsc-red); }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- State Management ---
def reset_state_with_new_file(uploaded_file):
    try:
        raw_json_data = json.load(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
        
        # Use the parser to transform the raw data into a clean, standardized format
        st.session_state.papers = [parse_serpapi_paper(p) for p in raw_json_data]
        
        st.session_state.total_papers = len(st.session_state.papers)
        st.session_state.current_index = 0
        st.session_state.decisions = {}
        st.session_state.uploaded_file_name = uploaded_file.name
        st.success(f"Successfully loaded and parsed '{uploaded_file.name}' with {st.session_state.total_papers} papers.")
    except Exception as e:
        st.error(f"Failed to process file. Please ensure it's a valid JSON from the expected source. Error: {e}")
        st.session_state.papers = None

# --- Main App ---

# Sidebar for Theme and File Upload
with st.sidebar:
    st.markdown("### Settings")
    selected_theme = st.radio("Choose App Theme", ("Light", "Dark"), key="theme", horizontal=True)
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload Research Data", type=['json'], help="Upload a JSON file from SerpApi.")

# Apply CSS based on theme selection
get_themed_css(selected_theme)

# App Header
st.markdown("""
    <div class="app-header"><div class="header-line"></div>
    <div class="header-text"><h1>Workforce Information & Analysis</h1><p>Research Screening Tool</p></div></div>
    """, unsafe_allow_html=True)

# Initialize or reset state on new file upload
if uploaded_file is not None:
    if 'uploaded_file_name' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        reset_state_with_new_file(uploaded_file)

# --- Main Screening Interface ---
if 'papers' in st.session_state and st.session_state.papers is not None:
    # Stats and Progress
    reviewed_count = len(st.session_state.decisions)
    kept_count = list(st.session_state.decisions.values()).count('keep')
    discarded_count = list(st.session_state.decisions.values()).count('discard')
    total_papers = st.session_state.total_papers

    col1, col2, col3 = st.columns(3)
    col1.metric("Reviewed", f"{reviewed_count}/{total_papers}")
    col2.metric("Kept", kept_count)
    col3.metric("Discarded", discarded_count)
    st.progress((reviewed_count / total_papers) if total_papers > 0 else 0)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Navigation and Decision Buttons
    is_screening_complete = (reviewed_count == total_papers)
    col1, col2, col3, col4 = st.columns(4)

    if col1.button("⬅️ Previous", disabled=(st.session_state.current_index == 0)):
        st.session_state.current_index -= 1; st.rerun()
    if col2.button("❌ Discard", disabled=is_screening_complete):
        st.session_state.decisions[st.session_state.current_index] = 'discard'
        if st.session_state.current_index < total_papers - 1: st.session_state.current_index += 1
        st.rerun()
    if col3.button("✅ Keep", disabled=is_screening_complete):
        st.session_state.decisions[st.session_state.current_index] = 'keep'
        if st.session_state.current_index < total_papers - 1: st.session_state.current_index += 1
        st.rerun()
    if col4.button("Next ➡️", disabled=(st.session_state.current_index >= total_papers - 1)):
        st.session_state.current_index += 1; st.rerun()
        
    # --- FIX for the empty box ---
    # The paper card is only created if there is something to display inside it.
    if is_screening_complete and total_papers > 0:
        st.success("🎉 All papers have been reviewed!")
        st.markdown(f"**Final Tally:** You kept **{kept_count}** and discarded **{discarded_count}** papers.")
        st.balloons()
    else:
        # Display Area for the current paper
        st.markdown('<div class="paper-card">', unsafe_allow_html=True)
        idx = st.session_state.current_index
        # Now we use the clean, parsed paper data
        paper = st.session_state.papers[idx]

        if idx in st.session_state.decisions:
            decision = st.session_state.decisions[idx]
            badge_class = "badge-keep" if decision == 'keep' else "badge-discard"
            st.markdown(f'<div class="decision-badge {badge_class}">Previously marked as: {decision.upper()}</div>', unsafe_allow_html=True)

        st.markdown(f"**Paper {idx + 1} of {total_papers}**")
        st.markdown(f'<p class="paper-title">{paper["title"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="paper-meta"><strong>Authors:</strong> {paper["authors"]}<br><strong>Year:</strong> {paper["year"]}</p>', unsafe_allow_html=True)
        
        if paper["link"] and paper["link"] != '#':
            st.link_button("View Full Text ↗️", paper["link"])
            
        st.markdown("**Abstract / Snippet**")
        st.markdown(f'<p class="abstract-text">{paper["abstract"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Export Section
    if reviewed_count > 0:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Export Decisions")
        # Prepare a clean DataFrame for export
        export_list = []
        for i, decision in st.session_state.decisions.items():
            clean_paper = st.session_state.papers[i]
            export_list.append({
                "decision": decision,
                "title": clean_paper['title'],
                "authors": clean_paper['authors'],
                "year": clean_paper['year'],
                "link": clean_paper['link'],
                "abstract": clean_paper['abstract']
            })
        df = pd.DataFrame(export_list)
        csv_bytes = df.to_csv(index=False, encoding='utf-8').encode('utf-8')
        json_bytes = df[df['decision'] == 'keep'].to_json(orient='records', indent=2).encode('utf-8')

        d_col1, d_col2 = st.columns(2)
        d_col1.download_button("📥 Download All Decisions (CSV)", csv_bytes, f"screening_decisions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)
        d_col2.download_button("📥 Download Kept Papers (JSON)", json_bytes, f"kept_papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json", use_container_width=True)

else:
    st.info("Upload a JSON file using the sidebar to begin screening.")
