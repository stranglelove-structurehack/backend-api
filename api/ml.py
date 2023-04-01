import pandas as pd
import numpy as np
import pgeocode
import math
from sklearn.cluster import AgglomerativeClustering


data = pd.read_csv('data/data_small.csv').drop('Unnamed: 0', axis=1)
retail_outlets = pd.read_csv('data/points.csv').fillna(0)
nomi = pgeocode.Nominatim('ru')


def agg_by_gtin(gtin):
    '''Сводная таблица по регионам, в которых продается товар gtin, пока не используется, но может потом пригодиться'''
    return pd.pivot_table(data[data['gtin'] == gtin], index=['region_code', 'id_sp_'], aggfunc=np.sum)

def adresses_in_region(region_code, gtin):
    '''Возвращает список координат точек в регионе, где продается товар gtin'''
    adresses = []
    t = data[data['region_code'] == region_code][data['gtin'] == gtin]
    t.head()
    for outlet in data['id_sp_'].unique():
        postal = retail_outlets[retail_outlets['id_sp_'] == outlet]['postal_code']
        if list(postal)[0]:
            adr = nomi.query_postal_code(int(postal))
            if not(math.isnan(adr['latitude']) or math.isnan(adr['longitude'])):
                adresses.append([adr['latitude'], adr['longitude']])
    return adresses

def clustering_adresses(adresses, n_classes):
    '''Кластеризует торговые точки на n_classes кластеров, возвращает массив,
    где каждый элемент состоит из широты, долготы и класса, к которому его отнесла кластеризцуия'''
    points = np.array(adresses)
    clustering = AgglomerativeClustering(n_clusters=n_classes).fit(points)
    return np.c_[adresses, clustering.labels_]


#user_gtin = '5A3E5F7B2D093D1D6CB3CF93BA9AC8A6' # данные, которые сервер будет получать от пользователя
#user_region_code = 1
#user_n_classes = 7

def get_info_from_user(user_gtin, user_region_code, user_n_classes):
    adresses = adresses_in_region(user_region_code, user_gtin)
    a = clustering_adresses(adresses, user_n_classes) # готовый список для отрисовки точек по кластерам на карте
    return a.tolist()

# 'ml/get_info_from_user' (user_gtin, user_region_code, user_n_classes) -> Array[a] 