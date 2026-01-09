"""
Production-ready version of sprint_dashboard.py
Handles file paths for both local and hosted environments
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, dash_table, callback
import dash
import dash_bootstrap_components as dbc
import os

# Initialize the Dash app with Bootstrap theme and custom CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Sprint Story Points Dashboard"

# Handle file path for both local and production environments
def get_data_path():
    """Get the Excel file path, checking multiple locations"""
    # Local development path
    local_path = r'C:\Users\Amit Sharma\Downloads\cw_finalfinal.xlsx'
    if os.path.exists(local_path):
        return local_path
    
    # Production path (same directory as script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prod_path = os.path.join(script_dir, 'cw_finalfinal.xlsx')
    if os.path.exists(prod_path):
        return prod_path
    
    # Environment variable path
    env_path = os.environ.get('DATA_FILE_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    
    # Default to current directory
    default_path = 'cw_finalfinal.xlsx'
    if os.path.exists(default_path):
        return default_path
    
    raise FileNotFoundError(
        f"Excel file not found. Tried:\n"
        f"1. {local_path}\n"
        f"2. {prod_path}\n"
        f"3. {env_path if env_path else 'N/A (from env)'}\n"
        f"4. {default_path}\n"
        f"Please ensure the file exists in one of these locations."
    )

# Load and prepare data
try:
    csv_path = get_data_path()
    df = pd.read_excel(csv_path)
    df.fillna(0, inplace=True)
except FileNotFoundError as e:
    print(f"ERROR: {e}")
    # Create empty dataframe to prevent app crash
    df = pd.DataFrame({'Developer': [], 'Sprint': [], 'Story Points': []})
    print("App will start but data will be empty. Please fix the file path.")

# Melt the DataFrame to long format
df_melted = df.melt(id_vars="Developer", var_name="Sprint", value_name="Story Points") if not df.empty else pd.DataFrame()

# Get unique developers and sprints
developers = sorted(df['Developer'].unique().tolist()) if not df.empty and 'Developer' in df.columns else []
sprints = sorted([col for col in df.columns if col != 'Developer']) if not df.empty else []

# Custom CSS for enhanced UI
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        {%css%}
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .main-container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                margin: 20px auto;
                max-width: 1400px;
                padding: 30px;
            }
            .header-gradient {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
            .stat-card-1 {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .stat-card-1:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
            }
            .stat-card-2 {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .stat-card-2:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(245, 87, 108, 0.4);
            }
            .stat-card-3 {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .stat-card-3:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(79, 172, 254, 0.4);
            }
            .stat-card-4 {
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                color: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(67, 233, 123, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .stat-card-4:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(67, 233, 123, 0.4);
            }
            .stat-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
                opacity: 0.9;
            }
            .stat-value {
                font-size: 2.5em;
                font-weight: 700;
                margin: 10px 0;
            }
            .stat-label {
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                opacity: 0.9;
                font-weight: 600;
            }
            .filter-card {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                border: none;
            }
            .chart-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                border: none;
            }
            .table-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                border: none;
            }
            .section-title {
                color: #333;
                font-weight: 700;
                font-size: 1.5em;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .btn-custom {
                border-radius: 25px;
                padding: 8px 20px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-custom:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
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

# Define the layout
app.layout = dbc.Container([
    html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1([
                        html.I(className="fas fa-chart-line me-3"),
                        "Sprint Story Points Dashboard"
                    ], className="text-center mb-3", style={'fontWeight': '700', 'fontSize': '2.5em'}),
                    html.P([
                        html.I(className="fas fa-users me-2"),
                        "Track developer performance across sprints"
                    ], className="text-center", style={'fontSize': '1.1em', 'opacity': '0.95'})
                ], className="header-gradient")
            ])
        ], className="mb-4"),
        
        # Statistics Cards
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-tasks stat-icon")
                    ]),
                    html.Div(id="stat-total", className="stat-value"),
                    html.Div("Total Story Points", className="stat-label")
                ], className="stat-card-1 text-center")
            ], md=3, className="mb-3"),
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-chart-bar stat-icon")
                    ]),
                    html.Div(id="stat-avg", className="stat-value"),
                    html.Div("Average per Sprint", className="stat-label")
                ], className="stat-card-2 text-center")
            ], md=3, className="mb-3"),
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-arrow-up stat-icon")
                    ]),
                    html.Div(id="stat-max", className="stat-value"),
                    html.Div("Max Story Points", className="stat-label")
                ], className="stat-card-3 text-center")
            ], md=3, className="mb-3"),
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-user-friends stat-icon")
                    ]),
                    html.Div(id="stat-developers", className="stat-value"),
                    html.Div("Active Developers", className="stat-label")
                ], className="stat-card-4 text-center")
            ], md=3, className="mb-3"),
        ], className="mb-4"),
        
        # Filters Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-filter me-2"),
                            "Filters"
                        ], className="section-title"),
                        html.Label([
                            html.I(className="fas fa-user me-2"),
                            "Select Developers:"
                        ], className="fw-bold mb-2", style={'fontSize': '1.1em', 'color': '#333'}),
                        dcc.Dropdown(
                            id='developer-filter',
                            options=[{'label': dev, 'value': dev} for dev in developers],
                            multi=True,
                            placeholder="Select developers (leave empty to show all)",
                            style={'width': '100%'},
                            className="mb-4"
                        ),
                        html.Label([
                            html.I(className="fas fa-sliders-h me-2"),
                            "Y-Axis Range:"
                        ], className="fw-bold mb-2", style={'fontSize': '1.1em', 'color': '#333'}),
                        dcc.RangeSlider(
                            id='yaxis-range',
                            min=0,
                            max=50,
                            step=5,
                            value=[0, 45],
                            marks={i: str(i) for i in range(0, 51, 10)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                    ])
                ], className="filter-card")
            ])
        ], className="mb-4"),
        
        # Main Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-line-chart me-2"),
                                "Story Points Over Time"
                            ], className="section-title d-inline"),
                            dbc.ButtonGroup([
                                dbc.Button([
                                    html.I(className="fas fa-eye me-2"),
                                    "Show All"
                                ], id="btn-show-all", size="sm", color="primary", className="btn-custom ms-3"),
                                dbc.Button([
                                    html.I(className="fas fa-eye-slash me-2"),
                                    "Hide All"
                                ], id="btn-hide-all", size="sm", color="secondary", className="btn-custom")
                            ], className="float-end")
                        ], className="mb-3 d-flex justify-content-between align-items-center"),
                        dcc.Graph(id='main-chart', style={'height': '600px'})
                    ])
                ], className="chart-card")
            ])
        ], className="mb-4"),
        
        # Summary Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-table me-2"),
                            "Summary Statistics by Developer"
                        ], className="section-title"),
                        html.Div(id='summary-table')
                    ])
                ], className="table-card")
            ])
        ], className="mb-4"),
        
    ], className="main-container")
], fluid=True, style={'padding': '0', 'background': 'transparent'})

# Callback for statistics
@callback(
    [Output('stat-total', 'children'),
     Output('stat-avg', 'children'),
     Output('stat-max', 'children'),
     Output('stat-developers', 'children')],
    [Input('developer-filter', 'value')]
)
def update_stats(selected_developers):
    if df_melted.empty:
        return "0", "0.0", "0", "0"
    
    filtered_df = df_melted.copy()
    
    if selected_developers:
        filtered_df = filtered_df[filtered_df['Developer'].isin(selected_developers)]
    
    total = filtered_df['Story Points'].sum()
    avg = filtered_df['Story Points'].mean()
    max_val = filtered_df['Story Points'].max()
    active_devs = filtered_df[filtered_df['Story Points'] > 0]['Developer'].nunique()
    
    return f"{total:,.0f}", f"{avg:.1f}", f"{max_val:.0f}", f"{active_devs}"

# Callback for main chart - combines all inputs
@callback(
    Output('main-chart', 'figure'),
    [Input('developer-filter', 'value'),
     Input('yaxis-range', 'value'),
     Input('btn-show-all', 'n_clicks'),
     Input('btn-hide-all', 'n_clicks')],
    prevent_initial_call=False
)
def update_main_chart(selected_developers, yaxis_range, show_clicks, hide_clicks):
    if df_melted.empty:
        # Return empty figure if no data
        fig = go.Figure()
        fig.add_annotation(text="No data available. Please check file path.", 
                         xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    filtered_df = df_melted.copy()
    
    if selected_developers:
        filtered_df = filtered_df[filtered_df['Developer'].isin(selected_developers)]
    
    # Create interactive line chart
    fig = px.line(
        filtered_df, 
        x="Sprint", 
        y="Story Points", 
        color="Developer", 
        markers=True,
        title=""
    )
    
    # Determine visibility based on button clicks
    visibility = 'legendonly'
    if show_clicks and hide_clicks:
        visibility = True if show_clicks > hide_clicks else 'legendonly'
    elif show_clicks:
        visibility = True
    elif hide_clicks:
        visibility = 'True'
    
    # Apply visibility to all traces
    for trace in fig.data:
        trace.visible = visibility
    
    # Improve layout with modern styling
    fig.update_layout(
        width=None,
        height=600,
        xaxis_title=dict(text="Sprint Date", font=dict(size=14, color='#333')),
        yaxis_title=dict(text="Story Points", font=dict(size=14, color='#333')),
        yaxis=dict(
            range=yaxis_range, 
            dtick=5,
            gridcolor='rgba(128, 128, 128, 0.2)',
            gridwidth=1,
            showgrid=True
        ),
        xaxis=dict(
            tickangle=45,
            gridcolor='rgba(128, 128, 128, 0.2)',
            gridwidth=1,
            showgrid=True
        ),
        legend=dict(
            title=dict(text="Developer", font=dict(size=13, color='#333')),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1
        ),
        hovermode="x unified",
        plot_bgcolor='rgba(250, 250, 250, 0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, sans-serif", size=12, color='#333'),
        margin=dict(l=60, r=50, t=20, b=100),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#667eea",
            font_size=12,
            font_family="Segoe UI"
        )
    )
    
    return fig

# Callback for summary table
@callback(
    Output('summary-table', 'children'),
    [Input('developer-filter', 'value')]
)
def update_summary_table(selected_developers):
    if df_melted.empty:
        return html.P("No data available.", className="text-muted")
    
    filtered_df = df_melted.copy()
    
    if selected_developers:
        filtered_df = filtered_df[filtered_df['Developer'].isin(selected_developers)]
    
    # Calculate summary statistics per developer
    summary = filtered_df.groupby('Developer').agg({
        'Story Points': ['sum', 'mean', 'max', 'count']
    }).round(1)
    
    summary.columns = ['Total Points', 'Average Points', 'Max Points', 'Sprints Count']
    summary = summary.reset_index()
    summary = summary.sort_values('Total Points', ascending=False)
    
    return dash_table.DataTable(
        data=summary.to_dict('records'),
        columns=[{"name": i, "id": i} for i in summary.columns],
        style_cell={
            'textAlign': 'left',
            'padding': '15px',
            'fontFamily': 'Segoe UI, sans-serif',
            'fontSize': '14px',
            'border': 'none'
        },
        style_header={
            'backgroundColor': '#667eea',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': 'none',
            'fontSize': '15px',
            'padding': '20px'
        },
        style_data={
            'backgroundColor': 'white',
            'color': '#333',
            'border': 'none'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            },
            {
                'if': {'filter_query': '{Total Points} > 0'},
                'backgroundColor': '#e7f3ff',
                'fontWeight': '500'
            },
            {
                'if': {'row_index': 0},
                'backgroundColor': '#fff3cd',
                'fontWeight': '600'
            }
        ],
        page_size=15,
        sort_action="native",
        filter_action="native",
        style_table={
            'borderRadius': '10px',
            'overflow': 'hidden',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
        },
        cell_selectable=False
    )

# Make server accessible for production deployment
server = app.server

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
