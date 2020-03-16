from datetime import datetime, date, timedelta
import json
import requests

import pandas as pd


urls_geografici = {'dati_geografici_regioni': 'https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson',
                   'dati_geografici_province': 'https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_provinces.geojson'}

urls_dict = {'nazionale': 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale',
             'regioni': 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni',
             'province': 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province'}



def download_go():
    #Restituisce True se l'ora attuale e >= 18:30

    download = False
    now = datetime.now()

    if now.hour >= 18 and now.minute >= 30:
        download = True

    return True


def download_dati(estensione='nazionale'):
    path = '../data/dati_andamento_{}.csv'.format(estensione)

    dati = pd.read_csv(urls_dict[estensione] + '.csv', error_bad_lines=False, encoding='utf-8')

    dati.to_csv(path, sep=';', encoding='utf-8')


def download_dati_giornalieri(date_str, estensione='nazionale'):
    path = '../data/giornaliero/{}/dati_andamento_{}_{}.csv'.format(estensione, estensione, date_str)

    dati = pd.read_csv(urls_dict[estensione] + '-' + date_str + '.csv', error_bad_lines=False, encoding='utf-8')

    dati.to_csv(path, sep=';', encoding='utf-8')
