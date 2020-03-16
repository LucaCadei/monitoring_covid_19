# -*- coding: utf-8 -*-
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from urllib.request import urlopen


from data_utils import *

#Download and read data from ../data
#Download only if current time >= 18:15

estensione = ['nazionale', 'regioni', 'province']

if download_go():
    for est in estensione:
        download_dati(est)


#Definisco la variabile globale current date per lo scaricamento e l'indicazione
#dell'aggiornamento dei dati
today = date.today()

now = datetime.now()

treshold_hour = datetime(year=now.year, month=now.month, day=now.day, hour=18, minute=15)

if now >= treshold_hour:
    current_date = today
else:
    current_date = date.today() - timedelta(days=1)

#Rendo il datetime stringa per metterlo nell'uel di scaricamento
current_date_str = current_date.strftime('%Y%m%d')

if current_date != date.today() - timedelta(days=1):
    for est in estensione:
        download_dati_giornalieri(current_date_str, est)

#Caricamento di tutti i dati in memoria
nazionale = pd.read_csv('../data/dati_andamento_nazionale.csv', sep=';', index_col=0, parse_dates=['data'], dtype={'codice_regione':'int'})
regioni = pd.read_csv('../data/dati_andamento_regioni.csv', sep=';', index_col=0, parse_dates=['data'], dtype={'codice_regione':'int'})
province = pd.read_csv('../data/dati_andamento_province.csv', sep=';', index_col=0, parse_dates=['data'], dtype={'codice_regione':'int'})

nazionale_odierno = pd.read_csv('../data/giornaliero/nazionale/dati_andamento_nazionale_{}.csv'.format(current_date_str), sep=';', index_col=0, parse_dates=['data'], dtype={'codice_regione':'int'})
regioni_odierno = pd.read_csv('../data/giornaliero/regioni/dati_andamento_regioni_{}.csv'.format(current_date_str), sep=';', index_col=0, parse_dates=['data'], dtype={'codice_regione':'int'})
province_odierno = pd.read_csv('../data/giornaliero/province/dati_andamento_province_{}.csv'.format(current_date_str), sep=';', index_col=0, parse_dates=['data'], dtype={'codice_regione':'int'})

#.geojson
with urlopen(urls_geografici['dati_geografici_regioni']) as response:
    regioni_geojson = json.load(response)


#Creazione dei dataframe ausiliari per il plot
contagi_per_regione = regioni_odierno[['codice_regione', 'totale_attualmente_positivi']].groupby(by=['codice_regione'], as_index=False)['totale_attualmente_positivi'].sum()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


storico_nazionale_contagi = go.Scatter(x = nazionale['data'], y = nazionale['totale_attualmente_positivi'],
                            name = 'storico nazionale contagi',
                            line = dict(width = 2,
                                color = 'rgb(229, 151, 50)'))

layout_totali = go.Layout(title = 'Contagi totali', hovermode = 'closest', width=800, height=300)
fig_nazionale_totale_contagi = go.Figure(data = [storico_nazionale_contagi], layout = layout_totali)



storico_nazionale_nuovi_contagi = go.Scatter(x = nazionale['data'], y = nazionale['nuovi_attualmente_positivi'],
                            name = 'storico nazionale nuovi contagi',
                            line = dict(width = 2,
                                color = 'rgb(229, 151, 50)'))

layout = go.Layout(title = 'Nuovi contagi', hovermode = 'closest', width=800, height=300)
fig_nazionale_nuovi_contagi = go.Figure(data = [storico_nazionale_nuovi_contagi], layout = layout)

storico_deceduti = go.Scatter(x = nazionale['data'], y = nazionale['deceduti'],
                            name = 'storico deceduti',
                            line = dict(width = 2,
                                color = 'rgb(229, 151, 50)'))

layout = go.Layout(title = 'Deceduti totali', hovermode = 'closest', width=800, height=300)
fig_deceduti = go.Figure(data = [storico_deceduti], layout = layout)



fig_naz = px.choropleth_mapbox(contagi_per_regione, geojson=regioni_geojson, featureidkey='properties.reg_istat_code_num',  locations='codice_regione', color='totale_attualmente_positivi',
                           color_continuous_scale=px.colors.sequential.OrRd,
                           range_color=(0, 20000),
                           mapbox_style="carto-positron",
                           zoom=5, center = {"lat": 41.29246, "lon": 12.5736108},
                           opacity=0.8,
                           labels={'totale_attualmente_positivi':'Positivi'},
                           width=770, height=900
                          )



#energy_data = go.Scatter(x=energy_series.index, y=energy_series.values)


#MODIFICARE TUTTO QUESTO CON LE CALLBACK
app.layout = html.Div(children=[
    html.Div(children=[
    html.H1(children='Cruscotto monitoraggio COVID-19', style={'float':'left'})],
         style={'clear':'both'}),
    html.Div(children=[
    html.Span(
        id='contagiati',
        children = 'Contagiati totali: {}'.format(nazionale_odierno['totale_attualmente_positivi'][0]),
        style={'float':'left', 'clear':'both'}),
    html.Span(
        id='tamponi',
        children = 'Tamponi effettuati: {}'.format(nazionale_odierno['tamponi'][0]),
        style={'float':'left', 'clear':'both'}),
    html.Span(
        id='morti',
        children = 'Deceduti totali: {}'.format(nazionale_odierno['deceduti'][0]),
        style={'float':'left', 'clear':'both'}),
    html.Span(
        id='guariti',
        children = 'Guariti totali: {}'.format(nazionale_odierno['dimessi_guariti'][0]),
        style={'float':'left', 'clear':'both'}),
    dcc.Graph(
        id='mappa_nazionale',
        figure = fig_naz,
        style={'float':'right'})
    ]),
    html.Div(children=[
    dcc.Graph(
        id='contagi_nazionale_nuovi',
        figure = fig_nazionale_nuovi_contagi,
        style={'padding':0, 'margin':0}),
    dcc.Graph(
        id='contagi_nazionale_totale',
        figure = fig_nazionale_totale_contagi,
        style={'padding':0, 'margin':0}),
    dcc.Graph(
        id='deceduti',
        figure = fig_deceduti,
        style={'padding':0, 'margin':0})
    ], style={'float':'left', 'padding':0, 'margin':0})
])




if __name__ == '__main__':
    app.run_server(debug=True)
