import re
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def comparisRequests(place):
        place = place[0]
        driver = webdriver.Chrome()

        driver.get("https://www.comparis.ch/immobilien/default")

        assert driver.current_url == "https://www.comparis.ch/immobilien/default"
        elem = driver.find_element(By.XPATH, '// *[ @ id = "txLocationSearchString"]')

        elem.clear()
        elem.send_keys(place)
        elem.send_keys(Keys.RETURN)

        pricesAndRooms = []

        try:

            resultList1 = driver.find_element_by_id('result_list_ajax_container').find_elements_by_tag_name('div')
            html = resultList1[0].get_attribute('innerHTML')
            pricesAndRooms.append(re.findall('<li>(\d.?)\s?Zimmer<\/li>|<strong>CHF(.*)<\/strong', html))
        except Exception:
            print("first page not found for"+place)

        sleep(3)
        try:
            driver.find_element_by_xpath('//*[@data-wt-fa-label="Page Changed to 2"]').click()
            resultList2 = (driver.find_element_by_id('result_list_ajax_container').find_elements_by_tag_name('div'))

            html = resultList2[0].get_attribute('innerHTML')
            pricesAndRooms.append(re.findall('<li>(\d.?)\s?Zimmer<\/li>|<strong>CHF(.*)<\/strong', html))
        except Exception:
            print("second page not found for" + place)

        sleep(1)
        try:
            driver.find_element_by_xpath('//*[@data-wt-fa-label="Page Changed to 3"]').click()
            resultList3 = (driver.find_element_by_id('result_list_ajax_container').find_elements_by_tag_name('div'))

            html = resultList3[0].get_attribute('innerHTML')
            pricesAndRooms.append(re.findall('<li>(\d.?)\s?Zimmer<\/li>|<strong>CHF(.*)<\/strong', html))
        except Exception:
            print("third page not found for" + place)


        cleanedPlacesAndRooms = []
        try:
            for entry in pricesAndRooms:
                i = 0
                while (i < len(entry)):
                    if not(entry[i][0] == '') and not(entry[i+1][1] ==''):
                        cleanedPlacesAndRooms.append(entry[i][0])
                        cleanedPlacesAndRooms.append(str(entry[i+1][1]).replace("'",""))
                        i = i+2
                    else:
                        i = i+1
        except Exception:
            print("adding failed for  "+place)

        pricePerRoomOnAverage = getPricePerRoomOnAverage(cleanedPlacesAndRooms)
        driver.close()
        return place, pricePerRoomOnAverage




def getPricePerRoomOnAverage(listOfResults):
    prices = []

    for i in range(0, len(listOfResults), 2):
        rooms = float(str(listOfResults[i]).replace("½",".5"))
        price = float(listOfResults[i+1])
        priceRoomRation = price/rooms
        if price > 350:
            prices.append(priceRoomRation)

    if len(prices) == 0:
        return 99999
    return sum(prices)/ len(prices)
