#!/usr/bin/python

import sys
import getopt
import requests
import pandas as pd
from bs4 import BeautifulSoup

VERSION = 0.1


tournaments = {
    **dict.fromkeys(["eliteserien"], 1),
    **dict.fromkeys(["obos", "obos ligaen", "obos_ligaen"], 2),
    **dict.fromkeys(["toppserien"], 3),
    **dict.fromkeys(["pl", "premier league", "premier_league"], 230),
    **dict.fromkeys(["ligue1"], 241),
    **dict.fromkeys(["laliga"], 238),
    **dict.fromkeys(["bundesliga"], 239),
    **dict.fromkeys(["seriea"], 236),
    **dict.fromkeys(["liga portugal bwin"], 249),
    **dict.fromkeys(["eredivisie"], 243),
    **dict.fromkeys(["jupiler pro league"], 246),
    **dict.fromkeys(["3f superliga"], 244),
    **dict.fromkeys(["allsvenskan"], 245),
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


def getTournamentStatistics(tournamentId, statType):
    url = (
        "https://www.altomfotball.no/elementsCommonAjax.do?cmd=statistics&subCmd="
        + statType
        + "&tournamentId="
        + str(tournamentId)
        + "&seasonId=&teamId=&useFullUrl=false"
    )
    df = pd.read_html(url, attrs={"class": "sd_table"}, flavor="bs4")[0]
    if statType == "spectators":
        df.set_index("Lag", inplace=True)
    else:
        df.set_index("Nr.", inplace=True)
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
    table_format = "fancy_grid"
    if len(argv) == 0:
        print("\n" + getNews())
        print(getOnTV().to_markdown(tablefmt=table_format))
        sys.exit(0)
    try:
        opts, args = getopt.getopt(
            argv,
            "hvl:s:",
            [
                "hjelp",
                "versjon",
                "liga=",
                "tabell",
                "hjemmetabell",
                "bortetabell",
                "tabellformat",
                "lag=",
                "terminliste",
                "statistikk=",
                "statlinjer=",
                "statfull",
            ],
        )
    except getopt.GetoptError as err:
        print(err)
        printUsage()
        sys.exit(1)
    tournament = ""
    team = ""
    table = ""
    fixtures = False
    stat_mode = ""
    stat_lines = 10
    for o, a in opts:
        if o in ("-h", "--hjelp"):
            printUsage()
            sys.exit(0)
        elif o in ("-v", "--versjon"):
            printVersion()
            sys.exit(0)
        elif o in ("-l", "--liga"):
            tournament = a
        elif o == "--tabell":
            table = "total"
        elif o == "--hjemmetabell":
            table = "home"
        elif o == "--bortetabell":
            table = "away"
        elif o == "--lag":
            team = a
        elif o == "--terminliste":
            fixtures = True
        elif o in ("-s", "--statistikk"):
            if a.lower() == "toppscorer":
                stat_mode = "goals"
            elif a.lower() == "assist":
                stat_mode = "assists"
            elif a.lower() == "poengliga":
                stat_mode = "pointLeague"
            elif a.lower() == "gule kort":
                stat_mode = "yellowCards"
            elif a.lower() == "røde kort":
                stat_mode = "redCards"
            elif a.lower() == "straffe":
                stat_mode = "penaltyShots"
            elif a.lower() == "straffebom":
                stat_mode = "penaltyMisses"
            elif a.lower() == "selvmål":
                stat_mode = "ownGoals"
            elif a.lower() == "kamper fra start":
                stat_mode = "gamesFromStart"
            elif a.lower() == "byttet inn":
                stat_mode = "changedIn"
            elif a.lower() == "byttet ut":
                stat_mode = "changedOut"
            elif a.lower() == "lagbørs":
                stat_mode = "teamScore"
            elif a.lower() == "råtassen":
                stat_mode = "mostBrutalPerson"
            elif a.lower() == "på benken":
                stat_mode = "gamesAsSubstitute"
            elif a.lower() == "råeste lag":
                stat_mode = "mostBrutal"
            elif a.lower() == "når kom målene":
                stat_mode = "goalTiming"
            elif a.lower() == "tilskuertall":
                stat_mode = "spectators"
            else:
                print("option -s " + a + " not recognized")
                printUsage()
                sys.exit(1)
        elif o == "--statlinjer":
            stat_lines = int(a)
        elif o == "--statfull":
            stat_lines = 0
        elif o == "--tabellformat":
            table_format = a
        else:
            assert False, "unhandled option"
    if tournament == "" and team == "":
        tournament = "eliteserien"
    if tournament != "":
        tournament = tournaments[tournament.lower()]
    if table != "":
        if team != "":
            print("Not supported yet")
        if tournament != "":
            print(getTournamentTable(tournament, table).to_markdown(tablefmt=table_format))
    if fixtures == True:
        print("Not supported yet")
    if stat_mode != "":
        if tournament != "":
            if stat_lines > 0:
                print(getTournamentStatistics(tournament, stat_mode).head(stat_lines).to_markdown(tablefmt=table_format))
            else:
                print(getTournamentStatistics(tournament, stat_mode).to_markdown(tablefmt=table_format))
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
