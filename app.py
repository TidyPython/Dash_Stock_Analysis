#####################################################
# Part 1: Import needed packages
#####################################################
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
import dash_bootstrap_components as dbc

#####################################################
# Part 2: Basic app information
#####################################################
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Stock Analysis Dashboard"
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",}

#####################################################
# Part 3: Data information
#####################################################
PATH = pathlib.Path(__file__)
DATA_PATH = PATH.joinpath("../datasets").resolve()

df = pd.read_csv(DATA_PATH.joinpath("df_combined_07_28_2022.csv"))

df = df.sort_values(by="Calendar Year")
df = df.round(0)

sales_list = ["Total Revenues", "Cost of Revenues", "Gross Profit", "Total Operating Expenses", "Operating Income", "Net Income",
              "Shares Outstanding", "Close Stock Price", "Market Cap", "Multiple of Revenue"]

#####################################################
# Part 4: App layout
#####################################################
app.layout = html.Div([
    html.Div([html.Div([
        html.Div(dcc.Dropdown(
            id='genre-dropdown', value=['Amazon', 'Tesla', 'Microsoft', 'Apple', 'Google'], clearable=False, multi=True,
            options=[{'label': x, 'value': x} for x in sorted(df.Company.unique())]
        ), className='six columns', style={"width": "50%"}, ),

        html.Div(dcc.Dropdown(
            id='sales-dropdown', value='Total Revenues', clearable=False,
            options=[{'label': x, 'value': x} for x in sales_list]
        ), className='six columns', style={"width": "15%"}, ),

    ], className='row'), ], className='custom-dropdown'),

    html.Div([dcc.Graph(id='my-bar', figure={}, config={'displayModeBar': True, 'displaylogo': False,
                                                        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d',
                                                                                   'zoomIn2d', 'zoomOut2d',
                                                                                   'resetScale2d']}), ],style={'width': '1250px'}),

    html.Div(html.Div(id='table-container_1'), style={'marginBottom': '15px', 'marginTop': '0px'}),], style=CONTENT_STYLE)

#####################################################
# Part 5: Callback to update the chart and table
#####################################################
@app.callback(
    [Output(component_id='my-bar', component_property='figure'), Output('table-container_1', 'children')],
    [Input(component_id='genre-dropdown', component_property='value'),
     Input(component_id='sales-dropdown', component_property='value')]
)

def display_value(genre_chosen, sales_chosen):
    if len(genre_chosen) == 0:
        dfv_fltrd = df[df['Company'].isin(['Amazon', 'Tesla', 'Microsoft', 'Apple', 'Google'])]
    else:
        dfv_fltrd = df[df['Company'].isin(genre_chosen)]

    dfv_fltrd.sort_values(by=['Company'])

    fig = px.line(dfv_fltrd, color='Company', x='Calendar Year', markers=True, y=sales_chosen, text=None,
                  template='ggplot2', width=1250, height=600)

    fig.update_layout(
        xaxis=dict(showgrid=False, showline=True, linecolor="#17202A"),
        yaxis=dict(showgrid=True, showline=True, linecolor="#17202A", gridcolor='#EAECEE'),
        font=dict(
            family="Times New Roman",
            size=14,
        ),

        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis_title="Quarters (Calendar Year)",
        width=1055,
        legend_font_size=19,
        legend=dict(itemsizing='trace'),)
    fig.update_traces(line=dict(width=4))

    df_reshaped = dfv_fltrd.pivot(index='Company', columns='Calendar Year', values=sales_chosen)
    df_reshaped_2 = df_reshaped.reset_index()


    return (fig,
            dash_table.DataTable(columns=[{"name": i, "id": i} for i in df_reshaped_2.columns],
                                 data=df_reshaped_2.to_dict('records'),
                                 export_format="csv",
                                 style_as_list_view=True,
                                 fill_width=True,
                                 style_cell={'font-size': '12px'},
                                 style_table={'maxWidth': 1055},
                                 style_header={'backgroundColor': 'black',
                                               'color': 'white', },
                                 style_data_conditional=[
                                     {
                                         'if': {
                                             'row_index': 'even',
                                             'filter': 'row_index >num(2)',
                                         },
                                         'backgroundColor': '#EBEDEF'
                                     }, ]
                                 ),
)

#####################################################
# Part 6: Set up local server to show the dashboard
#####################################################
if __name__ == '__main__':
    app.run_server(debug=False, port=8008)