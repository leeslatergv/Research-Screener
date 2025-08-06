import json
import pandas as pd
import streamlit as st
from datetime import datetime
import io

# --- Page Configuration and Styling ---
st.set_page_config(
    page_title="DHSC Research Screener",
    layout="centered"
)

def load_local_css():
    """Loads and injects the DHSC-compliant CSS."""
    css = """
    <style>
        :root {
            --dhsc-teal: #00ad93;
            --dhsc-forest-green: #006652;
            --dhsc-red: #cc092f;
            --dhsc-black: #0b0c0c;
            --dhsc-grey-1: #f3f2f1;
            --dhsc-grey-3: #505a5f;
            --dhsc-white: #ffffff;
        }
        html, body, [class*="st-"] { font-family: Arial, sans-serif; }
        .stApp { background-color: var(--dhsc-grey-1); }
        .app-header { display: flex; align-items: center; border-bottom: 1px solid #dee0e2; padding-bottom: 20px; margin-bottom: 20px; }
        .header-line { width: 5px; height: 50px; background-color: var(--dhsc-teal); margin-right: 20px; }
        .header-text h1 { font-weight: 700; font-size: 1.8rem; color: var(--dhsc-black); margin: 0; }
        .header-text p { font-size: 1rem; color: var(--dhsc-grey-3); margin: 0; }
        .stButton>button { border-radius: 5px; font-weight: 700; padding: 10px 25px; border: 2px solid transparent; width: 100%; }
        .paper-card { background-color: var(--dhsc-white); border: 1px solid #dee0e2; border-radius: 5px; padding: 25px; margin-top: 20px; min-height: 400px; }
        .paper-title { font-size: 1.4rem; font-weight: 700; color: var(--dhsc-black); line-height: 1.3; }
        .paper-meta { font-size: 0.9rem; color: var(--dhsc-grey-3); }
        .abstract-text { line-height: 1.6; color: var(--dhsc-black); text-align: justify; }
        .decision-badge { padding: 8px 15px; border-radius: 5px; font-weight: 700; margin-bottom: 15px; font-size: 0.9rem; display: inline-block; }
        .badge-keep { background: #e5f0ed; color: var(--dhsc-forest-green); }
        .badge-discard { background: #fae6e9; color: var(--dhsc-red); }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- State Management ---
def reset_state_with_new_file(uploaded_file):
    """Resets the screening progress and loads data from a new file."""
    try:
        # To read the uploaded file, it needs to be decoded.
        json_data = json.load(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
        
        st.session_state.papers = json_data
        st.session_state.total_papers = len(json_data)
        st.session_state.current_index = 0
        st.session_state.decisions = {}
        # Keep track of the file name to avoid resetting on every script rerun
        st.session_state.uploaded_file_name = uploaded_file.name
        st.success(f"Successfully loaded '{uploaded_file.name}' with {st.session_state.total_papers} papers.")
    except (json.JSONDecodeError, UnicodeDecodeError):
        st.error("Invalid JSON file. Please upload a valid JSON file containing a list of papers.")
        # Clear out any previous state if the new file is bad
        st.session_state.papers = None
    except Exception as e:
        st.error(f"An unexpected error occurred while processing the file: {e}")
        st.session_state.papers = None


# --- Main App ---

# Apply styling and display header
load_local_css()
st.markdown("""
    <div class="app-header">
        <div class="header-line"></div>
        <div class="header-text">
            <h1>Workforce Information & Analysis</h1>
            <p>Research Screening Tool</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Upload your research data",
    type=['json'],
    help="Please upload a JSON file where each entry is an object representing a research paper."
)

# Check if a new file has been uploaded and reset state if necessary
if uploaded_file is not None:
    # If it's the first upload or a different file, reset the state
    if 'uploaded_file_name' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        reset_state_with_new_file(uploaded_file)

# --- Screening Interface (only shown if data is loaded) ---

if 'papers' in st.session_state and st.session_state.papers is not None:
    # --- Progress and Stats ---
    reviewed_count = len(st.session_state.decisions)
    kept_count = list(st.session_state.decisions.values()).count('keep')
    discarded_count = list(st.session_state.decisions.values()).count('discard')

    col1, col2, col3 = st.columns(3)
    col1.metric("Reviewed", f"{reviewed_count}/{st.session_state.total_papers}")
    col2.metric("Kept", kept_count)
    col3.metric("Discarded", discarded_count)

    progress_value = (reviewed_count / st.session_state.total_papers) if st.session_state.total_papers > 0 else 0
    st.progress(progress_value)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Decision and Navigation Buttons ---
    is_screening_complete = reviewed_count == st.session_state.total_papers
    col1, col2, col3, col4 = st.columns(4)

    if col1.button("⬅️ Previous", disabled=(st.session_state.current_index == 0)):
        st.session_state.current_index -= 1
        st.rerun()

    if col2.button("❌ Discard", disabled=is_screening_complete):
        st.session_state.decisions[st.session_state.current_index] = 'discard'
        if st.session_state.current_index < st.session_state.total_papers - 1:
            st.session_state.current_index += 1
        st.rerun()

    if col3.button("✅ Keep", disabled=is_screening_complete):
        st.session_state.decisions[st.session_state.current_index] = 'keep'
        if st.session_state.current_index < st.session_state.total_papers - 1:
            st.session_state.current_index += 1
        st.rerun()

    if col4.button("Next ➡️", disabled=(st.session_state.current_index >= st.session_state.total_papers - 1)):
        st.session_state.current_index += 1
        st.rerun()

    # --- Paper Display / Completion Screen ---
    st.markdown('<div class="paper-card">', unsafe_allow_html=True)

    if is_screening_complete and st.session_state.total_papers > 0:
        st.success("🎉 All papers have been reviewed!")
        st.markdown(f"**Final Tally:** You kept **{kept_count}** and discarded **{discarded_count}** papers.")
        st.balloons()
    else:
        idx = st.session_state.current_index
        paper = st.session_state.papers[idx]

        if idx in st.session_state.decisions:
            decision = st.session_state.decisions[idx]
            badge_class = "badge-keep" if decision == 'keep' else "badge-discard"
            st.markdown(f'<div class="decision-badge {badge_class}">Previously marked as: {decision.upper()}</div>', unsafe_allow_html=True)

        st.markdown(f"**Paper {idx + 1} of {st.session_state.total_papers}**")
        st.markdown(f'<p class="paper-title">{paper.get("title", "No Title")}</p>', unsafe_allow_html=True)
        authors = ", ".join(paper.get("authors", [])) if isinstance(paper.get("authors"), list) else paper.get("authors", "N/A")
        st.markdown(f'<p class="paper-meta"><strong>Authors:</strong> {authors}<br><strong>Year:</strong> {paper.get("year", "N/A")}</p>', unsafe_allow_html=True)
        
        if paper.get("link") and paper.get("link") != 'N/A':
            st.link_button("View Full Text ↗️", paper["link"])
            
        st.markdown("**Abstract**")
        st.markdown(f'<p class="abstract-text">{paper.get("abstract", "No abstract available.")}</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # --- Export Section ---
    if reviewed_count > 0:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Export Decisions")
        
        export_data = [dict(p, decision=st.session_state.decisions.get(i)) for i, p in enumerate(st.session_state.papers) if i in st.session_state.decisions]
        df = pd.DataFrame(export_data)

        csv_bytes = df.to_csv(index=False, encoding='utf-8').encode('utf-8')
        kept_papers = [p for p in export_data if p['decision'] == 'keep']
        json_bytes = json.dumps(kept_papers, indent=2).encode('utf-8')

        d_col1, d_col2 = st.columns(2)
        d_col1.download_button("📥 Download All Decisions (CSV)", csv_bytes, f"screening_decisions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)
        d_col2.download_button("📥 Download Kept Papers (JSON)", json_bytes, f"kept_papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json", use_container_width=True)

else:
    # This message is shown before any file is uploaded
    st.info("Please upload a JSON file to begin screening.")
