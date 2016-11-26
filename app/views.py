"""
Definition of views.
"""

from django.shortcuts import render, render_to_response, redirect
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from helpers import apology, lookup
from models import Users, Portfolio, Transaction
from datetime import datetime
from django.core import serializers
import json

def index(request):
    if not request.session.get('id'):
        return redirect('login')

    empty_stock_rows = Portfolio.objects.filter(quantity__lte=0).delete()
    user_portfolio_info = Portfolio.objects.filter(id=request.session.get('id'))
    user_info = list()
    for row in user_portfolio_info:
        stock_total_cost = row.price
        current_stock = lookup(row.symbol)
        current_total_stock_price = current_stock.get('price') * row.quantity
        serialized_row = serializers.serialize('json', [row])
        if serialized_row:
            user_stock_info = json.loads(serialized_row)[0].get('fields')
            user_stock_info.update({'current_price': lookup(user_stock_info.get('symbol')).get('price')})
            user_stock_info.update({'status': current_total_stock_price - stock_total_cost})
            user_info.append(user_stock_info)

    return render(request, 
                  'app/index.html',
                  {'user_info': user_info})

def login(request):
    if request.session.get('id'):
        del request.session['id']

    if request.method == 'GET':
        return render(request, 'app/login.html')
    else:
        if not request.POST.get('username'):
            return apology("Username cannot be empty")
        if not request.POST.get("password"):
            return apology("Password field cannot be empty")

        username = request.POST.get("username")
        password = request.POST.get("password")
        rows = Users.objects.filter(username=username)
        if rows:
            if rows[0].hash != password:
                return apology("Password does not match")
            else:
                request.session['id'] = rows[0].id
        else:
            new_user = Users(username=username, hash=password, cash=10000.0)
            new_user.save()

        return redirect('index')

def logout(request):
    del request.session['id']
    return redirect('login')

def buy(request):
    if not request.session.get('id'):
        return redirect('login')

    if request.method == 'POST':
        if not request.POST.get('symbol'):
            return apology('Symbol field cannot be empty')
        if not request.POST.get('quantity'):
            return apology('Quantity field cannot be empty')

        symbol = request.POST.get('symbol').upper()
        quantity = int(request.POST.get('quantity'))
        stock_info = lookup(symbol)
        if not stock_info:
            return apology("No such symbol exists")

        user_info = Users.objects.filter(id=request.session.get('id'))
        if not user_info:
            return apology("Your session is invalid")

        available_cash = user_info[0].cash
        if available_cash >= quantity*stock_info.get('price'):
            user_portfolio = Portfolio.objects.filter(id=request.session.get('id')).filter(symbol=symbol)
            if user_portfolio:
                user_portfolio[0].price += stock_info.get('price') * quantity
                user_portfolio[0].quantity += quantity
                user_portfolio[0].save()
            else:
                user_portfolio = Portfolio(
                                    id=request.session.get('id'),
                                    symbol=symbol,
                                    price=stock_info.get('price') * quantity,
                                    quantity=quantity,
                                    stock_name=stock_info.get('name'),
                                )
                user_portfolio.save()
            user_info[0].cash -= quantity*stock_info.get('price') * quantity
            user_info[0].save()
            transaction = Transaction(symbol=stock_info.get('symbol'), 
                                      price=stock_info.get('price'), 
                                      share=quantity,
                                      timestamp=datetime.now())
            transaction.save()
            return redirect('index')
        else:
            return apology("You do not have enough cash")
    else:
        return render(request, 'app/buy.html')

def quote(request):
    if request.method == 'POST':
        if not request.POST.get('symbol'):
            return apology('Symbol field cannot be empty')
        symbol = request.POST.get('symbol')
        stock_info = lookup(symbol)
        if not stock_info:
            return apology("Could not find info for the symbol")
        return render(request, 
                      'app/quoted.html', 
                        {'stock_info': stock_info})
    else:
        return render(request, 'app/quote.html')

def sell(request):
    if request.method == 'POST':
        if not request.POST.get('symbol'):
            return apology('Symbol field cannot be empty')
        if not request.POST.get('quantity'):
            return apology('Quantity field cannot be empty')
        symbol = request.POST.get('symbol').upper()
        quantity = int(request.POST.get('quantity'))
        stock_info = lookup(symbol)
        if not stock_info:
            return apology('No information available for this symbol')
        user_portfolio = Portfolio.objects.filter(
                            id=request.session.get('id')).filter(
                            symbol=symbol)
        if not user_portfolio:
            return apology('No such stock found in your account')
        stocks_available = user_portfolio[0].quantity
        if quantity > stocks_available:
            return apology('You do not have enough stocks to sell')
        user_portfolio[0].quantity -= quantity
        user_portfolio[0].price -= stock_info.get('price')*quantity
        user_portfolio[0].save()
        user = Users.objects.filter(id=request.session.get('id'))
        user[0].cash += stock_info.get('price') * quantity
        user[0].save()
        transaction = Transaction(symbol=stock_info.get('symbol'), 
                                      price=stock_info.get('price'), 
                                      share=-quantity,
                                      timestamp=datetime.now())
        transaction.save()
            
        return redirect('index')
    else:
        return render(request, 'app/sell.html')
