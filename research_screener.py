import json
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime
import tldextract
import base64
import io
import re  # Added for regular expression matching

# --- The app now starts without loading any data initially ---

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])

# --- REVISED SECTION from original code (No changes needed here) ---

# A map for custom, clean names of common publishers.
SOURCE_MAP = {
    'taylorfrancis': 'Taylor & Francis',
    'springer': 'Springer',
    'wiley': 'Wiley',
    'sagepub': 'SAGE Publications',
    'cambridge': 'Cambridge University Press',
    'mdpi': 'MDPI',
    'ncbi': 'PubMed Central',
    'jstor': 'JSTOR',
    'proquest': 'ProQuest',
    'csiro': 'CSIRO Publishing',
    'lww': 'Lippincott Williams & Wilkins',
    'healio': 'Healio',
    'degruyterbrill': 'De Gruyter Brill',
    'sciencedirect': 'ScienceDirect',
    'elsevier': 'Elsevier',
    'informit': 'Informit',
    'jamanetwork': 'JAMA Network',
    'healthaffairs': 'Health Affairs',
    'academicradiology': 'Academic Radiology',
    'researchgate': 'ResearchGate'
}

def extract_source(link):
    if pd.isna(link) or link == 'N/A' or link == '#':
        return 'Source unknown'
    try:
        extracted = tldextract.extract(link)
        domain = extracted.domain
        if domain in SOURCE_MAP:
            return SOURCE_MAP[domain]
        return domain.title()
    except Exception:
        try:
            domain_part = link.split('/')[2]
            return domain_part.replace('www.', '').title()
        except IndexError:
            return 'Invalid link'

# --- End of previously revised section ---


# Custom CSS for DHSC aesthetics (with added styles for upload component)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --dhsc-teal: #00ad93;
                --dhsc-forest-green: #006652;
                --dhsc-red: #cc092f;
                --dhsc-black: #0b0c0c;
                --dhsc-grey-1: #f3f2f1;
                --dhsc-grey-2: #dee0e2;
                --dhsc-grey-3: #b1b4b6;
            }

            body {
                font-family: Arial, sans-serif;
                background-color: var(--dhsc-grey-1);
                color: var(--dhsc-black);
                min-height: 100vh;
                margin: 0;
            }
            
            .dhsc-container {
                background: white;
                border: 1px solid var(--dhsc-grey-2);
                border-top-right-radius: 20px;
                border-bottom-left-radius: 20px;
                border-top-left-radius: 5px;
                border-bottom-right-radius: 5px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                margin: 20px auto;
                max-width: 960px;
                padding: 40px;
            }
            
            /* --- UPLOAD STYLES START --- */
            .upload-container {
                text-align: center;
                padding: 50px;
                border: 2px dashed var(--dhsc-grey-3);
                border-radius: 10px;
                background-color: white;
            }
            
            .upload-container:hover {
                border-color: var(--dhsc-teal);
                background-color: #f9f9f9;
            }
            
            .upload-icon {
                font-size: 3rem;
                color: var(--dhsc-teal);
            }
            
            .upload-text {
                margin-top: 15px;
                font-size: 1.2rem;
                font-weight: 700;
                color: var(--dhsc-black);
            }
            
            .upload-hint {
                color: #505a5f;
                font-size: 0.9rem;
            }
            /* --- UPLOAD STYLES END --- */
            
            .app-header {
                display: flex;
                align-items: center;
                border-bottom: 1px solid var(--dhsc-grey-2);
                padding-bottom: 20px;
                margin-bottom: 30px;
            }
            
            .header-line {
                width: 5px;
                height: 50px;
                background-color: var(--dhsc-teal);
                margin-right: 20px;
            }
            
            .header-text h1 {
                font-weight: 700;
                font-size: 1.8rem;
                color: var(--dhsc-black);
                margin: 0;
            }
            
            .header-text p {
                font-size: 1rem;
                color: #505a5f;
                margin: 0;
            }
            
            .progress-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            
            .progress-stat {
                background-color: var(--dhsc-grey-1);
                border-radius: 5px;
                padding: 20px;
                text-align: center;
            }
            
            .progress-stat h3 {
                font-size: 2.2rem;
                font-weight: 700;
                margin: 0;
                color: var(--dhsc-black);
            }
            
            .progress-stat p {
                margin: 0;
                font-size: 0.9rem;
                color: #505a5f;
            }
            
            #kept-counter { color: var(--dhsc-forest-green); }
            #discarded-counter { color: var(--dhsc-red); }
            
            .progress {
                height: 10px;
                border-radius: 50px;
                background-color: var(--dhsc-grey-2);
            }
            
            .progress-bar {
                background-color: var(--dhsc-teal);
            }
            
            .paper-card {
                padding-top: 20px;
                min-height: 450px;
            }
            
            .paper-number {
                color: var(--dhsc-teal);
                font-weight: 700;
                font-size: 1rem;
                margin-bottom: 15px;
            }
            
            .paper-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--dhsc-black);
                line-height: 1.3;
                margin-bottom: 20px;
            }
            
            .paper-meta {
                background: var(--dhsc-grey-1);
                border-radius: 5px;
                padding: 20px;
                margin-bottom: 20px;
                font-size: 0.95rem;
            }
            
            .meta-item {
                display: flex;
                margin-bottom: 10px;
            }
            
            .meta-item:last-child { margin-bottom: 0; }
            
            .meta-label {
                font-weight: 700;
                color: var(--dhsc-black);
                min-width: 90px;
            }
            
            .meta-value { color: #505a5f; }
            
            .abstract-label {
                font-weight: 700;
                color: var(--dhsc-black);
                margin-bottom: 10px;
                display: block;
            }
            
            .abstract-text {
                line-height: 1.7;
                color: var(--dhsc-black);
                text-align: justify;
            }
            
            .action-buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-top: 30px;
                border-top: 1px solid var(--dhsc-grey-2);
                padding-top: 30px;
            }
            
            .btn-custom {
                padding: 10px 25px;
                border-radius: 5px;
                font-weight: 700;
                font-size: 1rem;
                border: 2px solid transparent;
                transition: all 0.2s ease;
                min-width: 130px;
            }
            
            .btn-keep {
                background-color: var(--dhsc-forest-green);
                color: white;
            }
            .btn-keep:hover { background-color: #004c3d; }
            
            .btn-discard {
                background-color: var(--dhsc-red);
                color: white;
            }
            .btn-discard:hover { background-color: #a50725; }
            
            .btn-nav {
                background-color: white;
                color: var(--dhsc-black);
                border-color: var(--dhsc-grey-3);
            }
            
            .btn-nav:hover:not(:disabled) {
                background-color: var(--dhsc-black);
                color: white;
            }
            .btn-nav:disabled { opacity: 0.5; cursor: not-allowed; }
            
            .decision-badge {
                display: inline-block;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: 700;
                margin-bottom: 15px;
                font-size: 0.9rem;
            }
            
            .badge-keep {
                background: #e5f0ed;
                color: var(--dhsc-forest-green);
            }
            
            .badge-discard {
                background: #fae6e9;
                color: var(--dhsc-red);
            }
            
            .export-section {
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid var(--dhsc-grey-2);
            }
            
            .btn-export {
                background-color: var(--dhsc-teal);
                color: white;
                padding: 10px 30px;
                font-weight: 700;
                border-radius: 5px;
                border: none;
            }
            .btn-export:hover { background-color: #008a70; }
            
            .completion-screen {
                text-align: center;
                padding: 50px 20px;
            }
            
            .completion-icon {
                font-size: 4rem;
                color: var(--dhsc-forest-green);
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout
app.layout = html.Div([
    # Data stores for holding state in the user's browser
    dcc.Store(id='stored-data'),  # Will hold the list of paper dictionaries
    dcc.Store(id='decision-store'), # Will hold the dictionary of decisions {index: 'decision'}

    dbc.Container([
        # Header (always visible)
        html.Div([
            html.Div(className="header-line"),
            html.Div([
                html.H1("Workforce Information & Analysis"),
                html.P("Research Screening Tool")
            ], className="header-text")
        ], className="app-header"),
        
        # Upload section (visible at start)
        html.Div([
            dcc.Upload(
                id='upload-data',
                className='upload-container',
                children=html.Div([
                    html.I(className="fas fa-upload upload-icon"),
                    html.P("Drag and Drop or Click to Select a JSON File", className='upload-text'),
                    html.P("The file should be a JSON array of research paper objects.", className='upload-hint')
                ]),
                multiple=False # Allow only a single file to be uploaded
            ),
            html.Div(id='upload-status') # To show error messages
        ], id='upload-container'),

        # Main content (hidden until data is loaded)
        html.Div([
            # Progress and Stats
            html.Div([
                html.Div([
                    html.P("Total Papers"),
                    html.H3(id="total-counter")
                ], className="progress-stat"),
                html.Div([
                    html.P("Papers Kept"),
                    html.H3(id="kept-counter", children="0")
                ], className="progress-stat"),
                html.Div([
                    html.P("Papers Discarded"),
                    html.H3(id="discarded-counter", children="0")
                ], className="progress-stat"),
            ], className="progress-grid"),
            dbc.Progress(id="progress-bar", value=0, className="mb-4"),

            # Paper Display
            html.Div(id="paper-display", className="paper-card"),

            # Action Buttons
            html.Div([
                html.Button([html.I(className="fas fa-chevron-left me-2"), "Previous"],
                           id="prev-btn", className="btn-custom btn-nav", disabled=True),
                html.Button([html.I(className="fas fa-times me-2"), "Discard"],
                           id="discard-btn", className="btn-custom btn-discard"),
                html.Button([html.I(className="fas fa-check me-2"), "Keep"],
                           id="keep-btn", className="btn-custom btn-keep"),
                html.Button(["Next", html.I(className="fas fa-chevron-right ms-2")],
                           id="next-btn", className="btn-custom btn-nav")
            ], id="action-buttons-div", className="action-buttons"),

            # Export Section
            html.Div([
                html.Button([html.I(className="fas fa-download me-2"), "Export Decisions"],
                           id="export-btn", className="btn-export"),
                html.Div(id="export-status", className="mt-3")
            ], id='export-section-div', className="export-section"),

            # Hidden div to store current index
            html.Div(id="current-index", style={"display": "none"}, children=0)
        ], id='main-content', style={'display': 'none'}) # Starts hidden
        
    ], className="dhsc-container")
])

def parse_contents(contents, filename):
    """Parses the uploaded file content and returns the data."""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'json' in filename:
            # Assume a JSON file
            data = json.loads(decoded.decode('utf-8'))
            return data, None
        else:
            return None, dbc.Alert(f"Invalid file type for '{filename}'. Please upload a .json file.", color="danger")
    except Exception as e:
        print(e)
        return None, dbc.Alert(f"There was an error processing the file: {e}", color="danger")

# --- NEW CALLBACKS ---

# Callback to handle file upload and store data
@app.callback(
    Output('stored-data', 'data'),
    Output('decision-store', 'data'),
    Output('upload-status', 'children'),
    Output('current-index', 'children', allow_duplicate=True),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def handle_upload(contents, filename):
    if contents is not None:
        data, error_msg = parse_contents(contents, filename)
        if data is not None:
            # On successful upload, store data, reset decisions and index
            return data, {}, dbc.Alert(f"Successfully loaded {len(data)} papers from '{filename}'.", color="success"), 0
        else:
            # If parsing fails, show an error and don't change stored data
            return dash.no_update, dash.no_update, error_msg, dash.no_update
    return dash.no_update, dash.no_update, None, dash.no_update

# Callback to control UI visibility
@app.callback(
    Output('main-content', 'style'),
    Output('upload-container', 'style'),
    Output('total-counter', 'children'),
    Input('stored-data', 'data')
)
def toggle_main_content(data):
    if data:
        # If data exists, show main content and hide upload
        return {'display': 'block'}, {'display': 'none'}, str(len(data))
    else:
        # Otherwise, hide main content and show upload
        return {'display': 'none'}, {'display': 'block'}, '0'

# --- REFACTORED AND UPDATED CALLBACKS ---

# Callback to display current paper (UPDATED FOR NEW JSON STRUCTURE)
@app.callback(
    Output("paper-display", "children"),
    Output("current-index", "children"),
    Output("decision-store", "data", allow_duplicate=True), # Output to decision store
    Output("prev-btn", "disabled"),
    Output("next-btn", "disabled"),
    Output("action-buttons-div", "style"),
    Output("export-section-div", "style"),
    Input("current-index", "children"),
    Input("keep-btn", "n_clicks"),
    Input("discard-btn", "n_clicks"),
    Input("prev-btn", "n_clicks"),
    Input("next-btn", "n_clicks"),
    State('stored-data', 'data'),      # Get paper data from store
    State('decision-store', 'data'), # Get/update decision data from store
    prevent_initial_call=True
)
def update_paper_display(current_idx_str, keep_clicks, discard_clicks, prev_clicks, next_clicks, papers, decisions):
    if not papers:
        raise dash.exceptions.PreventUpdate

    current_index = int(current_idx_str)
    total_papers = len(papers)
    
    decisions = decisions or {}

    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'current-index'
    
    str_current_index = str(current_index)

    if triggered_id in ["keep-btn", "discard-btn"]:
        decision = 'keep' if triggered_id == "keep-btn" else 'discard'
        if current_index < total_papers:
            decisions[str_current_index] = decision
        if current_index < total_papers - 1:
            current_index += 1
        else:
            current_index += 1

    elif triggered_id == "prev-btn" and current_index > 0:
        current_index -= 1
    elif triggered_id == "next-btn" and current_index < total_papers:
        current_index += 1
    
    if current_index >= total_papers:
        kept_count = sum(1 for d in decisions.values() if d == 'keep')
        discarded_count = sum(1 for d in decisions.values() if d == 'discard')
        
        completion_content = html.Div([
            html.I(className="fas fa-check-circle completion-icon"),
            html.H2("All Papers Reviewed", className="mb-3"),
            html.P(f"You have reviewed all {total_papers} papers: {kept_count} kept, {discarded_count} discarded."),
            html.P("Click the export button to download your results.", className="text-muted")
        ], className="completion-screen")
        
        return completion_content, total_papers, decisions, True, True, {'display': 'none'}, {'display': 'block'}
    
    paper = papers[current_index]
    str_current_index = str(current_index)
    
    # --- Data Extraction Logic for New JSON Structure ---
    title = paper.get('title', 'No title')
    
    pub_info = paper.get('publication_info', {})
    
    authors_list = pub_info.get('authors')
    authors_str = ''
    if authors_list and isinstance(authors_list, list):
        author_names = [author.get('name') for author in authors_list if author.get('name')]
        if author_names:
            authors_str = ', '.join(author_names)

    if not authors_str:
        summary = pub_info.get('summary', '')
        if summary:
            # Heuristic: extract the part before the first ' - '
            authors_part = summary.split(' - ')[0]
            authors_str = authors_part.replace('…', '').strip()
        else:
            authors_str = 'No authors listed'
            
    summary_for_year = pub_info.get('summary', '')
    year_match = re.search(r'\b(19|20)\d{2}\b', summary_for_year)
    year = year_match.group(0) if year_match else 'N/A'
    
    abstract = paper.get('snippet', 'No snippet available')
    link = paper.get('link')
    source = extract_source(link)
    # --- End of Data Extraction Logic ---
    
    paper_content = [
        html.Div(f"Paper {current_index + 1} of {total_papers}", className="paper-number"),
        html.H2(title, className="paper-title"),
        html.Div([
            html.Div([html.Span("Authors", className="meta-label"), html.Span(authors_str, className="meta-value")], className="meta-item"),
            html.Div([html.Span("Year", className="meta-label"), html.Span(year, className="meta-value")], className="meta-item"),
            html.Div([html.Span("Source", className="meta-label"), html.Span(source, className="meta-value")], className="meta-item"),
        ], className="paper-meta"),
        html.Div([
            html.Span("Abstract", className="abstract-label"),
            html.P(abstract, className="abstract-text")
        ]),
    ]
    
    if link and link not in ['N/A', '#']:
        paper_content.append(html.A([html.I(className="fas fa-external-link-alt me-2"), "View Full Text"], href=link, target="_blank", className="btn btn-outline-secondary btn-sm mt-3"))
    
    if str_current_index in decisions:
        decision = decisions[str_current_index]
        badge_class = "badge-keep" if decision == 'keep' else "badge-discard"
        icon_class = "fas fa-check" if decision == 'keep' else "fas fa-times"
        paper_content.insert(0, html.Div([html.I(className=f"{icon_class} me-2"), f"Previously marked as: {decision.upper()}"], className=f"decision-badge {badge_class}"))
    
    paper_display = html.Div(paper_content)
    
    prev_disabled = current_index == 0
    next_disabled = current_index >= total_papers - 1

    return paper_display, current_index, decisions, prev_disabled, next_disabled, {'display': 'flex'}, {'display': 'block'}

# Callback to update counters and progress (now uses dcc.Store)
@app.callback(
    Output("kept-counter", "children"),
    Output("discarded-counter", "children"),
    Output("progress-bar", "value"),
    Input("decision-store", "data"), # Triggered by changes in decisions
    State("stored-data", "data")   # Gets total count from stored papers
)
def update_counters(decisions, papers):
    if not papers:
        return "0", "0", 0

    decisions = decisions or {}
    total_papers = len(papers)
    reviewed_count = len(decisions)
    
    kept = sum(1 for d in decisions.values() if d == 'keep')
    discarded = sum(1 for d in decisions.values() if d == 'discard')
    progress = (reviewed_count / total_papers) * 100 if total_papers > 0 else 0
    
    return str(kept), str(discarded), progress

# Callback to export decisions (UPDATED FOR NEW JSON STRUCTURE)
@app.callback(
    Output("export-status", "children"),
    Input("export-btn", "n_clicks"),
    State("decision-store", "data"),
    State("stored-data", "data"),
    prevent_initial_call=True
)
def export_decisions(n_clicks, decisions, papers):
    if n_clicks and decisions and papers:
        flat_export_data = []
        kept_papers_original = []
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for str_idx, decision in decisions.items():
            idx = int(str_idx)
            if idx < len(papers):
                paper = papers[idx]

                # --- Data Extraction for CSV ---
                pub_info = paper.get('publication_info', {})
                authors_list = pub_info.get('authors')
                authors_str = ''
                if authors_list and isinstance(authors_list, list):
                    author_names = [author.get('name') for author in authors_list if author.get('name')]
                    if author_names:
                        authors_str = ', '.join(author_names)
                if not authors_str:
                    summary = pub_info.get('summary', '')
                    authors_str = summary.split(' - ')[0].replace('…', '').strip() if summary else 'No authors listed'
                
                summary_for_year = pub_info.get('summary', '')
                year_match = re.search(r'\b(19|20)\d{2}\b', summary_for_year)
                year = year_match.group(0) if year_match else 'N/A'
                link = paper.get('link')
                
                flat_paper_data = {
                    'index': idx,
                    'decision': decision,
                    'title': paper.get('title', 'N/A'),
                    'authors': authors_str,
                    'year': year,
                    'source': extract_source(link),
                    'link': link or 'N/A',
                    'snippet': paper.get('snippet', 'N/A'),
                }
                flat_export_data.append(flat_paper_data)
                # --- End Data Extraction ---

                if decision == 'keep':
                    paper_copy = paper.copy()
                    paper_copy['decision'] = decision
                    kept_papers_original.append(paper_copy)

        # Export flattened data to CSV
        df = pd.DataFrame(flat_export_data)
        csv_filename = f"screening_decisions_{timestamp}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        # Export kept papers with original structure to JSON
        json_filename = f"kept_papers_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(kept_papers_original, f, indent=4)
            
        return dbc.Alert(f"Successfully exported to {csv_filename} and {json_filename}", color="success", dismissable=True, duration=5000)
    return ""

if __name__ == "__main__":
    app.run(debug=True)