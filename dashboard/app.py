import sys
import subprocess
import importlib.util
from routes import setup_flask_routes

def check_package(package_name):
    """Check if a package is installed"""
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name):
    """Install a package using pip"""
    try:
        if not check_package(package_name):
            print(f"Installing {package_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], 
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            print(f"Successfully installed {package_name}")
        return True
    except Exception as e:
        print(f"Error installing {package_name}: {str(e)}")
        return False

# List of required packages
required_packages = ["dash", "plotly", "pandas", "flask"]

# Install all required packages
all_packages_installed = all(install_package(package) for package in required_packages)

if not all_packages_installed:
    print("Failed to install required packages. Please install them manually:")
    print("pip install dash plotly pandas")
    sys.exit(1)

# Import required packages
try:
    import dash
    from dash import dcc, html, Input, Output, Dash
    
    import plotly.express as px
    
    from flask import Flask, render_template
    
except ImportError as e:
    print(f"Error importing required packages: {str(e)}")
    print("Please ensure all packages are installed correctly")
    sys.exit(1)

#-----------------------------Dash App-----------------------------------------------------
def setup_dash_app():
        # Create Dash app with Flask server
    dash_app = Dash(__name__, server=server, url_base_pathname='/dash/')


    # Sample datasets (replace with your actual data)
    iris_df = px.data.iris()
    tips_df = px.data.tips()
    stocks_df = px.data.stocks()

    # Create figures
    iris_fig = px.scatter(iris_df, 
        x="sepal_width", 
        y="sepal_length", 
        color="species",
        title="Iris Dataset Analysis"
    )

    tips_fig = px.box(tips_df, 
        x="day", 
        y="total_bill", 
        color="smoker",
        title="Restaurant Tips Analysis"
    )

    stocks_fig = px.line(stocks_df, 
        x='date', 
        y='GOOG',
        title="Google Stock Prices"
    )

    # Dash layout with multiple dashboards
    dash_app.layout = html.Div([
        # Navigation tabs for dashboards
        dcc.Tabs([
            dcc.Tab(label='Iris Analysis', children=[
                html.Div([
                    html.H2("Iris Dataset Explorer"),
                    html.P("Click on points to see details"),
                    dcc.Graph(
                        id='iris-scatter',
                        figure=iris_fig
                    ),
                    html.Div(id='iris-output', className='output-container')
                ], className='dashboard-section')
            ]),
            
            dcc.Tab(label='Tips Analysis', children=[
                html.Div([
                    html.H2("Restaurant Tips Analysis"),
                    html.P("Explore tips data by day and smoking status"),
                    dcc.Graph(
                        id='tips-box',
                        figure=tips_fig
                    ),
                    html.Div([
                        dcc.Dropdown(
                            id='tips-metric',
                            options=[
                                {'label': 'Total Bill', 'value': 'total_bill'},
                                {'label': 'Tip Amount', 'value': 'tip'}
                            ],
                            value='total_bill'
                        )
                    ], className='controls-container'),
                    html.Div(id='tips-output', className='output-container')
                ], className='dashboard-section')
            ]),
            
            dcc.Tab(label='Stock Analysis', children=[
                html.Div([
                    html.H2("Stock Price Tracker"),
                    html.P("Select date range to analyze"),
                    dcc.Graph(
                        id='stock-line',
                        figure=stocks_fig
                    ),
                    dcc.DatePickerRange(
                        id='date-range',
                        start_date=stocks_df['date'].min(),
                        end_date=stocks_df['date'].max()
                    ),
                    html.Div(id='stock-output', className='output-container')
                ], className='dashboard-section')
            ])
        ], className='tabs-container')
    ], className='dash-container')

    # Callbacks for interactivity
    @dash_app.callback(
        Output('iris-output', 'children'),
        Input('iris-scatter', 'clickData')
    )
    def update_iris_output(clickData):
        if clickData is None:
            return "Click on a point to see details"
        point = clickData['points'][0]
        return f"Selected Iris: Species={point.get('customdata', 'N/A')}, " \
            f"Sepal Width={point['x']:.2f}, Sepal Length={point['y']:.2f}"

    @dash_app.callback(
        [Output('tips-box', 'figure'),
        Output('tips-output', 'children')],
        [Input('tips-metric', 'value')]
    )
    def update_tips_chart(metric):
        fig = px.box(tips_df, 
            x="day", 
            y=metric, 
            color="smoker",
            title=f"Restaurant {metric.replace('_', ' ').title()} Analysis"
        )
        avg_value = tips_df[metric].mean()
        return fig, f"Average {metric.replace('_', ' ')}: ${avg_value:.2f}"

    @dash_app.callback(
        [Output('stock-line', 'figure'),
        Output('stock-output', 'children')],
        [Input('date-range', 'start_date'),
        Input('date-range', 'end_date')]
    )
    def update_stock_chart(start_date, end_date):
        filtered_df = stocks_df[
            (stocks_df['date'] >= start_date) & 
            (stocks_df['date'] <= end_date)
        ]
        fig = px.line(filtered_df, 
            x='date', 
            y='GOOG',
            title="Google Stock Prices"
        )
        price_change = filtered_df['GOOG'].iloc[-1] - filtered_df['GOOG'].iloc[0]
        return fig, f"Price Change: ${price_change:.2f}"

    # In your Dash setup
    def get_current_data():
        global current_df
        return current_df if current_df is not None else pd.DataFrame()

    # Update your Dash callbacks to use get_current_data()
    @dash_app.callback(
        [Output('some-graph', 'figure')],
        [Input('some-input', 'value')]
    )
    def update_graph(value):
        df = get_current_data()
        if df.empty:
            return px.scatter()  # return empty figure
        # Create your figure using df
        fig = px.scatter(df, ...)
        return fig

#----------------------------------------run loop--------------------------------------

try:
    # Create Flask app first
    server = Flask(__name__)

    # ... existing Dash setup code ...
    setup_flask_routes(server)

    setup_dash_app()

    if __name__ == '__main__':
        print("Starting Flask server...")
        server.run(debug=True, port=8050)

except Exception as e:
    print(f"An error occurred while setting up the application: {str(e)}")
    sys.exit(1)
