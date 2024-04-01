import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context, callback
import pandas as pd
import dash_mantine_components as dmc
dash.register_page(__name__, name='Data Table')

# Read all three sheets
orders_df = pd.read_excel("./Sample - Superstore.xlsx", sheet_name="Orders")
returns_df = pd.read_excel("./Sample - Superstore.xlsx", sheet_name="Returns")
people_df = pd.read_excel("./Sample - Superstore.xlsx", sheet_name="People")

# Merge the Orders and Returns DataFrames
merged_df = pd.merge(orders_df, returns_df, on="Order ID", how="left")

# Merge the merged_df with the People DataFrame
df = pd.merge(merged_df, people_df, on="Region", how="left")

new_entries = []
date_columns = ['Order Date', 'Ship Date']
round_value_columns = ['Sales', 'Profit']

for col in date_columns:
    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')

for col in round_value_columns:
    df[col] = df['Sales'].round(3)

dropdown_style = {
    "font-size": ".9rem",  # Adjust the font size as needed
    "font-family": "Inter, sans-serif",
    "margin-top": "5px",
    "width": '33%'
}

layout = html.Div([
    # Dropdown filters
    html.Div([
        dmc.Text('Filter by region',
                 style={'margin-right': '10px', 'font-size': '.85rem', }),
        dcc.Dropdown(
            id='region',
            options=[{'label': region, 'value': region} for region in df['Region'].unique()],
            multi=True,
            value=[],
            style=dropdown_style,
        ),
    ], style={'margin-bottom': '20px'}),  # Add margin between dropdown and table

    html.Div([
        dmc.Text('Filter by state',
                 style={'margin-right': '10px', 'font-size': '.85rem', }),
        dcc.Dropdown(
            id='state',
            options=[{'label': state, 'value': state} for state in df['State'].unique()],
            multi=True,
            style=dropdown_style
        ),
    ], style={'margin-bottom': '20px'}),

    html.Div([
        dmc.Text('Filter by city',
                 style={'margin-right': '10px', 'font-size': '.85rem', }),
        dcc.Dropdown(
            id='city',
            options=[{'label': city, 'value': city} for city in df['City'].unique()],
            multi=True,
            style=dropdown_style
        ),
    ], style={'margin-bottom': '20px'}),

    # Dash DataTable to display the data
    dash_table.DataTable(
        id='datatable',
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        filter_action='native',
        sort_action='native',
        page_size=10,
        editable = True,
        style_cell={'textAlign': 'left'},
    ),

    # Input fields for adding new entries
    html.Div([
        dmc.Text("Add New Entry", style={'font-size': '1rem'}),
        html.Div([
            dmc.TextInput(placeholder='Order ID', id='order-id', value=''),
            dmc.TextInput(placeholder='Customer ID', id='customer-id', value=''),
            dmc.TextInput(placeholder='Product ID', id='product-id', value=''),
            dmc.NumberInput(placeholder='Sales', id='sales', value=''),
            dmc.NumberInput(placeholder='Profit', id='profit', value=''),
            dmc.Button('Add Entry', id='add-entry-btn', n_clicks=0),
            html.Div(id='duplicate-error', style={'color': 'red'})
        ], style={'margin-top': '20px', 'gap': '10px', 'display': 'flex'}),
        html.Div(id='duplicate-error', style={'color': 'red', 'margin-top': '10px'})

    ], style={'margin-top': '20px'})

])

# Callback to update State dropdown based on selected Region
@callback(
    Output('state', 'options'),
    Input('region', 'value')
)
def update_state_options(selected_regions):
    if not selected_regions:
        return []
    filtered_df = df[df['Region'].isin(selected_regions)]
    states = sorted(filtered_df["State"].unique())
    return [{'label': state, 'value': state} for state in states]


# Callback to update City dropdown based on selected State and Region
@callback(
    Output('city', 'options'),
    Input('state', 'value'),
    Input('region', 'value')
)
def update_city_options(selected_states, selected_regions):

    if not selected_regions or not selected_states:
        return []
    filtered_df = df[df['State'].isin(selected_states)]
    cities = sorted(filtered_df["City"].unique())
    return [{'label': city, 'value': city} for city in cities]


@callback(
    [Output('datatable', 'data'),
     Output('duplicate-error', 'children'),
     Output('region', 'value'),
     Output('state', 'value'),
     Output('city', 'value')],
    [Input('region', 'value'),
     Input('state', 'value'),
     Input('city', 'value'),
     Input('add-entry-btn', 'n_clicks')],
    [State('order-id', 'value'),
     State('customer-id', 'value'),
     State('product-id', 'value'),
     State('sales', 'value'),
     State('profit', 'value')]
)
def update_table_and_add_entry(region_filter, state_filter, city_filter, n_clicks, order_id, customer_id, product_id, sales, profit):
    global new_entries
    filtered_df = df.copy()  # Make a copy of the original DataFrame
    entry_df = df.copy()

    if region_filter:
        filtered_df = filtered_df[filtered_df['Region'].isin(region_filter)]
    if state_filter:
        filtered_df = filtered_df[filtered_df['State'].isin(state_filter)]
    if city_filter:
        filtered_df = filtered_df[filtered_df['City'].isin(city_filter)]

    # Check if the callback was triggered by the "Add Entry" button
    triggered_by = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_by == 'add-entry-btn' and n_clicks > 0:

        duplicate_order_row = []
        duplicate_product_row = []
        duplicate_customer_rows = []
        duplicate_customer_row = []

        if order_id in entry_df['Order ID'].values:
            duplicate_order_row = entry_df[entry_df['Order ID'] == order_id].iloc[-1]

        if product_id in entry_df['Product ID'].values:
            duplicate_product_row = entry_df[entry_df['Product ID'] == product_id].iloc[-1]

        if customer_id in entry_df['Customer ID'].values:
            if len(duplicate_order_row) == 0:
                duplicate_customer_row = entry_df[entry_df['Customer ID'] == customer_id].sort_values('Order Date').iloc[-1]
            else:
                duplicate_customer_rows = entry_df[(entry_df['Customer ID'] == customer_id) &
                                                      (entry_df['Order Date'] == duplicate_order_row.loc['Order Date'])]

                if len(duplicate_customer_rows) == 0:
                    duplicate_customer_row = entry_df[entry_df['Customer ID'] == customer_id].sort_values('Order Date').iloc[-1]
                else:
                    duplicate_customer_row = duplicate_customer_rows.iloc[-1]

        new_entry = pd.DataFrame({'Row ID': [len(df) + len(new_entries) + 1],
                                  'Order ID': [order_id],
                                  'Order Date': [duplicate_order_row['Order Date'] if len(duplicate_order_row) != 0 else None],
                                  'Ship Date': [duplicate_order_row['Ship Date'] if len(duplicate_order_row) != 0 else None],
                                  'Ship Mode': [duplicate_order_row['Ship Mode'] if len(duplicate_order_row) != 0 else None],
                                  'Customer ID': [customer_id],
                                  'Customer Name': [duplicate_customer_row['Customer Name'] if len(duplicate_customer_row) != 0 else None],
                                  'Segment': [duplicate_customer_row['Segment'] if len(duplicate_customer_row) != 0 else None],
                                  'Country': [duplicate_customer_row['Country'] if len(duplicate_customer_rows) != 0 else None],
                                  'State': [duplicate_customer_row['State'] if len(duplicate_customer_rows) != 0 else None],
                                  'City': [duplicate_customer_row['City'] if len(duplicate_customer_rows) != 0 else None],
                                  'Region': [duplicate_customer_row['Region'] if len(duplicate_customer_rows) != 0 else None],
                                  'Postal Code': [duplicate_customer_row['Postal Code'] if len(duplicate_customer_rows) != 0 else None],
                                  'Product ID': [product_id],
                                  'Category': [duplicate_product_row['Category'] if len(duplicate_product_row) != 0 else None],
                                  'Sub-Category': [duplicate_product_row['Sub-Category'] if len(duplicate_product_row) != 0 else None],
                                  'Product Name': [duplicate_product_row['Product Name'] if len(duplicate_product_row) != 0 else None],
                                  'Sales': [sales],
                                  'Profit': [profit],
                                  'Person': [duplicate_customer_row['Person'] if len(duplicate_customer_rows) != 0 else None]
                                  })

        # Check for duplicate row
        duplicate = entry_df[(entry_df['Customer ID'] == customer_id) &
                                (entry_df['Product ID'] == product_id) &
                                (entry_df['Order ID'] == order_id)]
        for entry in new_entries:
            entry_df = pd.concat([entry_df, entry], ignore_index=True)

        if len(duplicate) != 0:
            return entry_df.to_dict('records'), "Duplicate entry! Please try again with different values.", [], [], []
        else:
            # Concatenate new entry with existing data
            new_entries.append(new_entry)
            entry_df = pd.concat([entry_df, new_entry], ignore_index=True)
            return entry_df.to_dict('records'), "", [], [], []  # Clear the error message

    return filtered_df.to_dict('records'), "", region_filter, state_filter, city_filter


