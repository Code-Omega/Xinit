import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict, OrderedDict

from sklearn import preprocessing
from sklearn.cluster import SpectralClustering, Birch
from sklearn.linear_model import Ridge, ElasticNet, LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

import pickle

def daily_cluster():
    tickers = pickle.load(open('tickers_snp.pkl','rb'))
    data = pickle.load(open('2019-01-28_snp.pkl','rb'))

    dmin = data.min()
    dmax = data.max()
    data_norm = (data - dmin)/(dmax - dmin)

    X = np.arange(len(data_norm))
    X = X[:,np.newaxis]

    poly_features = []
    degree = 7

    for i in range(len(tickers)): #len(tickers)
        y = data_norm[data_norm.columns[i]].values
        mask = ~np.isnan(y)
        model = make_pipeline(PolynomialFeatures(degree), Ridge())
        model.fit(X[mask], y[mask])
        #print(model.__dict__)
        ticker_features = model.steps[1][1].coef_
        ticker_features[0] = model.steps[1][1].intercept_
        poly_features.append(ticker_features)
    poly_features = np.array(poly_features)

    n_clusters = 3

    clustering = SpectralClustering(n_clusters=n_clusters,
            assign_labels="kmeans").fit(poly_features)
    #clustering.labels_

    sc = defaultdict(list)
    for i in range(len(clustering.labels_)):
        sc[clustering.labels_[i]].append(i)

    cluster_features = []
    for c in sc:
        average_features = poly_features[sc[c]].mean(axis=0)
        #average_features = np.median(poly_features[sc[c]],axis=0)
        cluster_features.append(average_features)
    cf = cluster_features

    cfx = np.arange(len(data_norm))
    #cfx_lbl = pd.to_datetime(data_norm.index).tolist()
    cfx_lbl = data_norm.index.tolist()
    cfy = []
    for i in range(len(cf)):
        curve = np.ones(len(data_norm))*cf[i][0]
        for d in range(1,degree+1):
            curve += cfx**d*cf[i][d]
        cfy.append(curve)

    for i in range(len(cf)):
        plt.plot(cfx,cfy[i], label = i)
        plt.xticks(cfx[::50],cfx_lbl[::50])
        plt.title('Average performance per cluster')
        plt.legend()
        ########################################################### PLOT

    for c in sc:
        data_norm[data_norm.columns[sc[c]]].mean(axis=1).plot()
        plt.legend()
        ########################################################### PLOT

    acddf = pickle.load(open('comp-data_snp.pkl','rb'))

    cluster_dists = []
    for c in sc:
        cluster_dists.append(acddf[acddf.columns[sc[c]]].loc['sector'].value_counts()/acddf.loc['sector'].value_counts())
        #cluster_dists.append((snp500_list.iloc[sc[c]]['GICS Sector'].value_counts()/snp500_list['GICS Sector'].value_counts()).fillna(0))

    fig, axes = plt.subplots(ncols=len(sc),figsize=(15,6))

    for c in sc:
        cluster_dists[c].plot('bar',ylim=(0,1),ax=axes[c],title='cluster {}'.format(c))
        ########################################################### PLOT
