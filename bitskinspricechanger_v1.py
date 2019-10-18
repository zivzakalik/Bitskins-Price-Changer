
import json
import requests
import pyotp
import pprint
import time
import os
import base64
from threading import Timer
from decimal import Decimal
from ratelimit import limits, sleep_and_retry

    #connection details
with open('myItemsdb.json') as f:
    myItems = json.load(f)
apikey = ''
secret = ''

    #send request to the api
@sleep_and_retry
@limits(calls = 8, period = 1)
def sendReq(method, *args):
    code = pyotp.TOTP(secret).now()
    moreArgs = ''
    for ar in args:
        moreArgs+=ar+'&'
    url_mrktData = 'https://bitskins.com/api/v1/'+method+'/?api_key='+apikey+'&app_id=730&code='+str(code)+'&'+moreArgs
    while True:
        try:
            resp = requests.get(url = url_mrktData)
        except:
            print('server offline, press enter to try again')
            input()
            continue
        else:
            return json.loads(resp.text)

    # checks if you have the login details and takes them if you dont
def loginDetails():
    global apikey
    global secret
    if myItems['login']['api_key'] == '':
        apikey = input('Please insert your API key: ')
        myItems['login']['api_key'] = apikey
    else:
        apikey = myItems['login']['api_key']
    if myItems['login']['secret_code'] == '':
        secret = input('Please insert your secret code: ')
        while True:
            try:
                base64.b32decode(secret)
            except:
                secret = input('Secret code false - has to be  on base 32, please try again:\n ')
            else:
                break
        myItems['login']['secret_code'] = secret
    else:
        secret = myItems['login']['secret_code']
    if sendReq('get_account_balance')['status'] == 'fail':
        clearLoginDetails()
        os.system('cls')
        print('login details are incorrect, please try again.')
        loginDetails()

    #clears the login details when a user logs out.
def clearLoginDetails():
    myItems['login']['api_key'] = ''
    myItems['login']['secret_code'] = ''

    # updates myItems with api info
def getItemsOnSale():
    updated = False
    dellist = []
    global myItems
    inv = sendReq('get_my_inventory') 
    for myitem in myItems['items']:
        exists = False
        for item in inv['data']['bitskins_inventory']['items']:
            if(myitem['itemId'] == item['item_ids'][0]):
                exists = True
                break
        if not exists:
            print(myitem['name'] +' was removed because its in the bitskins inventory.')
            dellist.append(myitem)
    for item in dellist:
        myItems['items'].remove(item)
    for item in inv['data']['bitskins_inventory']['items']:
        for myitem in myItems['items']:
            updated = False
            if myitem['itemId'] == item['item_ids'][0]:
                myitem['price'] = item['prices'][0]
                updated = True
                break
        if not updated:
            myItems['items'].append({'name':item['market_hash_name'], 'price':float(item['prices'][0]), 'itemId': item['item_ids'][0]})
            new = myItems['items'][-1]
            print('added new weapon: '+ str(myItems['items'].index(new)+1) + ': ' + new['name'] + ' Current price: '+str(new['price']))
    
    # prints the items you have for sale.
def printItems():
    os.system('cls')
    for item in myItems['items']:
        print(str(myItems['items'].index(item)+1)+': '+ item['name'] + ' Current price: ' + str(item['price']) +' Minimal price: '+ str(item.get('minPrice', 'not set'))+' Maximal price: '+ str(item.get('maxPrice', 'not set')))

   #user input, returns the item chosen
def userInput():
    global myItems
    t.cancel()
    weaponIndex =''
    inputcheck = False
    current = myItems['items']
    print('Type "skip" to keep updating the site without any changes, or "logout" to change accounts.\n')
    print('which weapon do you want to set?\n')
    while not inputcheck:
        try:
            weaponIndex = input()
            if weaponIndex == "skip":
                os.system('cls')
                return -1
            if weaponIndex == "logout":
                os.system('cls')
                clearLoginDetails()
                setMinMax()
                return -1
            weaponIndex = abs(int(weaponIndex))
            myItems['items'][weaponIndex-1]
        except:
            print('Please choose a round number from the list.')
        else:
                inputcheck = True
                weaponIndex -= 1
    inputcheck=False
    print(current[weaponIndex]['name']+' is the item you chose. Current price: ' + str(current[weaponIndex]['price']))
    print('Whats the minimal price?\n')
    while not inputcheck:
        try:
            minPrice = abs(round(float(input()),2))
        except:
            print('Please choose a number.')
        else:
            inputcheck = True
    inputcheck = False
    print('And the maximal price?\n')
    while not inputcheck:
        try:
            maxPrice = abs(round(float(input()),2))
        except:
            print('Please choose a number.')
        else:
            if maxPrice < minPrice:
                print('Maximal price must be higher than the minimal price.')
            else:
                inputcheck = True
    myItems['items'][weaponIndex]['maxPrice']= maxPrice
    myItems['items'][weaponIndex]['minPrice']= minPrice
    print('Processing...')
    return weaponIndex

    #changing prices in the myItems dictionary according to min max and price
def priceChange():
    for item in myItems['items']:        
        findLowest(myItems['items'].index(item))
        currentItem = myItems['items'][myItems['items'].index(item)]
        oldprice = float(currentItem['price'])
        if currentItem.get('maxPrice', 'none') != 'none':
            if Decimal(currentItem['lowestAvailable'])-Decimal(0.01) != currentItem['price']:
                if currentItem['lowestAvailable'] >= currentItem['maxPrice']:
                    oldprice = float(currentItem['price'])
                    currentItem['price'] = currentItem['maxPrice']
                elif currentItem['lowestAvailable'] <= currentItem['minPrice']:
                    oldprice = float(currentItem['price'])
                    currentItem['price'] = currentItem['minPrice']
                else:
                    oldprice = float(currentItem['price'])
                    currentItem['price'] = float(Decimal(str(currentItem['lowestAvailable']))-Decimal('0.01'))
        newprice = float(currentItem['price'])
        if oldprice != newprice:
            print('The price for ' + currentItem['name'] + ' was updated from ' + str(oldprice) + ' to ' + str(currentItem['price']))
        if currentItem['price'] == 0:
            currentItem['price'] = 0.01

#    #getting index, returning lowest price available. doesnt include own items.
def findLowest(index):
    name = myItems['items'][index]['name']
    itemOnInv = sendReq('get_inventory_on_sale','market_hash_name='+name,'sort_by=price','per_page=30','order=asc')
    for item in itemOnInv['data']['items']:
        if not item['is_mine']:
            myItems['items'][index]['lowestAvailable'] = float(item['price'])
            break

    # prints the chosen item
def printChosen(index):
    if index != -1:
        current = myItems['items']
        os.system('cls')
        print('The item you chose is ' + current[index]['name'] + '.\nThe price set is: ' + str(current[index]['price']) + ' Minimal price set: '+str(current[index]['minPrice']) + '. Maximal price set: ' + str(current[index]['maxPrice'])+'.')


    #saving to DB
def updateDB():
    with open('myItemsdb.json', 'w', encoding='utf-8') as f:
        json.dump(myItems, f, ensure_ascii=False, indent=4)

    #updating prices on the site
def updateSite():
    current = myItems['items']
    idString = ''
    priceString = ''
    for item in current:
        idString += item['itemId'] + ','
        priceString += str(item['price']) +','
    priceString = priceString[:-1]
    sendReq('modify_sale_item','item_ids='+idString,'prices='+priceString)

    # updates both DB and site
def updateAll():
    updateDB()
    updateSite()

    # refreshing database and site every set time
def refresh():
    global t
    t  = Timer(60, refresh)
    getItemsOnSale()
    priceChange()
    updateAll()
    t.start()

    #main app setter
def setMinMax():  
    loginDetails()
    getItemsOnSale()
    printItems()
    index = userInput()
    priceChange()
    printChosen(index) #price could change after the input so its a seperate function
    updateAll()

    #main
t = Timer(60, refresh)
while True:
    setMinMax()
    t = Timer(60, refresh)
    t.start()
    print('Press enter to set another weapon.')
    input()