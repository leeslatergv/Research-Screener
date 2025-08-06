import json
import pandas as pd
import streamlit as st
from datetime import datetime
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="DHSC Research Screener",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Dynamic, Themed CSS ---
def get_themed_css(theme):
    """
    Returns a string of CSS rules based on the selected theme.
    """
    # Define color palettes for both themes
    if theme == "Dark":
        # Dark Mode Palette
        bg_color = "#1e2124"
        text_color = "#f1f1f1"
        card_bg_color = "#2b2d31"
        card_border_color = "#404246"
        meta_text_color = "#a0a3a8"
        badge_keep_bg = "rgba(0, 173, 147, 0.2)"  # Teal with alpha
        badge_discard_bg = "rgba(204, 9, 47, 0.2)" # Red with alpha
    else:
        # Light Mode Palette (Original)
        bg_color = "#f3f2f1"
        text_color = "#0b0c0c"
        card_bg_color = "#ffffff"
        card_border_color = "#dee0e2"
        meta_text_color = "#505a5f"
        badge_keep_bg = "#e5f0ed"
        badge_discard_bg = "#fae6e9"

    # Use an f-string to inject the theme colors into the CSS rules
    css = f"""
    <style>
        :root {{
            --dhsc-teal: #00ad93;
            --dhsc-forest-green: #006652;
            --dhsc-red: #cc092f;
        }}
        html, body, [class*="st-"] {{ font-family: Arial, sans-serif; }}
        
        /* Main app background and text color */
        .stApp {{ background-color: {bg_color}; }}
        
        /* Header styles */
        .app-header {{ display: flex; align-items: center; border-bottom: 1px solid {card_border_color}; padding-bottom: 20px; margin-bottom: 20px; }}
        .header-line {{ width: 5px; height: 50px; background-color: var(--dhsc-teal); margin-right: 20px; }}
        .header-text h1 {{ font-weight: 700; font-size: 1.8rem; color: {text_color}; margin: 0; }}
        .header-text p {{ font-size: 1rem; color: {meta_text_color}; margin: 0; }}
        
        /* General text and metric styles */
        .stMarkdown, .stMetric, .stRadio {{ color: {text_color}; }}
        
        /* Custom button styles */
        .stButton>button {{ border-radius: 5px; font-weight: 700; padding: 10px 25px; border: 2px solid transparent; width: 100%; }}
        
        /* Paper card styling */
        .paper-card {{ background-color: {card_bg_color}; border: 1px solid {card_border_color}; border-radius: 5px; padding: 25px; margin-top: 20px; min-height: 400px; }}
        .paper-title {{ font-size: 1.4rem; font-weight: 700; color: {text_color}; line-height: 1.3; }}
        .paper-meta {{ font-size: 0.9rem; color: {meta_text_color}; }}
        .abstract-text {{ line-height: 1.6; color: {text_color}; text-align: justify; }}
        
        /* Decision badge styling */
        .decision-badge {{ padding: 8px 15px; border-radius: 5px; font-weight: 700; margin-bottom: 15px; font-size: 0.9rem; display: inline-block; }}
        .badge-keep {{ background: {badge_keep_bg}; color: var(--dhsc-forest-green); }}
        .badge-discard {{ background: {badge_discard_bg}; color: var(--dhsc-red); }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- State Management ---
def reset_state_with_new_file(uploaded_file):
    try:
        json_data = json.load(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
        st.session_state.papers = json_data
        st.session_state.total_papers = len(json_data)
        st.session_state.current_index = 0
        st.session_state.decisions = {}
        st.session_state.uploaded_file_name = uploaded_file.name
        st.success(f"Successfully loaded '{uploaded_file.name}' with {st.session_state.total_papers} papers.")
    except Exception as e:
        st.error(f"Failed to process file: {e}")
        st.session_state.papers = None

# --- Main App ---

# --- Sidebar for Theme and File Upload ---
with st.sidebar:
    st.markdown("### Settings")
    
    # Theme selector
    selected_theme = st.radio(
        "Choose App Theme",
        ("Light", "Dark"),
        key="theme",
        horizontal=True
    )
    
    st.markdown("---")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Research Data",
        type=['json'],
        help="Upload a JSON file containing a list of research papers."
    )

# Apply the selected theme's CSS
get_themed_css(selected_theme)

# --- App Header ---
st.markdown("""
    <div class="app-header">
        <div class="header-line"></div>
        <div class="header-text">
            <h1>Workforce Information & Analysis</h1>
            <p>Research Screening Tool</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- Initialize/Reset State on New File Upload ---
if uploaded_file is not None:
    if 'uploaded_file_name' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        reset_state_with_new_file(uploaded_file)

# --- Screening Interface (only shown if data is loaded) ---
if 'papers' in st.session_state and st.session_state.papers is not None:
    
    # --- Progress and Stats ---
    reviewed_count = len(st.session_state.decisions)
    kept_count = list(st.session_state.decisions.values()).count('keep')
    discarded_count = list(st.session_state.decisions.values()).count('discard')
    total_papers = st.session_state.total_papers

    col1, col2, col3 = st.columns(3)
    col1.metric("Reviewed", f"{reviewed_count}/{total_papers}")
    col2.metric("Kept", kept_count)
    col3.metric("Discarded", discarded_count)
    progress_value = (reviewed_count / total_papers) if total_papers > 0 else 0
    st.progress(progress_value)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Decision and Navigation Buttons ---
    is_screening_complete = (reviewed_count == total_papers)
    col1, col2, col3, col4 = st.columns(4)

    if col1.button("⬅️ Previous", disabled=(st.session_state.current_index == 0)):
        st.session_state.current_index -= 1
        st.rerun()

    if col2.button("❌ Discard", disabled=is_screening_complete):
        st.session_state.decisions[st.session_state.current_index] = 'discard'
        if st.session_state.current_index < total_papers - 1:
            st.session_state.current_index += 1
        st.rerun()

    if col3.button("✅ Keep", disabled=is_screening_complete):
        st.session_state.decisions[st.session_state.current_index] = 'keep'
        if st.session_state.current_index < total_papers - 1:
            st.session_state.current_index += 1
        st.rerun()

    if col4.button("Next ➡️", disabled=(st.session_state.current_index >= total_papers - 1)):
        st.session_state.current_index += 1
        st.rerun()
        
    # --- Paper Display / Completion Screen ---
    st.markdown('<div class="paper-card">', unsafe_allow_html=True)
    if is_screening_complete and total_papers > 0:
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

        st.markdown(f"**Paper {idx + 1} of {total_papers}**")
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
    st.info("Upload a JSON file using the sidebar to begin screening.")
