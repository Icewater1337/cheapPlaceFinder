from multiprocessing import Pool

import pickle
import requests
import csv
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

api_key = "AIzaSyAn1t3ZQOJL2su36ZL-RZi34TSJBgXSNUc"



def comparisRequests(place):
     #// *[ @ id = "txLocationSearchString"]
    #https: // www.comparis.ch / immobilien / default
    try:
        place = place[1]
        driver = webdriver.Chrome()

        driver.get("https://www.comparis.ch/immobilien/default")

        assert driver.current_url == "https://www.comparis.ch/immobilien/default"
        elem = driver.find_element(By.XPATH, '// *[ @ id = "txLocationSearchString"]')

        elem.clear()
        elem.send_keys(place)
        elem.send_keys(Keys.RETURN)

        pricesAndRooms = []

        resultList1 = driver.find_element_by_id('result_list_ajax_container').find_elements_by_tag_name('div')
        html = resultList1[0].get_attribute('innerHTML')
        pricesAndRooms.append(re.findall('<li>(\d.?)\s?Zimmer<\/li>|<strong>CHF(.*)<\/strong', html))

        sleep(3)
        driver.find_element_by_xpath('//*[@data-wt-fa-label="Page Changed to 2"]').click()
        resultList2 = (driver.find_element_by_id('result_list_ajax_container').find_elements_by_tag_name('div'))

        html = resultList2[0].get_attribute('innerHTML')
        pricesAndRooms.append(re.findall('<li>(\d.?)\s?Zimmer<\/li>|<strong>CHF(.*)<\/strong', html))

        sleep(1)
        driver.find_element_by_xpath('//*[@data-wt-fa-label="Page Changed to 3"]').click()
        resultList3 = (driver.find_element_by_id('result_list_ajax_container').find_elements_by_tag_name('div'))

        html = resultList3[0].get_attribute('innerHTML')
        pricesAndRooms.append(re.findall('<li>(\d.?)\s?Zimmer<\/li>|<strong>CHF(.*)<\/strong', html))

        #save_obj(pricesAndRooms, place)

        cleanedPlacesAndRooms = []

        for entry in pricesAndRooms:
            i = 0
            while (i < len(entry)):
                if not(entry[i][0] == '') and not(entry[i+1][1] ==''):
                    cleanedPlacesAndRooms.append(entry[i][0])
                    cleanedPlacesAndRooms.append(str(entry[i+1][1]).replace("'",""))
                    i = i+2
                else:
                    i = i+1

        pricePerRoomOnAverage = getPricePerRoom(cleanedPlacesAndRooms)
        driver.close()
        return place, pricePerRoomOnAverage

    except Exception:
        driver.close()
        return place, 999999

def getPricePerRoom(listOfResults):
    prices = []

    for i in range(0, len(listOfResults), 2):
        rooms = float(str(listOfResults[i]).replace("½",".5"))
        price = float(listOfResults[i+1])
        priceRoomRation = price/rooms
        prices.append(priceRoomRation)

    return sum(prices)/ len(prices)


def getConnectionsFromList(lst):
    workPlace = 'Bern'
    place = lst[1]
    return lst[3], lst[1], getConnections('http://transport.opendata.ch/v1/connections?from=' + workPlace + '&to=' + place)

def getConnectionsFromListMap(lst):
    workPlace = 'Bern'
    place = lst[1]
    return lst[3], lst[1], getConnections(mapsUrl)



def readCsv(path):
    lst = []
    with open(path, newline='',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            print(row['Rang'], row['Ort'], row['Kanton'], row['Steuersatz'])
            lst.append((row['Rang'], row['Ort'], row['Kanton'], float(row['Steuersatz'])))
            # Rang	Ort	Kanton	Steuersatz
        return lst


def getConnections(url):
    return requests.get(url).json()

def getDurationFromGoogleMapsJsonInMinutes(json):
    return json["rows"][0]["elements"][0]["duration"]["value"]

def getDurationFromJsonInMinutes(json, connectionNbr):
    durationString = json.get("connections")[connectionNbr].get("duration")
    hoursAndMinutesString = re.search(r"(?<=d).*?(?=:..$)", durationString).group(0)
    hours = 60 * int(hoursAndMinutesString.split(':')[0])
    minutes = int(hoursAndMinutesString.split(':')[1])
    return hours + minutes



def getCheapestPlaceWithinDuration(maxDuration, jsonReqs):
    # iterate through list and get all durations that are within max duration. Then sort according to
    # steuersatz return name and steuersatz and duration
    #lst = readCsv("Steuersatz100.txt")
    cheapest = 100
    cheapestName = ''
    cheapestDuration = 100
    for tax, place, jsonRequest in jsonReqs:
        # make thread

        #duratiion = getDurationFromJsonInMinutes(jsonRequest, 0)
        duratiion = getDurationFromGoogleMapsJsonInMinutes(jsonRequest)
        if duratiion <= maxDuration:
            if tax < cheapest:
                cheapest = tax
                cheapestName = place
                cheapestDuration = duratiion

    return cheapest, cheapestName, cheapestDuration


def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    p = Pool(5)
    #comparisRequests("zürich")

    lst = readCsv("Steuersatz100.txt")
    #lst = lst[0:150]
    #lst = readCsv("SteuersatzTo900.txt")
    #fz = p.map(getConnectionsFromList, lst)
    #fz = p.map(getConnectionsFromListMap, lst)
    #save_obj(fz ,"durationsToPlacesGoogleMaps")
    fz = p.map(comparisRequests, lst)
    cheapestTax, cheapestName, cheapestDuration = getCheapestPlaceWithinDuration(60, fz)
    save_obj(fz, "PricesBern")

#jsonRequest = getConnections('http://transport.opendata.ch/v1/connections?from=Lausanne&to=Genève')
