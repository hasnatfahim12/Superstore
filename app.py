import dash
from dash import html
import dash_mantine_components as dmc
app = dash.Dash(__name__, use_pages=True)

app.layout = html.Div(
    [
        # main app framework


        dmc.Paper(
            shadow="lg",
            p="md",
            children=[
                dmc.Text("Superstore Dashboard")
            ],
            style={"background-color": "#F0F0F0", "font-size": "32px", "font-weight": "600", "display": "flex", "align-items": "center", "justify-content": "center"}
        ),

        html.Hr(),
        html.Div([
            dmc.Navbar(
            p="sm",
            width={"base": 200},
            height=600,
            style= {"margin-right": "20px", "min-width": "150px"},
            children=[
                dmc.Anchor("Home", href="/", ),
                dmc.Anchor("Data Table", href="/data-table"),
                dmc.Anchor("Graph Page", href="/graph"),
            ]),
        # html.Div([
        #     dcc.Link(page['name']+"  |  ", href=page['path'])
        #     for page in dash.page_registry.values()
        # ], style={"font-size": "20px"}),


        # content of each page
        dash.page_container], style= {"display": "flex",})
    ], style={ "padding-left": "40px", "padding-right": "40px", "height": "100vh" }
)


if __name__ == "__main__":
    app.run(debug=True)