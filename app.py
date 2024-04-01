import dash
from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

app = dash.Dash(__name__, use_pages=True)

app.layout = html.Div(
    [
        # main app framework

        dmc.Paper(
            shadow="lg",
            p="md",
            children=[
                dmc.Anchor("Superstore Dashboard", href="/"),
            ],
            style={"background-color": "#F0F0F0", "font-size": "32px", "font-weight": "600",
                   "display": "flex","align-items": "center", "justify-content": "center",
                   "text-align": "center"}
        ),

        html.Hr(),
        html.Div([
            dmc.Navbar(
            p="sm",
            width={"base": 200},
            height=600,
            style= {"margin-right": "20px", "min-width": "150px", "gap": "10px"},
            children=[
                html.Div([
                    DashIconify(icon="flat-color-icons:home", width=25),
                    dmc.Anchor("Home", href="/"),
                ], style={"display": "flex", "align-items": "center", "gap": "5px"}),
                html.Div([
                    DashIconify(icon="flat-color-icons:data-sheet", width=25),
                    dmc.Anchor("Data Table", href="/data-table"),
                ], style={"display": "flex", "align-items": "center", "gap": "5px"}),
                html.Div([
                    DashIconify(icon="flat-color-icons:combo-chart", width=25),
                    dmc.Anchor("Graph Page", href="/graph"),
                ], style={"display": "flex", "align-items": "center", "gap": "5px"}),
            ]),

        # content of each page
        dash.page_container], style= {"display": "flex", "padding-bottom": "20px"})
    ], style={ "padding-left": "40px", "padding-right": "40px", "height": "100vh"}
)


if __name__ == "__main__":
    app.run(debug=True)