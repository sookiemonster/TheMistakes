from flask import Flask, Blueprint, request, session, render_template, redirect, g
import os, sqlite3, json, urllib
from datetime import date
import auth
import random
from db import get_db
bp = Blueprint('shop', __name__)

today = date.today()

@bp.route("/shop", methods=['GET', 'POST'])
@auth.login_required
def shop():
    #if item is bought
    if request.method == 'POST':
        d = get_db()
        c = d.cursor()

        purchasedItem = request.form['itemName']
        # print(purchasedItem)
        c.execute("SELECT * FROM USERS WHERE USERNAME = (?)", (session['username'],))
        userPoints = c.fetchone()
        c.execute("SELECT * FROM SHOP WHERE NAME = (?)", (purchasedItem,))
        itemData = c.fetchone()
        # print(itemData)
        #check and subtract points
        if userPoints[2] < itemData[3]:
            return render_template("shop.html",error="You're broke")
        c.execute("UPDATE USERS SET POINTS = (?) WHERE USERNAME = (?)", (userPoints[2]-itemData[3], session['username']))
        #remove item from market
        c.execute("DELETE FROM SHOP WHERE NAME = (?)", (purchasedItem,))
        #update inventory
        d.commit()
        inventory_path = "inventories/%s.txt" % session['username']
        with open(inventory_path, "a") as inventory:
            inventory.write(""+itemData[0]+"/"+itemData[1]+"/"+itemData[2])
            inventory.write("\n")
        #run refresh_shop method
    refresh_shop()
    d = get_db()
    c = d.cursor()
    c.execute("SELECT * FROM SHOP")
    items = c.fetchall()
    c.execute("SELECT * FROM USERS WHERE USERNAME = (?)", (session['username'],))
    userPoints = c.fetchone()
    #render shop.html with parameters
    return render_template("shop.html",items=items,balance=userPoints[2])


def refresh_shop():

    d = get_db()
    c = d.cursor()

    c.execute("SELECT * FROM SHOP")
    existing_item = c.fetchone()
    if not existing_item:
        # add if table is empty
        for i in range(0,2):
            randColor = randomColor()
            # will generate random color based on day
            itemInfo = ["card_color",randColor[0],randColor[1],random.randint(100,300),today.strftime("%m/%d/%y")]
            # print(itemInfo)
            addItem = "INSERT INTO SHOP VALUES(?,?,?,?,?)"
            c.execute(addItem,itemInfo)

            randPFP = randomPFP()
            # will generate random pfp based on day
            itemInfo = ["pfp",randPFP[0],randPFP[1],random.randint(100,300),today.strftime("%m/%d/%y")]
            # print(itemInfo)
            addItem = "INSERT INTO SHOP VALUES(?,?,?,?,?)"
            c.execute(addItem,itemInfo)
            d.commit()

    if existing_item:
        if existing_item[4] != today.strftime("%m/%d/%y"):
            # clear table and add if date does not match (table stays the same if date matches)
            c.execute("DELETE FROM SHOP")

            for i in range(0,2):
                randColor = randomColor()
                #will generate random color based on day
                itemInfo = ["card_color",randColor[0],randColor[1],random.randint(100,300),today.strftime("%m/%d/%y")]
                # print(itemInfo)
                addItem = "INSERT INTO SHOP VALUES(?,?,?,?,?)"
                c.execute(addItem,itemInfo)

                randPFP = randomPFP()
                # will generate random pfp based on day
                itemInfo = ["pfp",randPFP[0],randPFP[1],random.randint(100,300),today.strftime("%m/%d/%y")]
                # print(itemInfo)
                addItem = "INSERT INTO SHOP VALUES(?,?,?,?,?)"
                c.execute(addItem,itemInfo)
                d.commit()

def randomColor():
    hexList = "0123456789ABCDEF"
    randomColor = hexList[random.randint(0,15)]+hexList[random.randint(0,15)]+hexList[random.randint(0,15)]+hexList[random.randint(0,15)]+hexList[random.randint(0,15)]+hexList[random.randint(0,15)]
    # opens up API data (API data being a randomly generated color hex value)
    req = urllib.request.Request('https://www.thecolorapi.com/id?hex='+randomColor, headers={'User-Agent': 'Mozilla/5.0'}) #change deck count for more decks of 52
    data = urllib.request.urlopen(req)
    # reads API data into variable (comes in as JSON data)
    response = data.read()
    # converts JSON data to python dictionary
    response_info = json.loads(response)
    # sets a variable dictionary with color data
    color = response_info["name"]
    RGB = response_info["rgb"]
    # set variable for rgb values
    colorName = color['value']
    # set variable for color name
    colorRGB = str(RGB["r"])+","+str(RGB["g"])+","+str(RGB["b"])
    return [colorName,colorRGB]

def randomPFP():
    # opens up API data (API data being a randomly generated image from api)
    req = urllib.request.Request('https://picsum.photos/v2/list?limit=1&page='+str(random.randint(0,993)), headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req)
    # reads API data into variable (comes in as JSON data)
    response = data.read()
    # converts JSON data to python dictionary
    response_info = json.loads(response)
    name = "Image "+str(response_info[0]["id"])
    # set variable for image "name"
    url = response_info[0]["url"]
    # set variable for image url
    return [name,url]
