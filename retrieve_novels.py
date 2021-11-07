import time
import re
from urllib import request
from bs4 import BeautifulSoup
import pandas as pd
import argparse 
import os
import tqdm


def retrieve_text(ncode,pbar):
    # 全部分数を取得
    while True:
        try:
            info_url = "https://ncode.syosetu.com/novelview/infotop/ncode/{}/".format(ncode)
            info_res = request.urlopen(info_url)
            soup = BeautifulSoup(info_res, "html.parser")
            pre_info = soup.select_one("#pre_info").text
            num_parts = int(re.search(r"全([0-9]+)部分", pre_info).group(1))
            break
        except:
            pbar.set_description('Error occured while requesting', url)
            time.sleep(1)

    for part in range(1, num_parts+1):
        # 作品本文ページのURL
        url = "https://ncode.syosetu.com/{}/{:d}/".format(ncode, part)

        while True:
            try:
                res = request.urlopen(url)
                break
            except:
                pbar.set_description('Error occured while requesting', url)
                time.sleep(1)
        soup = BeautifulSoup(res, "html.parser")

        # CSSセレクタで本文を指定
        honbun = soup.select_one("#novel_honbun").text
        honbun += "\n"  # 次の部分との間は念のため改行しておく
        
        pbar.set_description("part {:d} downloaded (total: {:d} parts)".format(part, num_parts))  # 進捗を表示

        time.sleep(1)  # 次の部分取得までは1秒間の時間を空ける
    return honbun

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('list',type=str)
    parser.add_argument('min_point',type=int)
    os.makedirs('data/',exist_ok=True)
    args = parser.parse_args()
    df = pd.read_excel(args.list)
    df = df[df['global_point'] > args.min_point]
    pbar = tqdm.tqdm(df.iterrows())
    for idx, row in pbar:
        honbun = retrieve_text(row['ncode'].lower(),pbar)
        with open(os.path.join('data',row['ncode']+'.txt'), mode='w') as f:
            f.write(honbun)