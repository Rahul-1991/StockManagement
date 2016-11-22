from django.shortcuts import render, render_to_response
from urllib import urlopen
import csv

def apology(top='', bottom=''):
     def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
            ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
     return render_to_response("app/apology.html", {top: escape(top), bottom: escape(bottom)})

def lookup(symbol):
    if symbol.startswith("^"):
        return None

    if "," in symbol:
        return None

    # query Yahoo for quote
    # http://stackoverflow.com/a/21351911
    try:
        url = "http://download.finance.yahoo.com/d/quotes.csv?f=snl1&s={}".format(symbol)
        print url
        webpage = urlopen(url)
        print webpage
        datareader = csv.reader(webpage.read().decode("utf-8").splitlines())
        row = next(datareader)
    except Exception as e:
        print e
        return None

    # ensure stock exists
    try:
        price = float(row[2])
    except:
        return None

    # return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
    return {
        "name": row[1],
        "price": price,
        "symbol": row[0].upper()
    }
