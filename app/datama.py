from app import fetcher

import pandas as pd
import numpy as np
import sqlite3
import urllib
import json

DB_PATH = 'db.sqlite'

def retrieve(table_name, query="*"):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("select "+query+" from "+table_name+" ;", conn)
    df['price'] = df.apply(get_current_price,axis=1,data=data)
    df['status'] = df.apply(check_band,axis=1)
    df = df[df['status'] != 'between']
    df['id'] = df.apply(get_symbol,axis=1,data=data)
    df['ns'] = (df['price']-df['m'])/(df['s'])
    df.drop(['index','window','v','last_update','status','s','lt','ut'], axis=1, inplace=True)
    df.sort_values(by=['ns'],inplace=True)

    df['m'] = df['m'].map(lambda x: '{0:.3}'.format(x))
    #df['s'] = df['s'].map(lambda x: '{0:.3}'.format(x))
    #df['lt'] = df['lt'].map(lambda x: '{0:.3}'.format(x))
    #df['ut'] = df['ut'].map(lambda x: '{0:.3}'.format(x))
    df['price'] = df['price'].map(lambda x: '{0:.3}'.format(x))
    df['ns'] = df['ns'].map(lambda x: '{0:.3}'.format(x))
    #print(df)
    send_alert(df)
    conn.close()

def update():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # scrape
    # corpus,header,source = fetcher.scrape()
    time,title,source,content = fetcher.scrape()

    c.execute("select * from "+TABLE_NAME+" ;")
    c.execute("insert into articles (time, title, source, content) "+
        "values ("++");")

    # scrape
    corpus,header,source = fetcher.scrape()

    df = pd.read_sql_query("select * from "+TABLE_NAME+" ;", conn)
    df = df.apply(update_band,axis=1)
    #XXX somehow index gets duplicated and causes trouble
    df.drop('index', axis=1, inplace=True)
    #print(df)
    df.to_sql(TABLE_NAME,conn,if_exists='replace')
    conn.commit()
    conn.close()

if __name__ == '__main__':