from leeger.league_loader import YahooLeagueLoader, SleeperLeagueLoader
from leeger.model.league import League
from leeger.util.excel import leagueToExcel


if __name__ == "__main__":
    # Application registered @ https://developer.yahoo.com/apps/ydpKkbBS/

    ownerNamesAndAliases = {
        "Ryan Gillies": ['Ryan', 'Ryan Gillies', 'rgillies28'],
        "James Evancho": ['James', 'James Evancho', 'bengalball'],
        "Dan Cuthbert": ['Dan','Dan Cuthbert', 'dcuth'],
        "Tom Evancho": ['Tom (2)', 'Tom Evancho', 'tevancho'],
        "Bob Ross": ['Bob', 'Bob Ross', 'BobTheChamp2016'],
        "Christian Wagner": ['Christian', 'Chris', 'Christian Wagner', 'ChristianSwagner'],
        "Alex Cohen": ['Alex', 'Alex Cohen', 'ConePollos'],
        "Tom Gillies": ['Tom', 'TomGill'],
        "Eric Gillies": ['Eric', 'egillies21'],
        "Steve Shaffer": ['S', 'Steve Shaffer', 'S_Shaffer'],
        "Andrew Constant": ['Andrew', 'Kyle', 'Andrew Constant', 'aconstant10'],
        'Tom Flora': ['tflora'],
    }

    # First, get League from Yahoo 2
    clientId = "dj0yJmk9SU1vYUtUamVZVWUyJmQ9WVdrOWVXUndTMnRpUWxNbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTEx"
    clientSecret = "1af22c0213e33f0b3f8856322ad496c68ad0e0cc"

    yahooLeagueLoader = YahooLeagueLoader(
        "84229",
        [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019],
        clientId=clientId,
        clientSecret=clientSecret,
        ownerNamesAndAliases=ownerNamesAndAliases,
    )

    yahooLeague: League = yahooLeagueLoader.loadLeague()

    myYahooLeague = yahooLeague

    myLeague = yahooLeague 

    leagueToExcel(myLeague, "myLeagueStats.xlsx", overwrite=True)
