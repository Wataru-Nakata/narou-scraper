# This program will retrieve the whole list of novels at syosetu.com

import bs4 
from urllib import request
from argparse import ArgumentParser
from parse import *
import time
import jsonlines

# soup = bs4.BeautifulSoup(html_doc, 'html')

def create_entry(soup):
    novels = []
    entries = soup.find_all('div',class_='searchkekka_box')
    for entry in entries:
        novel = {}
        links = entry.find_all('a')
        title = links[0].get_text()
        url = links[0]['href']
        author = links[1].get_text()
        author_url = links[1]['href']
        table = entry.find_all('td')[1].text.strip().replace("\n", " ")
        # print(table)
        result = parse("{}ジャンル：{}キーワード：{}最終更新日：{}読了時間：{}週別ユニークユーザ：{}レビュー数：{}総合ポイント：{}ブックマーク：{}評価人数：{}評価ポイント：{}",table)
        if result is None:
            print(parse("{}ジャンル：{}キーワード：{}最終更新日：{}読了時間：{}週別ユニークユーザ：{}",table))
            raise ValueError
        novel["description"] = result[0].strip()
        novel["genre"] = result[1].strip()
        novel["keywords"] = result[2].strip()
        novel["lastUpdated"] = result[3].strip()
        novel["time2read"] = result[4].strip()
        novel["weeklyUser"] = result[5].strip()
        novel["reviews"] = result[6].strip()
        novel["points"] = result[7].strip()
        novel["bookmarks"] = result[8].strip()
        novel["reviewers"] = result[9].strip()
        novel["reviewPoint"] = result[10].strip()
        novels.append(novel)
    return novels

def get_next_url(soup):
    try :
        return soup.find('a', class_='nextlink')['href']
    except:
        return None


if __name__ == '__main__':
    novels = []
    parser = ArgumentParser(description='scrape syosetu.com and create list of novels entries')
    parser.add_argument('search-page-url', type=str, help='search opage url')
    response = request.urlopen(url='https://yomou.syosetu.com/search.php?word=&notword=&genre=&type=&mintime=&maxtime=&minlen=&maxlen=&min_globalpoint=100&max_globalpoint=&minlastup=&maxlastup=&minfirstup=&maxfirstup=&order=new')
    soup = bs4.BeautifulSoup(response,features='html.parser')
    response.close()
    novels.extend(create_entry(soup))
    while True:
        url = get_next_url(soup)
        if url is None:
            break
        time.sleep(1)
        response = request.urlopen(url="https://yomou.syosetu.com/search.php" +url)
        print('retrieving',"https://yomou.syosetu.com/search.php" +url)
        soup = bs4.BeautifulSoup(response,features='html.parser')
        response.close()
        novels.extend(create_entry(soup))
    with jsonlines.open('novels.jsonl', mode='w') as writer:
        writer.write(novels)