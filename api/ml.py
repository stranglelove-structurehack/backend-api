import pandas as pd
import numpy as np
import pgeocode
import math
from sklearn.cluster import AgglomerativeClustering
import pickle
import matplotlib.pyplot as plt


data = pd.read_csv('data/data_small.csv').drop('Unnamed: 0', axis=1)
retail_outlets = pd.read_csv('data/points.csv').fillna(0)
products = pd.read_csv('data/products.csv')
nomi = pgeocode.Nominatim('ru')


def agg_by_gtin(gtin):
    '''Сводная таблица по регионам, в которых продается товар gtin, пока не используется, но может потом пригодиться'''
    return pd.pivot_table(data[data['gtin'] == gtin], index=['region_code', 'id_sp_'], aggfunc=np.sum)


def adresses_in_region(region_code, gtin):
    '''Возвращает список координат точек в регионе, где продается товар gtin'''
    # adresses = []
    # t = data[data['region_code'] == region_code][data['gtin'] == gtin]
    # t.head()
    # for outlet in data['id_sp_'].unique():
    #     postal = retail_outlets[retail_outlets['id_sp_'] == outlet]['postal_code']
    #     if list(postal)[0]:
    #         adr = nomi.query_postal_code(int(postal))
    #         if not(math.isnan(adr['latitude']) or math.isnan(adr['longitude'])):
    #             adresses.append([adr['latitude'], adr['longitude']])

    with open(f'data/Region_{region_code}.pkl', 'rb') as f:
       adresses = pickle.load(f)
       return list(map(lambda x: [x[0], x[1], x[2]], list(filter(lambda x: gtin in x[3], adresses))))

def clustering_adresses(adresses, n_classes):
    '''Кластеризует торговые точки на n_classes кластеров, возвращает массив,
    где каждый элемент состоит из широты, долготы и класса, к которому eгo отнесла кластеризцуия'''
    points = np.array(list(map(lambda x: [x[0], x[1]], adresses)))
    clustering = AgglomerativeClustering(n_clusters=n_classes).fit(points)
    return np.c_[adresses, clustering.labels_]

def get_stat(adresses, cluster, short_name):
    a = list(products[products['product_short_name'] == short_name]['gtin'])
    t_adresses = list(filter(lambda x: int(x[3]) == cluster, adresses))
    res = []
    for i, adr in enumerate(t_adresses):
        df = data[data['id_sp_'] == adr[2]]
        for j in range(df.shape[0]):
            if list(df['gtin'])[j] in a:
                res.append([list(df['dt'])[j], list(df['price'])[j]])
    return res

def draw_graph(res):
    t = list(filter(lambda x: x[1] != 0, res))
    df = pd.DataFrame(t, columns=['Date', 'price'])
    df['Date'] = df['Date'].astype("datetime64")
    df = df.groupby(by=['Date']).mean()
    df = df.sort_index()
    plt.plot(df['price'])
    plt.savefig('price.png')

#user_gtin = '5A3E5F7B2D093D1D6CB3CF93BA9AC8A6' # данные, которые сервер будет получать от пользователя
#user_region_code = 1
#user_n_classes = 7


def get_stat(cluster, short_name, GLOBAL_ADRESSES):
    a = list(products[products['product_short_name'] == short_name]['gtin'])
    t_adresses = list(filter(lambda x: int(x[3]) == cluster, GLOBAL_ADRESSES))
    res = []
    for i, adr in enumerate(t_adresses):
        df = data[data['id_sp_'] == adr[2]]
        for j in range(df.shape[0]):
            if list(df['gtin'])[j] in a:
                res.append([list(df['dt'])[j], list(df['price'])[j]])
    return res


def draw_graph(res):
    t = list(filter(lambda x: x[1] != 0, res))
    df = pd.DataFrame(t, columns=['Date', 'price'])
    df['Date'] = df['Date'].astype("datetime64")
    df = df.groupby(by=['Date']).mean()
    df = df.sort_index()
    plt.plot(df['price'])
    plt.savefig('price.png')


'ml/get_info_from_user'     # 1. user_product_name; user_region_code;
'ml/get_stat_picture'               # 2.


def get_info_from_user(user_product_name: str, user_region_code: int, user_n_classes: int):

    adresses = adresses_in_region(user_region_code, user_product_name)

    if len(adresses) > 0:
        GLOBAL_ADRESSES = clustering_adresses(adresses, user_n_classes) # готовый список для отрисовки точек по кластерам на карте
        return GLOBAL_ADRESSES.tolist(), GLOBAL_ADRESSES

    return []


def get_stat_picture(user_number_of_cluster: int, user_product_name: str, GLOBAL_ADRESSES: str):
    res = get_stat(user_number_of_cluster, user_product_name, GLOBAL_ADRESSES)
    draw_graph(res)


# 'ml/get_info_from_user' (user_gtin, user_region_code, user_n_classes) -> Array[a] 