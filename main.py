#!/usr/bin/python

import sys
import getopt
import requests
import pandas as pd
from bs4 import BeautifulSoup

VERSION = 0.1

TABLE_FORMAT = "fancy_grid"

tournaments = {
    "men": {
        "no": {"eliteserien": 1, "div1": 2, "div2a1": 4, "div2a2": 5},
        "en": {"pl": 230},
        "fr": {"ligue1": 241},
        "es": {"laliga": 238},
        "de": {"bundesliga": 239},
        "it": {"seriea": 236},
    },
    "women": {"global": {}, "no": {"toppserien": 3}},
}


def printUsage():
    print("usage: aof-cli -g [m/f] -c COUNTRY -l LEAGUE")
    return 0


def printVersion():
    print("Versjon: " + str(VERSION))
    return 0


def getTournamentTable(tournamentId, tournamentType):
    pos = ""
    url = (
        "https://www.altomfotball.no/elementsCommonAjax.do?cmd=table&tournamentId="
        + str(tournamentId)
        + "&subCmd="
        + tournamentType
        + "&live=false&useFullUrl=false"
    )
    df = pd.read_html(url, attrs={"class": "sd_table"}, flavor="bs4")[0]

    if tournamentType == "both":
        df.rename(columns={"Unnamed: 0_level_0": pos}, inplace=True)
    else:
        del df["Siste Kamper"]
        df.rename(columns={"Unnamed: 0": pos}, inplace=True)
        df.set_index(pos, inplace=True)
    return df


def getOnTV():
    url = "https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&subCmd=fewFixturesTournamentNames&month=twoweeks&filter=tv&useFullUrl=false"
    df = pd.read_html(url, attrs={"class": "sd_table"}, flavor="bs4")[0]
    del df["Unnamed: 3_level_0"]
    df.columns = df.columns.droplevel(1)
    return df


def getNews():
    url = "https://www.altomfotball.no/element.do"
    data = requests.get(url).text
    soup = BeautifulSoup(data, "html.parser")
    newsTitle = soup.find_all("div", class_="newsTitle")[2].text
    newsIngress = soup.find_all("div", class_="newsIngress")[2].text
    news = newsTitle + "\n" + newsIngress
    return news


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hvg:m:c:l:")
    except getopt.GetoptError:
        print("\n" + getNews())
        print(getOnTV().to_markdown(tablefmt=TABLE_FORMAT))
        sys.exit(0)
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
