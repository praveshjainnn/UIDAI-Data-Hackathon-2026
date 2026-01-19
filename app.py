import dash
from dash import dcc, html, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import io
import os

# === CONFIG ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], 
                title="MSME Analytics Dashboard", suppress_callback_exceptions=True)
server = app.server
WORK_DIR = r"c:\Users\PRAVESH\Desktop\UDHAI"

# State coordinates for mapping
STATE_COORDS = {
    'ANDHRA PRADESH': {'lat': 15.9129, 'lon': 79.7400},
    'ARUNACHAL PRADESH': {'lat': 28.2180, 'lon': 94.7278},
    'ASSAM': {'lat': 26.2006, 'lon': 92.9376},
    'BIHAR': {'lat': 25.0961, 'lon': 85.3131},
    'CHHATTISGARH': {'lat': 21.2787, 'lon': 81.8661},
    'GOA': {'lat': 15.2993, 'lon': 74.1240},
    'GUJARAT': {'lat': 22.2587, 'lon': 71.1924},
    'HARYANA': {'lat': 29.0588, 'lon': 76.0856},
    'HIMACHAL PRADESH': {'lat': 31.1048, 'lon': 77.1734},
    'JHARKHAND': {'lat': 23.6102, 'lon': 85.2799},
    'KARNATAKA': {'lat': 15.3173, 'lon': 75.7139},
    'KERALA': {'lat': 10.8505, 'lon': 76.2711},
    'MADHYA PRADESH': {'lat': 22.9734, 'lon': 78.6569},
    'MAHARASHTRA': {'lat': 19.7515, 'lon': 75.7139},
    'MANIPUR': {'lat': 24.6637, 'lon': 93.9063},
    'MEGHALAYA': {'lat': 25.4670, 'lon': 91.3662},
    'MIZORAM': {'lat': 23.1645, 'lon': 92.9376},
    'NAGALAND': {'lat': 26.1584, 'lon': 94.5624},
    'ODISHA': {'lat': 20.9517, 'lon': 85.0985},
    'PUNJAB': {'lat': 31.1471, 'lon': 75.3412},
    'RAJASTHAN': {'lat': 27.0238, 'lon': 74.2179},
    'SIKKIM': {'lat': 27.5330, 'lon': 88.5122},
    'TAMIL NADU': {'lat': 11.1271, 'lon': 78.6569},
    'TELANGANA': {'lat': 18.1124, 'lon': 79.0193},
    'TRIPURA': {'lat': 23.9408, 'lon': 91.9882},
    'UTTAR PRADESH': {'lat': 26.8467, 'lon': 80.9462},
    'UTTARAKHAND': {'lat': 30.0668, 'lon': 79.0193},
    'WEST BENGAL': {'lat': 22.9868, 'lon': 87.8550},
    'DELHI': {'lat': 28.7041, 'lon': 77.1025},
    'CHANDIGARH': {'lat': 30.7333, 'lon': 76.7794},
    'PUDUCHERRY': {'lat': 11.9416, 'lon': 79.8083},
    'LAKSHADWEEP': {'lat': 10.5669, 'lon': 72.6417},
    'JAMMU AND KASHMIR': {'lat': 33.7782, 'lon': 76.5762},
    'DAMAN AND DIU': {'lat': 20.4283, 'lon': 72.8397},
    'DADAR AND NAGAR HAVELI': {'lat': 20.1809, 'lon': 73.0169}
}

# === LOAD DATA ===
def load_csv(filename):
    path = os.path.join(WORK_DIR, filename)
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return pd.DataFrame()

# NIC Sector Mapping (5-digit code ranges to broad sectors)
NIC_SECTOR_MAP = {
    'Manufacturing': range(10000, 34000),
    'Textiles & Apparel': range(13000, 15000),
    'Food Processing': range(10000, 11000),
    'Chemicals': range(20000, 21000),
    'Metal & Machinery': range(24000, 29000),
    'Construction': range(41000, 44000),
    'Trade & Retail': range(45000, 48000),
    'Transportation': range(49000, 54000),
    'Hotels & Restaurants': range(55000, 57000),
    'IT & Services': range(58000, 64000),
    'Professional Services': range(69000, 75000),
    'Other Services': range(77000, 97000)
}

def get_nic_sector(nic_code):
    """Map a 5-digit NIC code to its broad sector"""
    try:
        code = int(str(nic_code)[:5])
        for sector, code_range in NIC_SECTOR_MAP.items():
            if code in code_range:
                return sector
        return 'Other'
    except:
        return 'Other'

print("Loading MSME data...", flush=True)
df_loc = load_csv("location_profile.csv")
df_soc = load_csv("social_profile.csv")
df_emp = load_csv("employment_profile.csv")
df_ind = load_csv("industry_profile.csv")
df_score = load_csv("composite_score.csv")
df_master = load_csv("msme_merged.csv")  # Master file for detailed NIC analysis
print(f"Data loaded: {len(df_loc)} locations, {len(df_master)} master records", flush=True)

# === HELPER ===
def filter_df(df, state, district):
    if df.empty:
        return df
    dff = df.copy()
    if state and 'State' in dff.columns:
        dff = dff[dff['State'] == state]
    if district and 'District' in dff.columns:
        dff = dff[dff['District'] == district]
    return dff

def create_india_map(df_state, color_col, scale='Viridis', title='', size_col=None):
    """Create bubble map of India using state coordinates"""
    if df_state.empty:
        return go.Figure()
    
    # Add coordinates
    df_map = df_state.copy()
    df_map['lat'] = df_map['State'].map(lambda x: STATE_COORDS.get(x, {}).get('lat', 22))
    df_map['lon'] = df_map['State'].map(lambda x: STATE_COORDS.get(x, {}).get('lon', 78))
    
    # Create figure
    if size_col and size_col in df_map.columns:
        fig = px.scatter_mapbox(
            df_map,
            lat='lat', lon='lon',
            color=color_col,
            size=size_col,
            hover_name='State',
            hover_data=[color_col],
            color_continuous_scale=scale,
            size_max=25,  # Reduced from 40 to make dots smaller
            zoom=4.2,
            center={"lat": 22, "lon": 78},
            title=title
        )
    else:
        fig = px.scatter_mapbox(
            df_map,
            lat='lat', lon='lon',
            color=color_col,
            hover_name='State',
            hover_data=[color_col],
            color_continuous_scale=scale,
            size=[12]*len(df_map),  # Reduced from 30 to make dots smaller
            zoom=4.2,
            center={"lat": 22, "lon": 78},
            title=title
        )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":30,"l":0,"b":0},
        height=850,
        dragmode=False  # Disable rotation/dragging
    )
    fig.update_mapboxes(
        bearing=0,  # Lock orientation
        pitch=0     # Lock tilt
    )
    return fig

# === LAYOUTS ===
def create_header():
    return html.Div([
        html.Div([
            html.Div([
                html.Img(src="/assets/emblem.jpg", 
                        height="70px", 
                        className="me-3"),
                html.Div([
                    html.P("", 
                          style={'fontSize': '0.7rem', 'color': '#666', 'textAlign': 'center', 
                                 'marginTop': '-5px', 'marginBottom': '0', 'fontWeight': 'bold'})
                ])
            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
            html.Div([
                html.H3("National MSME Analytics Portal", className="header-title"),
                html.P("Geospatial Implementation of MSME Manual", className="header-subtitle")
            ])
        ], className="d-flex align-items-center"),
        html.Div([
            dbc.Button("Dashboard", id="btn-dashboard", color="danger", className="me-2", n_clicks=0),
            dbc.Button("DSS Tools", id="btn-dss", color="warning", className="me-2", n_clicks=0),
            dbc.Button("Data Upload", id="btn-upload", color="primary", n_clicks=0)
        ])
    ], className="header-container")

def create_dashboard_layout():
    return html.Div([
        html.Div([
            html.Label("Profile View:", className="nav-label"),
            dcc.Dropdown(id='tab-selector', value='tab1', clearable=False, style={'width': '250px'}, className="me-3",
                options=[
                    {'label': '1. Location & Infrastructure', 'value': 'tab1'},
                    {'label': '2. Social Inclusion', 'value': 'tab2'},
                    {'label': '3. Employment & Scale', 'value': 'tab3'},
                    {'label': '4. Industry Profile', 'value': 'tab4'},
                    {'label': '5. Development Score', 'value': 'tab5'}
                ]),
            html.Label("State:", className="nav-label"),
            dcc.Dropdown(id='state-selector', placeholder="All States", style={'width': '200px'}, className="me-3"),
            html.Label("District:", className="nav-label"),
            dcc.Dropdown(id='district-selector', placeholder="All Districts", style={'width': '200px'})
        ], className="nav-bar"),
        
        dbc.Container([
            dcc.Loading(id="loading", type="circle", children=[
                html.Br(),
                dbc.Row(id='kpi-row', className="mb-3"),
                
                # Insights Section
                dbc.Row([
                    dbc.Col([
                        html.Div(id='insights-section', className="mb-3")
                    ], width=12)
                ]),
                
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5("Geospatial View - India Map", className="section-title"),
                            html.P(id='map-description', className="text-muted", style={'fontSize': '0.9rem', 'marginBottom': '10px'}),
                            dcc.Graph(id='main-map', config={'scrollZoom': False, 'displayModeBar': False}, style={'height': '750px'})
                        ], className="section-card")
                    ], width=8),
                    dbc.Col([
                        html.Div([
                            html.H5(id="chart-header", className="section-title"),
                            dcc.Graph(id='chart-1', style={'height': '400px'}),
                            html.Hr(),
                            dcc.Graph(id='chart-2', style={'height': '400px'}),
                            html.Div(id='chart-3-container', children=[
                                html.Hr(),
                                dcc.Graph(id='chart-3', style={'height': '400px'})
                            ], style={'display': 'none'})
                        ], className="section-card")
                    ], width=4)
                ])
            ])
        ], fluid=True, className="p-4")
    ])

def create_dss_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("State", className="dss-control-label"),
                    dcc.Dropdown(id='dss-state-selector', placeholder="All India", className="mb-2"),
                    
                    html.Label("Highlight On Map", className="dss-control-label"),
                    dcc.Dropdown(
                        id='dss-highlight-selector',
                        options=[
                            {'label': 'None', 'value': 'none'},
                            {'label': '🔴 High MSME Density', 'value': 'high_density'},
                            {'label': '🟠 Low Female Ownership', 'value': 'low_female'},
                            {'label': '🟢 High Employment', 'value': 'high_employment'}
                        ],
                        value='none',
                        className="mb-3"
                    ),
                    
                    html.Div("Decision Insights", className="dss-section-header"),
                    html.Div(id='dss-insights', style={'fontSize': '0.9rem', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'minHeight': '60px'}),
                    
                    html.Hr(style={'margin': '20px 0'}),
                    
                    html.H5("Top Districts", className="section-title", style={'fontSize': '1rem', 'marginTop': '15px'}),
                    html.Div(id="dss-data-table", style={'maxHeight': '400px', 'overflowY': 'auto'})
                ], className="dss-sidebar", style={'height': '88vh', 'overflowY': 'auto'})
            ], width=3, style={'padding': '0'}),
            
            dbc.Col([
                dcc.Loading(
                    dcc.Graph(id='dss-main-map', style={'height': '88vh', 'width': '100%'}, config={'scrollZoom': False, 'displayModeBar': False, 'doubleClick': False})
                )
            ], width=9, style={'padding': '0'})
        ], className="g-0")
    ], fluid=True)

def create_upload_layout():
    return dbc.Container([
        html.Br(),
        html.H2("Data Upload Portal", className="text-center mb-4"),
        dbc.Card([
            dbc.CardBody([
                html.H5("Upload CSV File", className="card-title"),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files', style={'color': '#007bff', 'cursor': 'pointer'})
                    ]),
                    style={
                        'width': '100%', 'height': '80px', 'lineHeight': '80px',
                        'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '8px',
                        'textAlign': 'center', 'margin': '10px', 'cursor': 'pointer'
                    },
                    multiple=False
                ),
                html.Div(id='upload-output', className='mt-3')
            ])
        ], className="p-4", style={'maxWidth': '700px', 'margin': 'auto'})
    ], fluid=True)

# === MAIN LAYOUT ===
app.layout = html.Div([
    dcc.Store(id='page-mode', data='dashboard'),
    create_header(),
    html.Div(id='page-content')
])

# === CALLBACKS ===

@app.callback(Output('page-mode', 'data'),
              [Input('btn-dashboard', 'n_clicks'), Input('btn-dss', 'n_clicks'), Input('btn-upload', 'n_clicks')],
              State('page-mode', 'data'))
def toggle_mode(btn1, btn2, btn3, current):
    cid = ctx.triggered_id
    if cid == 'btn-dss': return 'dss'
    if cid == 'btn-upload': return 'upload'
    return 'dashboard'

@app.callback(Output('page-content', 'children'), Input('page-mode', 'data'))
def render_page(mode):
    if mode == 'dss': return create_dss_layout()
    if mode == 'upload': return create_upload_layout()
    return create_dashboard_layout()

@app.callback(Output('state-selector', 'options'), Input('page-mode', 'data'))
def populate_state_dropdown(mode):
    if df_loc.empty: return []
    return [{'label': s, 'value': s} for s in sorted(df_loc['State'].dropna().unique())]

@app.callback(Output('dss-state-selector', 'options'), Input('page-mode', 'data'))
def populate_dss_state(mode):
    if df_loc.empty: return []
    return [{'label': s, 'value': s} for s in sorted(df_loc['State'].dropna().unique())]

@app.callback(Output('district-selector', 'options'), Input('state-selector', 'value'))
def update_districts(state):
    if not state or df_loc.empty: return []
    dists = df_loc[df_loc['State'] == state]['District'].dropna().unique()
    return [{'label': d, 'value': d} for d in sorted(dists)]

# Dashboard Main
@app.callback(
    [Output('kpi-row', 'children'), Output('main-map', 'figure'), Output('chart-1', 'figure'), 
     Output('chart-2', 'figure'), Output('chart-header', 'children'),
     Output('chart-3', 'figure'), Output('chart-3-container', 'style'),
     Output('insights-section', 'children'), Output('map-description', 'children')],
    [Input('tab-selector', 'value'), Input('state-selector', 'value'), Input('district-selector', 'value')]
)
def update_dashboard(tab, state, district):
    map_fig = go.Figure()
    chart1 = go.Figure()
    chart2 = go.Figure()
    chart3 = go.Figure()
    kpis = []
    header = "Analytics"
    show_chart3 = {'display': 'none'}
    insights = html.Div()
    map_desc = ""
    
    try:
        if tab == 'tab1':
            dff = filter_df(df_loc, state, district)
            header ="Location Distribution"
            map_desc = "Bubble size represents MSME density. Darker colors indicate higher concentration of enterprises."
            
            if not dff.empty:
                state_agg = dff.groupby('State', as_index=False).agg({'msme_count': 'sum'})
                map_fig = create_india_map(state_agg, 'msme_count', 'Viridis', 'MSME Density', 'msme_count')
                
                # Generate insights
                top_state = state_agg.loc[state_agg['msme_count'].idxmax()]
                total_msmes = dff['msme_count'].sum()
                top_3_states = state_agg.nlargest(3, 'msme_count')
                top_3_contribution = (top_3_states['msme_count'].sum() / total_msmes * 100)
                
                insights = dbc.Alert([
                    html.Div([
                        html.I(className="fas fa-lightbulb me-2"),
                        html.Strong("📊 Key Insights:"),
                    ], className="mb-2"),
                    html.Ul([
                        html.Li(f"🥇 {top_state['State']} leads with {top_state['msme_count']:,} MSMEs"),
                        html.Li(f"📈 Top 3 states account for {top_3_contribution:.1f}% of total enterprises"),
                        html.Li(f"🏢 Total {dff['District'].nunique()} districts have registered MSMEs"),
                    ], style={'marginBottom': '0'})
                ], color="info", className="mb-3")
                
                kpis = [
                    dbc.Col(html.Div([html.Div(f"{dff['msme_count'].sum():,}", className="kpi-value"), 
                                      html.Div("Total MSMEs", className="kpi-label")], className="kpi-card bg-grey"), width=3),
                    dbc.Col(html.Div([html.Div(dff['District'].nunique(), className="kpi-value"), 
                                      html.Div("Districts", className="kpi-label")], className="kpi-card bg-blue"), width=3)
                ]
                
                top10 = dff.groupby('District')['msme_count'].sum().nlargest(10).reset_index()
                chart1 = px.bar(top10, x='District', y='msme_count', title="Top 10 Districts by MSME Count")
                chart1.update_layout(height=320)
                
                if state:
                    chart2 = px.pie(dff, names='Dic_Name', values='msme_count', title="DIC Distribution", hole=0.4)
                else:
                    top_states = state_agg.nlargest(10, 'msme_count')
                    chart2 = px.bar(top_states, x='State', y='msme_count', title="Top 10 States by MSME Count", color='msme_count')
                chart2.update_layout(height=320)
        
        elif tab == 'tab2':
            dff = filter_df(df_soc, state, district)
            header = "Social Inclusion"
            map_desc = "Map shows female ownership percentage. Larger bubbles indicate more enterprises."
            
            if not dff.empty:
                state_agg = dff.groupby('State', as_index=False).agg({
                    'female_owned': 'sum', 'total_msmes': 'sum', 'sc_count': 'sum', 'st_count': 'sum'
                })
                state_agg['women_pct'] = (state_agg['female_owned'] / state_agg['total_msmes'] * 100).fillna(0)
                map_fig = create_india_map(state_agg, 'women_pct', 'RdPu', 'Female Ownership %', 'total_msmes')
                
                # Generate insights
                female_total = dff['female_owned'].sum()
                male_total = dff['male_owned'].sum()
                total_all = female_total + male_total
                women_pct = (female_total / total_all * 100) if total_all > 0 else 0
                top_women_state = state_agg.loc[state_agg['women_pct'].idxmax()]
                
                sc_st_total = dff['sc_count'].sum() + dff['st_count'].sum()
                sc_st_pct = (sc_st_total / dff['total_msmes'].sum() * 100) if dff['total_msmes'].sum() > 0 else 0
                
                insights = dbc.Alert([
                    html.Div([
                        html.I(className="fas fa-users me-2"),
                        html.Strong("🌟 Inclusion Insights:"),
                    ], className="mb-2"),
                    html.Ul([
                        html.Li(f"👩‍💼 Women own {women_pct:.1f}% of MSMEs ({female_total:,} enterprises)"),
                        html.Li(f"🏆 {top_women_state['State']} leads in women entrepreneurship ({top_women_state['women_pct']:.1f}%)"),
                        html.Li(f"🤝 SC/ST entrepreneurs represent {sc_st_pct:.1f}% of total MSMEs"),
                    ], style={'marginBottom': '0'})
                ], color="success", className="mb-3")
                
                kpis = [
                    dbc.Col(html.Div([html.Div(f"{dff['female_owned'].sum():,}", className="kpi-value"), 
                                      html.Div("Women Owned", className="kpi-label")], className="kpi-card bg-red"), width=3),
                    dbc.Col(html.Div([html.Div(f"{dff['male_owned'].sum():,}", className="kpi-value"), 
                                      html.Div("Men Owned", className="kpi-label")], className="kpi-card bg-yellow"), width=3)
                ]
                
                # CHART 1: Social Category Distribution as DONUT CHART
                cats_data = pd.DataFrame({
                    'Category': ['General', 'OBC', 'SC', 'ST'], 
                    'Count': [dff['general_count'].sum(), dff['obc_count'].sum(), dff['sc_count'].sum(), dff['st_count'].sum()]
                })
                
                chart1 = px.pie(
                    cats_data, 
                    names='Category', 
                    values='Count', 
                    hole=0.4,  # Donut chart
                    title="Social Category Distribution",
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#95E1D3', '#FFE66D']  # Vibrant colors
                )
                chart1.update_traces(textposition='inside', textinfo='percent+label')
                chart1.update_layout(height=400)
                
                # CHART 2: Gender Distribution as PIE CHART with OUTSIDE percentages
                genders_data = pd.DataFrame({
                    'Gender': ['Male', 'Female'], 
                    'Count': [dff['male_owned'].sum(), dff['female_owned'].sum()]
                })
                chart2 = px.pie(
                    genders_data, 
                    names='Gender', 
                    values='Count', 
                    title="Gender Distribution",
                    color_discrete_map={'Male': '#3498db', 'Female': '#e74c3c'}  # Blue for Male, Red for Female
                )
                chart2.update_traces(
                    textposition='outside',  # Percentages OUTSIDE
                    textinfo='percent+label',
                    textfont_size=13,
                    pull=[0.05, 0.05]  # Slightly pull slices apart for clarity
                )
                chart2.update_layout(height=350)
        
        elif tab == 'tab3':
            dff = filter_df(df_emp, state, district)
            header = "Employment & Investment"
            map_desc = "Bubble size shows total employment. Color intensity indicates employment levels across states."
            
            if not dff.empty:
                state_agg = dff.groupby('State', as_index=False).agg({'total_employment': 'sum', 'total_msmes': 'sum'})
                map_fig = create_india_map(state_agg, 'total_employment', 'Plasma', 'Employment', 'total_employment')
                
                # Enhanced KPIs
                total_investment = dff['total_investment'].sum()
                total_employment = dff['total_employment'].sum()
                avg_investment_per_job = total_investment / total_employment if total_employment > 0 else 0
                
                # Generate insights
                top_employer = dff.loc[dff['total_employment'].idxmax()]
                avg_emp_per_msme = total_employment / dff['total_msmes'].sum() if dff['total_msmes'].sum() > 0 else 0
                
                insights = dbc.Alert([
                    html.Div([
                        html.I(className="fas fa-briefcase me-2"),
                        html.Strong("💼 Employment Insights:"),
                    ], className="mb-2"),
                    html.Ul([
                        html.Li(f"👥 Total {total_employment:,} jobs created across {dff['total_msmes'].sum():,} MSMEs"),
                        html.Li(f"📊 Average {avg_emp_per_msme:.1f} employees per enterprise"),
                        html.Li(f"💰 Investment efficiency: ₹{avg_investment_per_job:.1f}L per job created"),
                    ], style={'marginBottom': '0'})
                ], color="warning", className="mb-3")
                
                kpis = [
                    dbc.Col(html.Div([html.Div(f"{total_employment:,}", className="kpi-value"), 
                                      html.Div("Total Jobs", className="kpi-label")], className="kpi-card bg-blue"), width=3),
                    dbc.Col(html.Div([html.Div(f"₹{total_investment:,.0f}L", className="kpi-value"), 
                                      html.Div("Total Investment", className="kpi-label")], className="kpi-card bg-green"), width=3),
                    dbc.Col(html.Div([html.Div(f"₹{avg_investment_per_job:.1f}L", className="kpi-value"), 
                                      html.Div("Investment per Job", className="kpi-label")], className="kpi-card bg-red"), width=3)
                ]
                
                # CHART 1: Enterprise Type Distribution with Employment
                # Parse enterprise_type_split to extract counts
                def parse_enterprise_types(df):
                    enterprise_data = {'Micro': 0, 'Small': 0, 'Medium': 0}
                    employment_data = {'Micro': 0, 'Small': 0, 'Medium': 0}
                    
                    for idx, row in df.iterrows():
                        split_str = str(row.get('enterprise_type_split', ''))
                        emp = row.get('total_employment', 0)
                        msmes = row.get('total_msmes', 1)
                        avg_emp_per_msme = emp / msmes if msmes > 0 else 0
                        
                        # Parse "Micro: 5 | Small: 2 | Medium: 1" format
                        for part in split_str.split('|'):
                            part = part.strip()
                            if 'Micro:' in part:
                                count = int(part.split(':')[1].strip())
                                enterprise_data['Micro'] += count
                                employment_data['Micro'] += count * avg_emp_per_msme
                            elif 'Small:' in part:
                                count = int(part.split(':')[1].strip())
                                enterprise_data['Small'] += count
                                employment_data['Small'] += count * avg_emp_per_msme
                            elif 'Medium:' in part:
                                count = int(part.split(':')[1].strip())
                                enterprise_data['Medium'] += count
                                employment_data['Medium'] += count * avg_emp_per_msme
                    
                    return pd.DataFrame({
                        'Enterprise Type': list(enterprise_data.keys()),
                        'Count': list(enterprise_data.values()),
                        'Employment': list(employment_data.values())
                    })
                
                enterprise_df = parse_enterprise_types(dff)
                enterprise_df['Avg Employment'] = enterprise_df['Employment'] / enterprise_df['Count']
                enterprise_df['Avg Employment'] = enterprise_df['Avg Employment'].fillna(0)
                
                chart1 = px.bar(
                    enterprise_df,
                    x='Enterprise Type',
                    y='Employment',
                    title="Employment by Enterprise Type",
                    color='Enterprise Type',
                    text='Employment',
                    color_discrete_map={'Micro': '#3498db', 'Small': '#e67e22', 'Medium': '#e74c3c'}
                )
                chart1.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                chart1.update_layout(height=400, showlegend=False)
                
                # CHART 2: Investment Efficiency - Top Districts
                dff_efficiency = dff.copy()
                dff_efficiency['employment_per_investment'] = (
                    dff_efficiency['total_employment'] / dff_efficiency['total_investment']
                ).replace([float('inf'), -float('inf')], 0).fillna(0)
                
                # Filter out zeros and get top performers
                dff_efficiency = dff_efficiency[dff_efficiency['employment_per_investment'] > 0]
                top_efficient = dff_efficiency.nlargest(15, 'employment_per_investment')
                
                if len(top_efficient) > 0:
                    chart2 = px.bar(
                        top_efficient,
                        y='District' if not state else 'State',
                        x='employment_per_investment',
                        orientation='h',
                        title="Top 15: Employment per ₹Lakh Investment",
                        color='employment_per_investment',
                        color_continuous_scale='Viridis',
                        hover_data=['total_employment', 'total_investment']
                    )
                    chart2.update_layout(
                        height=400,
                        xaxis_title="Jobs per ₹L",
                        yaxis_title="",
                        showlegend=False
                    )
                else:
                    chart2 = go.Figure()
                    chart2.update_layout(height=400, title="No data available")
                
                # CHART 3: Top Employment Generators
                top_employers = dff.nlargest(15, 'total_employment')
                
                chart3 = px.bar(
                    top_employers,
                    x='District' if 'District' in top_employers.columns else 'State',
                    y='total_employment',
                    title="Top 15 Employment Generators",
                    color='total_investment',
                    color_continuous_scale='Blues',
                    hover_data=['total_msmes', 'avg_employment']
                )
                chart3.update_layout(
                    height=400,
                    xaxis_tickangle=-45,
                    xaxis_title="",
                    yaxis_title="Total Employment"
                )
                
                # Show Chart 3
                show_chart3 = {'display': 'block'}
        
        elif tab == 'tab4':
            dff = filter_df(df_ind, state, district)
            header = "Industry Profile"
            if not dff.empty:
                # Aggregate by state for map visualization
                state_agg = dff.groupby('State', as_index=False).agg({
                    'manufacturing_pct': 'mean',
                    'services_pct': 'mean',
                    'industry_diversity_index': 'mean'
                })
                
                # Create map showing BOTH manufacturing and services percentages
                # Add both metrics to the dataframe for hover display
                state_agg_map = state_agg.copy()
                
                # Create custom map with both metrics visible
                df_map = state_agg_map.copy()
                df_map['lat'] = df_map['State'].map(lambda x: STATE_COORDS.get(x, {}).get('lat', 22))
                df_map['lon'] = df_map['State'].map(lambda x: STATE_COORDS.get(x, {}).get('lon', 78))
                
                # Create scatter mapbox with both manufacturing and services in hover
                map_fig = px.scatter_mapbox(
                    df_map,
                    lat='lat', 
                    lon='lon',
                    color='manufacturing_pct',
                    hover_name='State',
                    hover_data={
                        'manufacturing_pct': ':.1f',
                        'services_pct': ':.1f',
                        'lat': False,
                        'lon': False
                    },
                    color_continuous_scale='RdYlGn_r',  # Red for high manufacturing, Green for high services
                    size=[12]*len(df_map),
                    zoom=3.8,
                    center={"lat": 22, "lon": 78},
                    title='Manufacturing vs Services %',
                    labels={
                        'manufacturing_pct': 'Manufacturing %',
                        'services_pct': 'Services %'
                    }
                )
                
                map_fig.update_layout(
                    mapbox_style="open-street-map",
                    margin={"r":0,"t":30,"l":0,"b":0},
                    height=650,
                    dragmode=False
                )
                map_fig.update_mapboxes(bearing=0, pitch=0)
                
                kpis = [
                    dbc.Col(html.Div([html.Div(f"{dff['manufacturing_pct'].mean():.1f}%", className="kpi-value"), 
                                      html.Div("Avg Manufacturing", className="kpi-label")], className="kpi-card bg-red"), width=3),
                    dbc.Col(html.Div([html.Div(f"{dff['services_pct'].mean():.1f}%", className="kpi-value"), 
                                      html.Div("Avg Services", className="kpi-label")], className="kpi-card bg-blue"), width=3),
                    dbc.Col(html.Div([html.Div(f"{dff['industry_diversity_index'].mean():.1f}", className="kpi-value"), 
                                      html.Div("Avg Diversity Index", className="kpi-label")], className="kpi-card bg-green"), width=3)
                ]
                
                # CHART 1: Manufacturing vs Services Bar Chart
                if state:
                    # If state is selected, show district-level data
                    mfg_vs_svc = dff.head(15).copy()
                    mfg_vs_svc = mfg_vs_svc.melt(
                        id_vars=['District'], 
                        value_vars=['manufacturing_pct', 'services_pct'],
                        var_name='Sector', 
                        value_name='Percentage'
                    )
                    mfg_vs_svc['Sector'] = mfg_vs_svc['Sector'].map({
                        'manufacturing_pct': 'Manufacturing',
                        'services_pct': 'Services'
                    })
                    chart1 = px.bar(
                        mfg_vs_svc, 
                        x='District', 
                        y='Percentage', 
                        color='Sector',
                        title="Manufacturing vs Services by District",
                        barmode='group',
                        color_discrete_map={'Manufacturing': '#FF6B35', 'Services': '#004E89'}
                    )
                    chart1.update_layout(height=400, xaxis_tickangle=-45)
                else:
                    # Show state-level aggregation
                    top_states = state_agg.nlargest(15, 'manufacturing_pct')
                    mfg_vs_svc = top_states.melt(
                        id_vars=['State'], 
                        value_vars=['manufacturing_pct', 'services_pct'],
                        var_name='Sector', 
                        value_name='Percentage'
                    )
                    mfg_vs_svc['Sector'] = mfg_vs_svc['Sector'].map({
                        'manufacturing_pct': 'Manufacturing',
                        'services_pct': 'Services'
                    })
                    chart1 = px.bar(
                        mfg_vs_svc, 
                        x='State', 
                        y='Percentage', 
                        color='Sector',
                        title="Manufacturing vs Services by State (Top 15)",
                        barmode='group',
                        color_discrete_map={'Manufacturing': '#FF6B35', 'Services': '#004E89'}
                    )
                    chart1.update_layout(height=400, xaxis_tickangle=-45)
                
                # CHART 2: Industry Diversity Index
                if state:
                    diversity_data = dff.sort_values('industry_diversity_index', ascending=False).head(15)
                    chart2 = px.bar(
                        diversity_data,
                        x='District',
                        y='industry_diversity_index',
                        title="Industry Diversity Index by District",
                        color='industry_diversity_index',
                        color_continuous_scale='Viridis'
                    )
                    chart2.update_layout(height=400, xaxis_tickangle=-45)
                else:
                    diversity_state = state_agg.sort_values('industry_diversity_index', ascending=False).head(15)
                    chart2 = px.bar(
                        diversity_state,
                        x='State',
                        y='industry_diversity_index',
                        title="Industry Diversity Index by State (Top 15)",
                        color='industry_diversity_index',
                        color_continuous_scale='Viridis'
                    )
                    chart2.update_layout(height=400, xaxis_tickangle=-45)
                
                # No Chart 3 - keeping single map only
                show_chart3 = {'display': 'none'}
        
        elif tab == 'tab5':
            dff = filter_df(df_score, state, None)
            header = "Development Scorecard"
            map_desc = "Color coding shows MSME development score (Red: Low, Yellow: Medium, Green: High)."
            
            if not dff.empty:
                map_fig = create_india_map(dff, 'Final_MSME_Score', 'RdYlGn', 'MSME Score')
                
                # Enhanced KPIs
                avg_score = dff['Final_MSME_Score'].mean()
                top_state = dff.loc[dff['Final_MSME_Score'].idxmax(), 'State']
                top_score = dff['Final_MSME_Score'].max()
                category_counts = dff['Category'].value_counts()
                
                # Generate insights
                advanced_count = category_counts.get('Advanced', 0)
                developing_count = category_counts.get('Developing', 0)
                nascent_count = category_counts.get('Nascent', 0)
                
                insights = dbc.Alert([
                    html.Div([
                        html.I(className="fas fa-chart-line me-2"),
                        html.Strong("🎯 Development Insights:"),
                    ], className="mb-2"),
                    html.Ul([
                        html.Li(f"🏆 {top_state} ranks #1 with {top_score:.1f} score (Advanced category)"),
                        html.Li(f"📈 {developing_count} states in 'Developing' stage, {nascent_count} need urgent focus"),
                        html.Li(f"⚖️ National average MSME development score: {avg_score:.1f}/100"),
                    ], style={'marginBottom': '0'})
                ], color="primary", className="mb-3")
                
                kpis = [
                    dbc.Col(html.Div([html.Div(f"{avg_score:.1f}", className="kpi-value"), 
                                      html.Div("Avg MSME Score", className="kpi-label")], className="kpi-card bg-blue"), width=3),
                    dbc.Col(html.Div([html.Div(top_state[:15], className="kpi-value", style={'fontSize': '1.2rem'}), 
                                      html.Div("Top Performer", className="kpi-label")], className="kpi-card bg-green"), width=3),
                    dbc.Col(html.Div([html.Div(str(len(dff)), className="kpi-value"), 
                                      html.Div("States/UTs", className="kpi-label")], className="kpi-card bg-red"), width=3)
                ]
                
                # CHART 1: Enhanced State Rankings (Top 20 only for better readability)
                top_states = dff.nlargest(20, 'Final_MSME_Score')
                
                chart1 = px.bar(
                    top_states.sort_values('Final_MSME_Score'),
                    x='Final_MSME_Score',
                    y='State',
                    orientation='h',
                    color='Category',
                    title="Top 20 State Rankings by MSME Score",
                    color_discrete_map={
                        'Nascent': '#e74c3c',      # Red
                        'Emerging': '#f39c12',     # Orange
                        'Developing': '#3498db',   # Blue
                        'Advanced': '#27ae60'      # Green
                    },
                    hover_data=['Scale_Score', 'Social_Score', 'Employment_Score', 'Industry_Score']
                )
                chart1.update_layout(
                    height=400,
                    xaxis_title="Final MSME Score",
                    yaxis_title="",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                # CHART 2: Radar Chart for Top 5 States showing all 4 dimensions
                top5_states = dff.nlargest(5, 'Final_MSME_Score')
                
                chart2 = go.Figure()
                
                categories_radar = ['Scale Score', 'Social Score', 'Employment Score', 'Industry Score']
                
                colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
                
                for idx, (_, row) in enumerate(top5_states.iterrows()):
                    values = [
                        row['Scale_Score'],
                        row['Social_Score'],
                        row['Employment_Score'],
                        row['Industry_Score']
                    ]
                    # Close the radar chart by adding first value at end
                    values_closed = values + [values[0]]
                    categories_closed = categories_radar + [categories_radar[0]]
                    
                    chart2.add_trace(go.Scatterpolar(
                        r=values_closed,
                        theta=categories_closed,
                        fill='toself',
                        name=row['State'][:15],  # Truncate long names
                        line_color=colors[idx % len(colors)]
                    ))
                
                chart2.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=True,
                    title="Top 5 States: Multi-Dimensional Score Analysis",
                    height=400,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                
                # CHART 3: Category Distribution with Score Breakdown
                category_stats = dff.groupby('Category').agg({
                    'Final_MSME_Score': 'mean',
                    'State': 'count'
                }).reset_index()
                category_stats.columns = ['Category', 'Avg_Score', 'Count']
                
                # Sort by category order
                category_order = ['Nascent', 'Emerging', 'Developing', 'Advanced']
                category_stats['Category'] = pd.Categorical(
                    category_stats['Category'], 
                    categories=category_order, 
                    ordered=True
                )
                category_stats = category_stats.sort_values('Category')
                
                chart3 = go.Figure()
                
                # Add bar for count
                chart3.add_trace(go.Bar(
                    x=category_stats['Category'],
                    y=category_stats['Count'],
                    name='Number of States',
                    marker_color=['#e74c3c', '#f39c12', '#3498db', '#27ae60'],
                    text=category_stats['Count'],
                    textposition='outside',
                    yaxis='y'
                ))
                
                # Add line for average score
                chart3.add_trace(go.Scatter(
                    x=category_stats['Category'],
                    y=category_stats['Avg_Score'],
                    name='Avg MSME Score',
                    mode='lines+markers+text',
                    marker=dict(size=10, color='#34495e'),
                    line=dict(width=3, color='#34495e'),
                    text=[f"{score:.1f}" for score in category_stats['Avg_Score']],
                    textposition='top center',
                    yaxis='y2'
                ))
                
                chart3.update_layout(
                    title="Category Distribution & Average Scores",
                    xaxis_title="Development Category",
                    yaxis=dict(
                        title="Number of States",
                        side='left'
                    ),
                    yaxis2=dict(
                        title="Average MSME Score",
                        overlaying='y',
                        side='right',
                        range=[0, 100]
                    ),
                    height=400,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hovermode='x unified'
                )
                
                # Show Chart 3
                show_chart3 = {'display': 'block'}

    except Exception as e:
        print(f"Dashboard error: {e}")
    
    return kpis, map_fig, chart1, chart2, header, chart3, show_chart3, insights, map_desc

# DSS View
@app.callback(
    [Output('dss-main-map', 'figure'), Output('dss-data-table', 'children'), Output('dss-insights', 'children')],
    [Input('dss-state-selector', 'value'), Input('dss-highlight-selector', 'value')]
)
def update_dss(state, highlight):
    dff = df_loc.copy() if not df_loc.empty else pd.DataFrame()
    if state and not dff.empty:
        dff = dff[dff['State'] == state]
    
    if dff.empty:
        return go.Figure(), html.P("No data"), "No data available"
    
    state_agg = dff.groupby('State', as_index=False).agg({'msme_count': 'sum'})
    color = 'msme_count'
    scale = 'Viridis'
    insights = "All India view - select a highlight option"
    
    if highlight == 'high_density':
        threshold = state_agg['msme_count'].quantile(0.7)
        state_agg['highlight_score'] = state_agg['msme_count']
        state_agg.loc[state_agg['msme_count'] < threshold, 'highlight_score'] = 0
        color = 'highlight_score'
        scale = [[0, 'lightgrey'], [0.01, 'red'], [1, 'darkred']]
        count = (state_agg['msme_count'] >= threshold).sum()
        insights = f"🔴 {count} states highlighted in RED (top 30% MSME density)"
    
    elif highlight == 'low_female':
        if not df_soc.empty:
            soc_state = df_soc.groupby('State', as_index=False).agg({'female_owned': 'sum', 'total_msmes': 'sum'})
            soc_state['women_pct'] = (soc_state['female_owned'] / soc_state['total_msmes'] * 100).fillna(0)
            state_agg = state_agg.merge(soc_state[['State', 'women_pct']], on='State', how='left')
            state_agg['highlight_score'] = 100 - state_agg['women_pct']
            color = 'highlight_score'
            scale = [[0, 'lightgreen'], [0.5, 'yellow'], [1, 'orange']]
            count = (state_agg['women_pct'] < 20).sum()
            insights = f"🟠 {count} states need focus on women entrepreneurship (< 20% female owned)"
    
    elif highlight == 'high_employment':
        if not df_emp.empty:
            emp_state = df_emp.groupby('State', as_index=False).agg({'total_employment': 'sum'})
            state_agg = state_agg.merge(emp_state, on='State', how='left')
            threshold = state_agg['total_employment'].quantile(0.7)
            state_agg['highlight_score'] = state_agg['total_employment']
            state_agg.loc[state_agg['total_employment'] < threshold, 'highlight_score'] = 0
            color = 'highlight_score'
            scale = [[0, 'lightgrey'], [0.01, 'green'], [1, 'darkgreen']]
            count = (state_agg['total_employment'] >= threshold).sum()
            insights = f"🟢 {count} states are HIGH employment generators (top 30%)"
    
    fig = create_india_map(state_agg, color, scale, f"DSS: {highlight}", size_col='msme_count' if highlight == 'none' else None)
    fig.update_layout(height=880, dragmode=False)
    fig.update_mapboxes(bearing=0, pitch=0)
    
    # Table
    top_districts = dff.groupby('District')['msme_count'].sum().nlargest(15).reset_index()
    top_districts.columns = ['District', 'MSMEs']
    table = dbc.Table.from_dataframe(top_districts, striped=True, bordered=True, hover=True, size='sm')
    
    return fig, table, insights

# Upload
@app.callback(Output('upload-output', 'children'), Input('upload-data', 'contents'), State('upload-data', 'filename'))
def handle_upload(contents, filename):
    if contents is None:
        raise PreventUpdate
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            save_path = os.path.join(WORK_DIR, filename)
            df.to_csv(save_path, index=False)
            
            return dbc.Alert([
                html.H5("✅ Upload Successful!", className="alert-heading"),
                html.P(f"File: {filename}"),
                html.P(f"Rows: {len(df)} | Columns: {len(df.columns)}"),
                html.P(f"Saved to: {save_path}"),
                dbc.Button("Reload Dashboard", color="success", href="/", className="mt-2")
            ], color="success")
        else:
            return dbc.Alert("❌ Please upload a CSV file", color="danger")
    
    except Exception as e:
        return dbc.Alert(f"❌ Upload failed: {str(e)}", color="danger")

if __name__ == '__main__':
    print("Starting dashboard on http://127.0.0.1:8050", flush=True)
    app.run(debug=True, port=8050, dev_tools_ui=False, dev_tools_props_check=False)
