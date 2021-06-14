import logging
import os

import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_table
from flask import Flask
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


logger = logging.getLogger()
logger.setLevel(logging.INFO)

server = Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

SQL_HOST=os.getenv("SQL_HOST")
SQL_PASSWORD=os.getenv("SQL_PASSWORD")
SQL_USER=os.getenv("SQL_USER")
SQL_DATABASE=os.getenv("SQL_DATABASE")



def get_table(table_name):                                                                                                 
    logging.info(f'Get table {table_name}')
    logging.info(f'Connecting to DB...')
    conn = psycopg2.connect(database=SQL_DATABASE,
                            user=SQL_USER, 
                            password=SQL_PASSWORD,
                            host=SQL_HOST,
                            port= '5432'
                            )
    cursor = conn.cursor()  
    cursor.execute(f"select * from {table_name}")
    records = cursor.fetchall()
    conn.commit()
    conn.close() 
    return records   

data =  get_table('NAMES_ARCHIVE_POLAND')   
df = pd.DataFrame(data, columns=['year', 'name', 'births', 'sex'])
df['name'] = df['name'].str.strip().str.title()
df['sex'] = df['sex'].str[:1]
df = df.sort_values(by=['year', 'births'], ascending=False)
logging.info(f'{df.head()}')

df_ = df.groupby(['year', 'sex']).sum().reset_index()
df_k = df_[df_.sex == 'KOBIETA']
df_m = df_[df_.sex == 'MĘŻCZYZNA']
figa = px.scatter(df_k, x="year", y="births", title='Łączna liczba urodzeń w latach')
figa.add_trace(go.Scatter(y=df_m['births'].values, 
                                    x=df_m['year'].values,
                                    mode='lines+markers',
                                    name='name'
                                    ))



app.layout = html.Div(children=[
    html.H1('Imiona nadane w XXI wieku w Polsce', style={'textAlign': 'center',}),
    dcc.Dropdown(
        id='names-input',
        style={'textAlign': 'center', 'width': '70%', 'margin': '0 15%' },
        options=[{'label': name, 'value': name} for name in df['name'].unique()],
        value=['Julia', 'Zuzanna'],
        multi=True,
        placeholder='Wybierz...'),


    dcc.Graph(id='graph',),
    html.Hr(),
    html.H1('Tabela z danymi', style={'textAlign': 'center',}),
    html.Div(children=[
        html.P('=2017 w kolumnie rok wyświetli dane tylko z 2017 roku', style={'textAlign': 'center',}
            , className="one-third column"),
        html.P('>=7 w kolumnie liczba wyświetli tylko wystąpienia większe lub równe 7', style={'textAlign': 'center',}
            , className="one-third column"),
        html.P('K w kolumnie płeć wyświetli tylko żeńskie imiona', style={'textAlign': 'center',}
            , className="one-third column"),
        html.P('M w kolumnie płeć wyświetli tylko męskie imiona', style={'textAlign': 'center',}
            , className="one-third column"),
        ], className="row"),
    dash_table.DataTable(
                    sort_action='native',
                    filter_action='native',
                    page_action='native',
                    page_size= 50,
                    id='table',
                    columns=[{"name": z, "id": i} for i, z in zip(df.columns, ('rok', 'imię', 'liczba', 'płeć'))],
                    data=df.to_dict('records'),
                    ),
    html.Hr(),
    html.Span(["**Dane pochodzą z ",
            html.A('dane.gov.pl/dataset/219,imiona-nadawane-dzieciom-w-polsce',
                    href="https://dane.gov.pl/dataset/219,imiona-nadawane-dzieciom-w-polsce",
                    target="blank")]),
    ])


@app.callback(
    [Output(component_id='graph', component_property='figure'),],
    [Input(component_id='names-input', component_property='value'),]

)


def update(names):
    '''Get name from names-input, load data from df, update graph.'''
    name = names.pop()
    df_temp = df[df['name'] == name].drop(columns=['sex'])
    df_temp = df_temp.set_index('year').reindex(range(df.year.min(), df.year.max()+1)).reset_index().fillna('0')
    fig = go.Figure(data=go.Scatter(y=df_temp['births'].values, 
                                    x=df_temp['year'].values,
                                    mode='lines+markers',
                                    name=name
                                    ))
    fig.update_xaxes(tick0=df.year.min(), dtick=1)
    fig.update_yaxes(tick0=0)
    if names:
        title = f'Tyle razy imiona: {name}, {",".join(names)} zostały nadane jako pierwsze w latach {df.year.min()}-{df.year.max()}'
    else:
        title = f'Tyle razy imię {name} zostało nadane jako pierwsze w latach {df.year.min()}-{df.year.max()}'

    fig.update_layout(title={
                            'text': title,
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
                      hovermode='x',
                      xaxis_title = '',
                      font=dict(
                      family="Courier New, monospace",
                      size=(14-len(names)*0.33),
                      color="RebeccaPurple"),)
    for name in names:
        df_temp = df[df['name'] == name].drop(columns=['sex'])
        df_temp = df_temp.set_index('year').reindex(range(df.year.min(), df.year.max()+1)).reset_index().fillna('0')       
        fig.add_trace(go.Scatter(y=df_temp['births'].values, 
                                    x=df_temp['year'].values,
                                    mode='lines+markers',
                                    name=name
                                    ))
    return (fig,)