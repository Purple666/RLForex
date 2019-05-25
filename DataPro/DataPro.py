import numpy as np
import pandas as pd
import glob
import os


def rename():
    count = 0
    for filename in glob.glob("fulldata/*.csv"):
        tmp = pd.read_csv(filename, error_bad_lines = False)
        if tmp.shape[0] != 0:
            mm = str(tmp.time[[0]].values[0])[0:2]
            dd = str(tmp.time[[0]].values[0])[3:5]
            newname = 'fulldata/renamed/' + filename[9:28] + mm + dd + '.csv'
            tmp.to_csv(newname,index=False)
            os.remove(filename)
        count += 1
        if count % 50 == 0:
            print("changing file #:",count)
    print(count, "files in total")

def gen_list():
    memory = []
    for filename in glob.glob("fulldata/renamed/*.csv"):
        memory.append(filename)
    date = list(set([elem[-8:-4]for elem in memory]))
    cur = list(set([elem[29:35]for elem in memory]))
    return cur, date

def combine_lp(cur_list,date_list,lp_list = ['LP-1','LP-2','LP-3','LP-4','LP-5']):
    col_names = list(pd.read_csv('fulldata/renamed/LP-1-STRM-1-AUDUSD-0201.csv').columns.values)
    base = 'fulldata/renamed/'
    for date in date_list:
        total = None
        for cur in cur_list:
            current = pd.DataFrame(columns = col_names)
            for lp in lp_list:
                filename = base + lp + '-STRM-' +lp[-1] + '-' + cur + '-' + date + '.csv'
                if os.path.exists(filename):
                    tmp = pd.read_csv(filename)
                    tmp['timestamp'] = tmp['time'].astype(str).str[:-4]
                    tmp = tmp.drop_duplicates(['timestamp'], 'last')
                    current = current.append(tmp)
            if total is not None:
                total = total.append(current)
            else:
                total = current
        bid_best = total
        ask_best = total
        bid_best['_ind'] = bid_best['timestamp'] + "+" + bid_best['currency pair']
        ask_best['_ind'] = ask_best['timestamp'] + "+" + ask_best['currency pair']
        bid_best['bid price'] = pd.to_numeric(bid_best['bid price'], errors = 'coerce')
        bid_best['ask price'] = pd.to_numeric(bid_best['ask price'], errors = 'coerce')

        bid_best = bid_best.sort_values(by=['bid price'], ascending=True)
        bid_best = bid_best.drop_duplicates(['_ind'], 'last')
        ask_best = ask_best.sort_values(by=['ask price'], ascending=False)
        ask_best = ask_best.drop_duplicates(['_ind'], 'last')
        bid_best = bid_best.rename(index=str, columns={'provider':'bid provider'})
        bid_best = bid_best.drop(columns=['stream','time', 'ask price','ask volume','guid','tier','status','quote type','currency pair'])
        ask_best = ask_best.rename(index=str, columns={'provider':'ask provider'})
        ask_best = ask_best.drop(columns=['stream', 'time', 'bid price','bid volume','guid','tier','status','quote type','timestamp'])
        best = bid_best.set_index('_ind').join(ask_best.set_index('_ind')).reset_index(drop=True)
        best = best.sort_values(by=['currency pair', 'timestamp'], ascending=True)
        best = best[best['bid price'] != 0]
        best = best[best['ask price'] != 0]
        best = best.dropna()
        newname = 'fulldata/best/' + 'best-' + date + '.csv'
        best.to_csv(newname,index=False)

def pad_data():
    for filename in glob.glob("fulldata/best/*.csv"):
        tmp = pd.read_csv(filename, error_bad_lines = False)
        tmp['pad'] = [0]*len(tmp['bid provider'])
        pad_col = ['currency pair','timestamp']
        time = tmp['timestamp'].unique()
        pad = pd.DataFrame(columns = pad_col)
        for cur in tmp['currency pair'].unique():
            mycur = pd.DataFrame(columns = pad_col)
            mycur['currency pair'] = [cur]*len(time)
            mycur['timestamp'] = time
            pad = pad.append(mycur, ignore_index=True)
        tmp['_ind'] = tmp['timestamp'] + "+" + tmp['currency pair']
        pad['_ind'] = pad['timestamp'] + "+" + pad['currency pair']
        tmp = tmp.drop(columns=['timestamp','currency pair'])
        pad = pad.set_index('_ind').join(tmp.set_index('_ind')).reset_index(drop=True)
        pad[['pad']] = pad[['pad']].fillna(value=1)
        pad = pad.fillna(method='pad')
        new_name = 'fulldata/pad/pad'+filename[18:]
        pad.to_csv(new_name,index=False)


if __name__ == '__main__':
    # rename()
    # cur, date = gen_list()
    # combine_lp(cur,date)
    pad_data()
