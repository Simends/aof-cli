#!/usr/bin/python

import sys
import datetime
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

teams = {
    **dict.fromkeys(["viking"], 303),
    **dict.fromkeys(["lillestrøm"], 308),
    **dict.fromkeys(["molde"], 309),
    **dict.fromkeys(["strømsgodset"], 328),
    **dict.fromkeys(["aalesund"], 403),
    **dict.fromkeys(["rosenborg", "rbk"], 313),
    **dict.fromkeys(["sarpsborg 08", "sarpsborg", "sarpsborg_08", "sarpsborg08"], 541),
    **dict.fromkeys(["bodø/glimt", "bodøglimt"], 307),
    **dict.fromkeys(["odd"], 311),
    **dict.fromkeys(["tromsø"], 315),
    **dict.fromkeys(["vålerenga"], 314),
    **dict.fromkeys(["hamkam"], 320),
    **dict.fromkeys(["sandefjord"], 324),
    **dict.fromkeys(["haugesund"], 306),
    **dict.fromkeys(["jerv"], 3181),
    **dict.fromkeys(["kristiansund bk", "kristiansund"], 411),
    **dict.fromkeys(["brann"], 302),
    **dict.fromkeys(["mjøndalen"], 921),
    **dict.fromkeys(["stabæk"], 312),
    **dict.fromkeys(["sandnes ulf", "sandnes-ulf", "sandnesulf"], 496),
    **dict.fromkeys(["kfum"], 3584),
    **dict.fromkeys(["ranheim"], 414),
    **dict.fromkeys(["start"], 305),
    **dict.fromkeys(["sogndal"], 326),
    **dict.fromkeys(["fredrikstad"], 361),
    **dict.fromkeys(["raufoss"], 321),
    **dict.fromkeys(["åsane"], 341),
    **dict.fromkeys(["bryne"], 304),
    **dict.fromkeys(["kongsvinger"], 322),
    **dict.fromkeys(["grorud"], 2302),
    **dict.fromkeys(["stjørdals-blink"], 2101),
    **dict.fromkeys(["skeid"], 319),
}


def printUsage():
    print(
        "\nUsage:\n\taof-cli [-l | --liga <liganavn>] [--tabellformat <format>] --tabell | --hjemmetabell | --bortetabell"
    )
    print(
        "\taof-cli [-l | --liga <liganavn>] [--tabellformat <format>] --terminliste <måned>"
    )
    print(
        "\taof-cli [-l | --liga <liganavn>] [--tabellformat <format>] [--statlinjer <linjetall> | --statfull] -s | --statistikk <statistikktype>"
    )
    print("\taof-cli [-h | --hjelp] | [-v | --versjon]\n")
    print("Statistikk:")
    print(
        "\tMulige alternativer: toppscorer,"
        + " assist,"
        + " poengliga,"
        + " gule kort,"
        + " røde kort,"
        + " straffe,"
        + " straffebom,"
        + " selvmål,"
        + " kamper fra start,"
        + " byttet inn,"
        + " byttet ut,"
        + " lagbørs,"
        + " råtassen,"
        + " på benken,"
        + " råeste lag,"
        + " når kom målene,"
        + " tilskuertall"
    )
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
    try:
        df = pd.read_html(
            url, attrs={"class": "sd_table"}, flavor="bs4", keep_default_na=False
        )[0]
    except ValueError:
        print("No data found")
        sys.exit(0)

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
    try:
        df = pd.read_html(
            url, attrs={"class": "sd_table"}, flavor="bs4", keep_default_na=False
        )[0]
    except ValueError:
        print("No data found")
        sys.exit(0)
    if statType == "spectators":
        df.set_index("Lag", inplace=True)
    else:
        df.set_index("Nr.", inplace=True)
    return df


def getTournamentFixtures(tournamentId, month, year):
    url = (
        "https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&tournamentId="
        + str(tournamentId)
        + "&month="
        + month
        + str(year)
        + "&useFullUrl=false"
    )
    try:
        df = pd.read_html(
            url, attrs={"class": "sd_fixtures"}, flavor="bs4", keep_default_na=False
        )[0]
    except ValueError:
        print("No data found")
        sys.exit(0)
    df["Lag"] = df[3] + " - " + df[5]
    del df[7]
    del df[2]
    del df[3]
    del df[5]
    df = df[[0, 1, 4, "Lag", 6]]
    df.rename(columns={0: "Dato", 1: "Runde", 4: "Tid", 6: "Kanal"}, inplace=True)
    return df


def getOnTV():
    url = "https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&subCmd=fewFixturesTournamentNames&month=twoweeks&filter=tv&useFullUrl=false"
    try:
        df = pd.read_html(
            url, attrs={"class": "sd_table"}, flavor="bs4", keep_default_na=False
        )[0]
    except ValueError:
        print("No data found")
        sys.exit(0)
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
                "terminliste=",
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
    fixtures = ""
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
            fixtures = a
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
            print(
                getTournamentTable(tournament, table).to_markdown(tablefmt=table_format)
            )
    if fixtures != "":
        if tournament != "":
            time = datetime.datetime.now()
            year = time.year
            if fixtures == "idag":
                month = "0"
            else:
                month = fixtures
            print(
                getTournamentFixtures(tournament, month, year).to_markdown(
                    tablefmt=table_format
                )
            )
    if stat_mode != "":
        if tournament != "":
            if stat_lines > 0:
                print(
                    getTournamentStatistics(tournament, stat_mode)
                    .head(stat_lines)
                    .to_markdown(tablefmt=table_format)
                )
            else:
                print(
                    getTournamentStatistics(tournament, stat_mode).to_markdown(
                        tablefmt=table_format
                    )
                )
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
