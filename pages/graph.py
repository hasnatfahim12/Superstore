import dash
from dash import dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_mantine_components as dmc

# Load the data

# Read all three sheets

dash.register_page(__name__, name='Chart Page')

orders_df = pd.read_excel("./Sample - Superstore.xlsx", sheet_name="Orders")
returns_df = pd.read_excel("./Sample - Superstore.xlsx", sheet_name="Returns")
people_df = pd.read_excel("./Sample - Superstore.xlsx", sheet_name="People")

# Merge the Orders and Returns DataFrames
merged_df = pd.merge(orders_df, returns_df, on="Order ID", how="left")

# Merge the merged_df with the People DataFrame
df = pd.merge(merged_df, people_df, on="Region", how="left")

df = df.sort_values(by='Order Date')
# Calculate 'Days to Ship'
df['Days to Ship'] = (pd.to_datetime(df['Ship Date']) - pd.to_datetime(df['Order Date'])).dt.days

# Calculate 'Profit Ratio'
df['Profit Ratio'] = (df['Profit'] / df['Sales']) * 100

axis_options = ['Days to Ship', 'Discount', 'Profit', 'Profit Ratio', 'Quantity', 'Returns', 'Sales']

dropdown_style = {
    "font-size": ".9rem",  # Adjust the font size as needed
    "font-family": "Inter, sans-serif",
    "margin-top": "5px"
}

# Define the layout
layout = dmc.MantineProvider(
    theme={"primaryColor": ""},
    children=[
        dmc.Grid(
            children=[
                dmc.Col(
                    span=4,
                    children=[
                        dmc.DateRangePicker(
                            id="date-range",
                            label="Date Range",
                            value=[df["Order Date"].min(), df["Order Date"].max()],
                        )
                    ]
                ),
                dmc.Col(
                    span=4,
                    children=[
                        dmc.Select(
                            id="granularity-dropdown",
                            label="Granularity",
                            data=[
                                {"label": "Daily", "value": "D"},
                                {"label": "Week", "value": "W"},
                                {"label": "Month", "value": "M"},
                                {"label": "Quarter", "value": "Q"},
                                {"label": "Year", "value": "Y"},
                            ],
                            value="M",
                        )
                    ]
                ),


                dmc.Col(
                    span=6,
                    children=[
                        dmc.Paper(
                            shadow="md",
                            p="md",
                            children=[
                                dcc.Graph(
                                    id='timeline-graph',
                                    figure={}
                                )
                            ],
                        )
                    ],
                ),
                dmc.Col(
                    span=6,
                    children=[
                        dmc.Paper(
                            shadow="md",
                            p="md",
                            children=[
                                dcc.Graph(
                                    id='bubble-chart',
                                    figure={}
                                )
                            ],
                        ),
                          # Add margin between label and dropdown
                        dmc.Grid(
                            style={"margin-top": "20px"},
                            children=[
                                dmc.Col(
                                    span=4,
                                    children=[
                                        dmc.Text('x-axis',
                                                 style={'margin-right': '10px', 'font-size': '.85rem',}),
                                        dcc.Dropdown(
                                            id='x-axis-dropdown',
                                            options=[{'label': col, 'value': col} for col in axis_options if
                                                     col != 'Sales'],
                                            value='Profit',
                                            style=dropdown_style,
                                            clearable=False
                                        )
                                    ],
                                ),
                                dmc.Col(
                                    span=4,
                                    children=[
                                        dmc.Text('y-axis',
                                                 style={'margin-right': '10px', 'font-size': '.85rem', }),
                                        dcc.Dropdown(
                                            id='y-axis-dropdown',
                                            options=[{'label': col, 'value': col} for col in axis_options if
                                                     col != 'Profit'],
                                            value='Sales',
                                            style=dropdown_style,
                                            clearable=False
                                        )
                                    ],
                                ),
                                dmc.Col(
                                    span=4,
                                    children=[
                                        dmc.Text('breakdown',
                                                 style={'margin-right': '10px', 'font-size': '.85rem', }),
                                        dcc.Dropdown(
                                            id="breakdown-dropdown",
                                            options=[
                                                {"label": col, "value": col}
                                                for col in [
                                                    "Segment",
                                                    "Ship Mode",
                                                    "Customer Name",
                                                    "Category",
                                                    "Sub-Category",
                                                    "Product Name",
                                                ]
                                            ],
                                            value="Segment",
                                            style=dropdown_style,
                                            clearable=False
                                        )
                                    ],
                                ),
                            ]
                        ),
                    ],
                ),
            ]
        )
    ],
)


@callback(
    [Output('x-axis-dropdown', 'options'),
     Output('y-axis-dropdown', 'options')],
    [Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value')]
)
def update_axis_options(selected_x_axis, selected_y_axis):
    # Define the options for the y-axis dropdown
    y_axis_options = [
        {'label': col, 'value': col}
        for col in axis_options
        if col != selected_x_axis  # Exclude the selected x-axis value from the options
    ]

    x_axis_options = [
        {'label': col, 'value': col}
        for col in axis_options
        if col != selected_y_axis  # Exclude the selected y-axis value from the options
    ]

    return x_axis_options, y_axis_options



@callback(
    [Output('timeline-graph', 'figure'),
     Output('bubble-chart', 'figure')],
    [Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('breakdown-dropdown', 'value'),
     Input("date-range", "value"),
     Input('granularity-dropdown', 'value')]
)
def update_graphs(x_axis, y_axis, breakdown, dates, granularity):
    # Filter the DataFrame
    filtered_df = df[(df['Order Date'] >= dates[0]) & (df['Order Date'] <= dates[1])]
    filtered_df['Period'] = pd.to_datetime(filtered_df['Order Date']).dt.to_period(granularity).astype(str)

    # Create a boolean mask to identify rows where 'Returned' is 'Yes' and 'Order ID' is unique
    mask = None
    if breakdown in ['Segment', 'Ship Mode', 'Customer Name']:
        mask = (filtered_df['Returned'] == 'Yes') & (~filtered_df.duplicated(subset=['Order ID'], keep='first'))
    elif breakdown == 'Category':
        mask = (filtered_df['Returned'] == 'Yes') & (~filtered_df.duplicated(subset=['Order ID', 'Category'], keep='first'))
    elif breakdown == 'Sub-Category':
        mask = (filtered_df['Returned'] == 'Yes') & (~filtered_df.duplicated(subset=['Order ID', 'Sub-Category'], keep='first'))
    else:
        mask = (filtered_df['Returned'] == 'Yes') & (~filtered_df.duplicated(subset=['Order ID', 'Product ID'], keep='first'))
    # Set the 'Returns' column to 1 for rows that satisfy the condition in the mask
    filtered_df.loc[mask, 'Returns'] = 1
    filtered_df['Returns'].fillna(0, inplace=True)
    filtered_df['Discount'] = filtered_df['Discount'] * 100

    # Define aggregation functions
    agg_funcs = {
        col: 'sum' if col in ['Profit', 'Sales', 'Quantity', 'Returns'] else
        ('mean' if col in ['Discount', 'Days to Ship'] else 'first')
        for col in filtered_df.columns
    }



    # Group and aggregate the DataFrame
    grouped_df_bubble = (
        filtered_df
        .groupby(breakdown, as_index=False)
        .agg(agg_funcs)
    )

    grouped_df_bubble['Profit Ratio'] = ((grouped_df_bubble['Profit'] / grouped_df_bubble['Sales']) * 100).round(2)

    grouped_df_timeline = (
        filtered_df
        .groupby('Period', as_index=False)
        .agg(agg_funcs)
    )

    grouped_df_timeline['Profit Ratio'] = ((grouped_df_timeline['Profit'] / grouped_df_timeline['Sales']) * 100).round(2)

    line_cols = [col for col in [x_axis, y_axis] if col not in ['Profit', 'Sales', 'Quantity', 'Returns']]
    timeline_fig = px.line(grouped_df_timeline, x='Period', y=[grouped_df_timeline[col] for col in line_cols],
                  title='Timeline Graph')

    # Add bar traces for 'Profit', 'Sales', 'Quantity', and 'Returns' if selected
    bar_columns = ['Profit', 'Sales', 'Quantity', 'Returns']
    for col in bar_columns:
        if col in [x_axis, y_axis]:
            timeline_fig.add_trace(go.Bar(x=grouped_df_timeline['Period'], y=grouped_df_timeline[col], name=col))

    # Update traces to show markers+lines
    line_traces = [trace for trace in timeline_fig.data if trace.type == 'scatter']
    for trace in line_traces:
        trace.update(mode='markers+lines')



    # Create the bubble chart figure
    bubble_fig = px.scatter(grouped_df_bubble, x=x_axis, y=y_axis, size='Quantity', color= grouped_df_bubble[breakdown].apply(lambda x: x[:15] + '...' if len(x) > 15 else x), hover_name=breakdown, title='Bubble Chart')



    timeline_fig.update_layout(
        yaxis=dict(
            range=[(min(grouped_df_timeline[y_axis].dropna()) * 0.9) if grouped_df_timeline[y_axis].dropna().min() < 0 else 0,
                   None],
            title=y_axis
        )
    )

    timeline_fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    if breakdown not in ["Customer Name", "Product Name", "Sub-Category"]:
        bubble_fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))





    return timeline_fig, bubble_fig


