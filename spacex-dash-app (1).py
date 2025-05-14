# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
# Corrected: Removed trailing space in CSV filename
spacex_df = pd.read_csv("spacex_launch_dash.csv") 

# Corrected: Removed leading space in column name 'Payload Mass (kg)'
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__) 

# dropdown options
# Get unique launch sites
launch_sites = spacex_df['Launch Site'].unique().tolist()
# Create list of dictionaries for options
site_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    site_options.append({'label': site, 'value': site})

# app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}), # Ensured font-size is a number
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown', 
        options=site_options,
        value='ALL', 
        placeholder="Select a Launch Site here", 
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,  
        max=10000,  
        step=1000,  # interval 
        marks={  
            0: '0 Kg',
            2500: '2500 Kg',
            5000: '5000 Kg',
            7500: '7500 Kg',
            10000: '10000 Kg'
        },
        value=[min_payload, max_payload]  
    ),
    html.Br(), 

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Filter for successful launches to show distribution by site
        all_sites_success_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            all_sites_success_df,
            names='Launch Site', 
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Filter for the specific selected site
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Create a temporary column for more descriptive labels in the pie chart
        temp_df = site_df.copy() 
        temp_df['outcome_label'] = temp_df['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            temp_df,
            names='outcome_label', 
            title=f'Launch Outcomes for Site: {entered_site}',
            color='outcome_label', # Color by the new outcome_label
            color_discrete_map={'Success':'green', 'Failure':'red'} # Assign specific colors
        )
        return fig

# TASK 4:


@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    # payload_range is a list [min_selected_payload, max_selected_payload]
    low, high = payload_range
    
    # Filter DataFrame based on selected payload range first
    # Ensure the column name 'Payload Mass (kg)' exactly matches your CSV.
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        # If ALL sites are selected, use all rows from the payload-filtered DataFrame
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category', 
            title='Payload vs. Launch Outcome for All Sites (Filtered by Payload)',
            labels={'class': 'Launch Outcome (0=Fail, 1=Success)'} # More descriptive y-axis label
        )
        return fig
    else:
        # If a specific launch site is selected, further filter the DataFrame for that site
        site_specific_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_specific_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category', 
            title=f'Payload vs. Launch Outcome for Site: {entered_site} (Filtered by Payload)',
            labels={'class': 'Launch Outcome (0=Fail, 1=Success)'} # More descriptive y-axis label
        )
        return fig

# Run the app
if __name__ == '__main__':
    # Using app.run and specifying port, debug=True
    app.run(debug=True, port=8051) #issue with ports changed to test
