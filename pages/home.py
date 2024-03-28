import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_mantine_components as dmc
import math
# Load the data

# Read all three sheets

dash.register_page(__name__, path='/')

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

# Calculate 'Profit per Customer'
customer_profits = df.groupby('Customer ID')['Profit'].sum()
num_customers = df['Customer ID'].nunique()
profit_per_customer = customer_profits.sum() / num_customers

# Calculate 'Profit per Order'
order_profits = df.groupby('Order ID')['Profit'].sum()
num_orders = df['Order ID'].nunique()
profit_per_order = order_profits.sum() / num_orders

# Calculate Returns
mask = (df['Returned'] == 'Yes') & (~df.duplicated(subset=['Order ID'], keep='first'))
df.loc[mask, 'Returns'] = 1
df['Returns'].fillna(0, inplace=True)

# Group the data by 'State' and sum the 'Sales'
# sales_by_state = df.groupby('State')['Sales'].sum().reset_index()


# fig = px.choropleth(sales_by_state,
#                     locations='State',
#                     locationmode='USA-states',
#                     color='Sales',
#                     scope='usa',
#                     color_continuous_scale='Plasma')

# Update the layout
# fig.update_layout(title='Sales by State',
#                   geo=dict(scope='usa',
#                            showlakes=True,
#                            lakecolor='rgb(255, 255, 255)'))


# Calculate top 10 profitable products
profitable_products = df.groupby('Product Name')['Profit'].sum().reset_index()
loss_products = profitable_products.sort_values(by="Profit", ascending=True).head(10)
profitable_products = profitable_products.sort_values(by="Profit", ascending=False).head(10)
# Calculate total profit/loss for each product

max_chars = 15
profitable_products['Product Name shorten'] = profitable_products['Product Name'].apply(lambda x: x[:max_chars] + "..." if len(x) > max_chars else x)
loss_products['Product Name shorten'] = loss_products['Product Name'].apply(lambda x: x[:max_chars] + "..." if len(x) > max_chars else x)

# Create the bar chart
profitable_products_fig = go.Figure()
profitable_products_fig.add_trace(go.Bar(
    y=profitable_products['Product Name shorten'],  # Adjust this according to your column name
    x=profitable_products['Profit'],  # Adjust this according to your column name
    orientation='h',
    marker=dict(
        color='#023020'
    )
))

loss_products_fig = go.Figure()
loss_products_fig.add_trace(go.Bar(
    y=loss_products['Product Name shorten'],  # Adjust this according to your column name
    x=loss_products['Profit'],  # Adjust this according to your column name
    orientation='h',
    marker=dict(
        color='#8B0000'
    )
))

# Update y-axis to use truncated labels
profitable_products_fig.update_layout(
    title='Top 10 Most Profitable Products',
    yaxis=dict(
        tickvals=profitable_products['Product Name shorten'],  # Use product names as tick values
        ticktext=profitable_products['Product Name shorten'],  # Use truncated product names as tick labels
        autorange="reversed"  # Reverse the y-axis
    )
)

loss_products_fig.update_layout(
    title='Top 10 Most Loss-making Products',
    yaxis=dict(
        tickvals=loss_products['Product Name shorten'],  # Use product names as tick values
        ticktext=loss_products['Product Name shorten'],  # Use truncated product names as tick labels
        autorange="reversed"  # Reverse the y-axis
    )
)

# Calculate total profit by region
profit_by_region = df.groupby('Region')['Profit'].sum().reset_index()

# Create a pie chart
profit_by_region_fig = px.pie(profit_by_region, values='Profit', names='Region', title='Profit by Region')
# Define the layout

metrics = [
    {"name": "Total Sales", "value": (df['Sales'].sum() / 1000000).round(2), "suffix": "M"},
    {"name": "Total Quantity", "value": (df['Quantity'].sum() / 1000).round(2), "suffix": "K"},
    {"name": "Avg. Delivery Days", "value": math.floor(df['Days to Ship'].mean())},
    {"name": "Return Orders", "value": int(df['Returns'].sum())},
    {"name": "Profit", "value": (df['Profit'].sum() / 1000).round(2), "suffix": "K"},
    {"name": "Profit Ratio", "value": ((df['Profit'].sum() / df['Sales'].sum()) * 100).round(2), "suffix": "%"},
    {"name": "Profit per Order", "value": profit_per_order.round(2), "suffix": "$"},
    {"name": "Profit per Customer", "value": profit_per_customer.round(2), "suffix": "$"}
]

metrics_grid_children = []
for metric in metrics:
    metrics_grid_children.append(
        dmc.Col(
            span=6,
            children=[
                dmc.Paper(
                    shadow="md",
                    style={"background-color": "#F3F2EE", "border-radius": "16px"},
                    p="md",
                    children=[
                        html.Div([
                            html.Div([
                                metric["name"]
                            ], style={"font-size": "24px", "font-weight": "400", "white-space": "nowrap"}),
                            html.Div([
                                str(metric["value"]) + f' {metric["suffix"]}' if "suffix" in metric else str(metric["value"])
                            ], style={"font-size": "40px", "font-weight": "600", "white-space": "nowrap"})
                        ], style={"display": "flex", "align-items": "center", "justify-content": "center", "flex-direction": "column", "min-width": "100px"}
                        )
                    ]
                )
            ]
        )
    )


layout = dmc.MantineProvider(
    theme={"primaryColor": ""},
    children=[
        dmc.Grid(
            children=[
                dmc.Col(
                    span=6,
                    children=[
                        dmc.Paper(
                            shadow="md",
                            style={"background-color": "#F3F2EE", "border-radius": "16px"},
                            p="md",
                            children=[
                                html.Div([
                                    html.A([
                                        "Go to data table page"
                                    ], href="/data-table", style={"font-size": "24px", "font-weight": "400", "white-space": "nowrap"}),
                                ], style={"display": "flex", "align-items": "center", "justify-content": "center", "flex-direction": "column", "min-width": "100px"}
                                )
                            ]
                        )
                    ],
                ),
                dmc.Col(
                    span=6,
                    children=[

                        dmc.Paper(
                            shadow="md",
                            style={"background-color": "#F3F2EE", "border-radius": "16px"},
                            p="md",
                            children=[
                                html.Div([
                                    html.A([
                                        "Go to graph page"
                                    ], href="/graph", style={"font-size": "24px", "font-weight": "400", "white-space": "nowrap"}),
                                ], style={"display": "flex", "align-items": "center", "justify-content": "center",
                                          "flex-direction": "column", "min-width": "100px"}
                                )
                            ]
                        )
                    ],
                ),
                dmc.Col(
                    span=6,
                    children=[
                        dmc.Grid(
                            children=metrics_grid_children
                        ),
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
                                    figure=profit_by_region_fig
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
                                    figure=profitable_products_fig
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
                                    figure=loss_products_fig
                                )
                            ],
                        )
                    ],
                ),
            ]
        )
    ],
)

