from dash.dependencies import Input, Output
from dash_bootstrap_components._components.NavbarBrand import NavbarBrand
from dash_html_components.Figure import Figure
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.io as plt_io

# Custom dark template for plotly
# plt_io.templates["custom_dark"] = plt_io.templates["plotly_dark"]
plt_io.templates["custom_dark"] = plt_io.templates["plotly_dark"]

# set the paper_bgcolor and the plot_bgcolor to a new color
plt_io.templates["custom_dark"]["layout"]["paper_bgcolor"] = "#30404D"
plt_io.templates["custom_dark"]["layout"]["plot_bgcolor"] = "#30404D"

# you may also want to change gridline colors if you are modifying background
plt_io.templates["custom_dark"]["layout"]["yaxis"]["gridcolor"] = "#4f687d"
plt_io.templates["custom_dark"]["layout"]["xaxis"]["gridcolor"] = "#4f687d"

# Project module
from data import DataFlow

# required data

data = DataFlow()
world_wide_data = data.get_all_country_data()
names_of_all_countries = world_wide_data['country']

# data table columns
data_table = [
    "state",
    "confirmed",
    "deaths",
    "recovered",
    "active",
    "incident_rate",
    "case_fatality_ratio",
]

# global_options

global_options = [
    {"label": "TOTAL CONFIRMED", "value": "total_confirmed"},
    {"label": "TOTAL DEATHS", "value": "total_deaths"},
    {"label": "TOTAL RECOVERED", "value": "total_recovered"},
]

global_status = data.get_global_status()

# --------------- COUNTRY NAME OPTIONS (DROPDOWN OPTIONS) ---------------------
country_name_options = [ {"label":i,"value":i} for i in names_of_all_countries ]
   

graph_type = [{"label": "LINE", "value": "LINE"}, {"label": "BAR", "value": "BAR"}]

timeseries_options = [
    {"label": "Confirmed", "value": "confirmed"},
    {"label": "Deaths", "value": "deaths"},
    {"label": "Recovered", "value": "recovered"},
]




# CREATING OUR DASHBOARD
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# -------------------- All Callbacks (RETURNS GRAPHS OR TABLES) ------------
# global table_data


@app.callback(
    Output(component_id="state_data_table", component_property="data"),
    Input(component_id="country_name_dropdown", component_property="value"),
)
def return_data_table(value):
    # state data of a given country
    table_data = data.get_selected_country_state_data(value)
    return table_data.to_dict("records")


@app.callback(
    Output(component_id="total_vaccinations", component_property="figure"),
    [
        Input(component_id="vaccination_country_name", component_property="value"),
        Input(component_id="graph_type", component_property="value"),
    ],
)
def total_vaccination(country, graph_type):
    vaccine_data = data.get_vaccination_status_by_country_timeseries(country)
    if graph_type == "LINE":
        fig = px.line(x=vaccine_data["dates"], y=vaccine_data["total_vaccinations"])
    else:
        fig = px.bar(x=vaccine_data["dates"], y=vaccine_data["total_vaccinations"])

    fig.update_layout(
        title="TOTAL VACCINES AVAILABILITY",
        xaxis_title="DATE",
        yaxis_title="NO. OF VACCINES AVAILABLE",
    )

    fig.layout.template = "custom_dark"
    return fig


@app.callback(
    Output(component_id="people_vaccinated", component_property="figure"),
    [
        Input(component_id="vaccination_country_name", component_property="value"),
        Input(component_id="graph_type", component_property="value"),
    ],
)
def people_vaccinated(country, graph_type):
    vaccine_data = data.get_vaccination_status_by_country_timeseries(country)
    if graph_type == "BAR":
        fig = px.bar(x=vaccine_data["dates"], y=vaccine_data["people_vaccinated"])
    else:
        fig = px.line(x=vaccine_data["dates"], y=vaccine_data["people_vaccinated"])

    fig.update_layout(
        title="PEOPLE VACCINATED",
        xaxis_title="DATE",
        yaxis_title="NO. OF PEOPLE VACCINATED",
    )
    fig.layout.template = "custom_dark"
    return fig


@app.callback(
    Output(component_id="people_fully_vaccinated", component_property="figure"),
    [
        Input(component_id="vaccination_country_name", component_property="value"),
        Input(component_id="graph_type", component_property="value"),
    ],
)
def people_fully_vaccinated(country, graph_type):
    vaccine_data = data.get_vaccination_status_by_country_timeseries(country)
    if graph_type == "LINE":
        fig = px.line(
            x=vaccine_data["dates"], y=vaccine_data["people_fully_vaccinated"]
        )
    else:
        fig = px.bar(x=vaccine_data["dates"], y=vaccine_data["people_fully_vaccinated"])

    fig.update_layout(
        title="PEOPLE FULLY VACCINATED",
        xaxis_title="DATE",
        yaxis_title="NO. OF PEOPLE VACCINATED",
    )
    fig.layout.template = "custom_dark"
    return fig


def top_20_countries(category=None):

    if category == "total_recovered":
        color_scale = "green"
    elif category == "total_deaths":
        color_scale = "red"
    else:
        color_scale = "blue"

    data = DataFlow()
    country_data = data.get_all_country_data()
    data = country_data.sort_values(by=category, ascending=False)[:20]
    fig = px.bar(
        data,
        y="country",
        x=category,
        title="TOP 20 COUNTRIES WITH MOST {}".format(category.upper()),
        color_discrete_sequence=[color_scale],
    )
    fig.layout.template = "custom_dark"
    return fig


@app.callback(
    Output("top_timeseries_graph", "figure"), Input("top_timeseries_category", "value")
)
def timeseries_graph_of_top_countries(category):
    data = DataFlow()

    if category == "recovered":
        top_country_name = data.get_all_country_data().sort_values(
            by="total_recovered", ascending=False
        )[:10]["country"]
    elif category == "deaths":
        top_country_name = data.get_all_country_data().sort_values(
            by="total_deaths", ascending=False
        )[:10]["country"]
    else:
        top_country_name = data.get_all_country_data().sort_values(
            by="total_confirmed", ascending=False
        )[:10]["country"]

    # Generating Titles
    title_list = []
    for country in top_country_name:
        title = "{} IN {}".format(category.upper(), country.upper())
        title_list.append(title)

    fig = make_subplots(rows=5, cols=2, subplot_titles=title_list)
    row = 1
    col = 1
    for country in top_country_name:
        df = data.get_timeseries_data_by_country(country=country, category=category)
        if col == 2:
            fig.add_trace(
                go.Line(x=df["Date"], y=df[category], name=country), row=row, col=col
            )
            col = 1
            row += 1
        else:
            fig.add_trace(
                go.Line(x=df["Date"], y=df[category], name=country), row=row, col=col
            )
            col += 1

    fig.update_layout(height=1200, width=1350)

    fig.layout.template = "custom_dark"
    return fig


# ---------------------- Claabacks Ends -----------------


# ---------------------- LAYOUT OF PAGE ----------------------------------------------------------------------------------------
app.layout = html.Div(
    [
        html.Div(
            [
                dbc.NavbarSimple(
                    [],
                    sticky="/covid-19.jpg",
                    brand="COVID-19 GLOBAL TRACKER",
                    color="dark",
                ),
            ],
            className="nav_div",
        ),
        # Global Status records
        html.Div(
            children=[
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4("Total Global Cases"),
                            html.Br(),
                            html.H3(global_status["confirmed"]),
                            html.H5(
                                "{} M".format(
                                    round(global_status["confirmed"] / 1000000, 2)
                                )
                            ),
                        ],
                    ),
                    color="warning",
                    style={"size": 100},
                ),
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4("Total Global Deaths"),
                            html.Br(),
                            html.H3(global_status["deaths"]),
                            html.H5(
                                "{} M".format(
                                    round(global_status["deaths"] / 1000000, 2)
                                )
                            ),
                        ],
                    ),
                    color="danger",
                    style={"size": 100},
                ),
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4("Total Global Recovered"),
                            html.Br(),
                            html.H3(global_status["recovered"]),
                            html.H5(
                                "{} M".format(
                                    round(global_status["recovered"] / 1000000, 2)
                                )
                            ),
                        ]
                    ),
                    color="success",
                    style={"size": 100},
                ),
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4("Total Global Active Cases"),
                            html.Br(),
                            html.H3(global_status["active"]),
                            html.H5(
                                "{} M".format(
                                    round(global_status["active"] / 1000000, 2)
                                )
                            ),
                        ]
                    ),
                    color="warning",
                ),
            ],
            className="Global_Status_Div",
        ),
        html.Div(
            [html.H3("Situation By Country")],
            style={"padding-bottom": "30", "font-color": "white"},
        ),
        # TIMESERIES BY COUNTRY
        html.Div(
            [
                dcc.Dropdown(
                    id="top_timeseries_category",
                    value="recovered",
                    options=timeseries_options,
                    style={"background-color": "#30404D"},
                ),
                html.Br(),
                dcc.Graph(id="top_timeseries_graph"),
            ]
        ),
        # GLOBAL GRAPH
        html.Br(),
        # TOp 20 Nations
        # Global Info Graphs
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Br(),
                                dcc.Graph(
                                    id="total_cases",
                                    figure=top_20_countries("total_confirmed"),
                                ),
                            ],
                            className="Total_Cases",
                        ),
                        html.Div(
                            children=[
                                html.Br(),
                                dcc.Graph(
                                    id="total_deaths",
                                    figure=top_20_countries("total_deaths"),
                                ),
                            ],
                            className="Total_Deaths",
                        ),
                    ],
                    className="Top_20_Country_First_Two",
                ),
                html.Div(
                    children=[
                        html.Br(),
                        dcc.Graph(
                            id="total_recovered",
                            figure=top_20_countries("total_recovered"),
                        ),
                    ],
                    className="Total_Recovered",
                ),
            ],
            className="Top_20_Country_Status",
        ),  # Global Status
        html.Br(),
        html.Div(
            children=[
                html.H4(
                    "SITUATION OF STATES OF SELECTED COUNTRY",
                    id="situation_of_states_text",
                ),
                dcc.Dropdown(
                    id="country_name_dropdown",
                    options=country_name_options,
                    value="India",
                    style={"background-color": "#30404D"},
                ),
                html.Br(),
            ],
            className="Country_states_analysis",
        ),
        html.Div(  # Data table
            children=[
                dash_table.DataTable(
                    id="state_data_table",
                    columns=[{"name": i, "id": i} for i in data_table],
                    page_size=20,
                    style_cell_conditional=[
                        {"if": {"column_id": c}, "textAlign": "left"}
                        for c in ["Date", "Region"]
                    ],
                    style_data_conditional=[
                        {
                            "backgroundColor": "#30404D",
                        }
                    ],
                    style_header={
                        "backgroundColor": "#30404D",
                        "fontWeight": "bold",
                    },
                    style_cell={"color": "white"},
                )
            ],
            className="DataTable",
        ),
        html.Br(),
        # Vaccination plot
        html.Div(
            children=[
                html.H3("VACCINATION STATUS OF SELECTED COUNTRY"),
                html.Br(),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="vaccination_country_name",
                            options=country_name_options,
                            value="India",
                            style={"width": 250, "background-color": "#30404D"},
                        ),
                        dcc.Dropdown(
                            id="graph_type",
                            options=graph_type,
                            value="LINE",
                            style={"width": 250, "background-color": "#30404D"},
                        ),
                    ],
                    className="vaccination_dropdowns",
                ),
            ]
        ),
        html.Div(
            children=[
                dcc.Graph(id="total_vaccinations"),
                dcc.Graph(id="people_vaccinated"),
                dcc.Graph(id="people_fully_vaccinated"),
            ],
            className="vaccination_graphs",
        ),  # vaccination plots ends
    ],
    className="main_div",
)
# ------------------------- RUN PROGRAM -----------------------------------------

if __name__ == "__main__":
    app.run_server(debug=True)
