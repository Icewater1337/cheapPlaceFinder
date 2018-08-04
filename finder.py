from multiprocessing import Pool

import pickle
import requests
import csv
import ComparisRequestHandler as comparis

workPlace = 'Bern'
apiKey = 'AIzaSyBvRi8WcVAqTsx-TC7Xi_spt2wCNTuolyc'
base_request_url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
travelStyle = 'transit'


def getConnectionsFromList(lst):
    workPlace = 'Bern'
    apiKey = 'AIzaSyBvRi8WcVAqTsx-TC7Xi_spt2wCNTuolyc'
    base_request_url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    travelStyle = 'transit'
    place = lst[1]
    connection_request = "mode={}&origins={}&destinations={},Schweiz&departure_time=1533204000&key={}".format(
            travelStyle, workPlace,
            place, apiKey)

    # QUick fix. Unexperienced with multiprocessing,. No idea why this is, no time to fix
    request = getConnections(base_request_url + connection_request)

    if request.get('rows')[0].get('elements')[0].get('status') == 'NOT_FOUND':
        print()

    return lst[3], lst[1], request


def readCsv(path):
    lst = []
    with open(path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            print(row['Rang'], row['Ort'], row['Kanton'], row['Steuersatz'])
            lst.append((row['Rang'], row['Ort'], row['Kanton'], float(row['Steuersatz'])))
        return lst


def getConnections(request_url):
    return requests.get(request_url).json()


def getDurationFromJsonInMinutes(json):
    if json.get('rows')[0].get('elements')[0].get('status') == 'ZERO_RESULTS':
        return 99999
    durationInSeconds = json.get("rows")[0].get("elements")[0].get("duration").get("value")
    return durationInSeconds / 60


def getCheapestPlacesWithinDuration(maxDuration, jsonReqs):
    cheapest = 100
    durationList = []
    for tax, place, jsonRequest in jsonReqs:
        # make thread

        duration = getDurationFromJsonInMinutes(jsonRequest)

        if duration <= maxDuration:
            durationList.append((place, tax, duration))
            if tax < cheapest:
                cheapest = tax

    return sorted(durationList, key=lambda x: x[1])


def save_obj(obj, name):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def findCheapestOverallWithTaxAndLoan(cheapestPlaceWithinDurationLst, averageCostLst):
    finalCostDict = []
    for idx, val in enumerate(averageCostLst):
        if cheapestPlaceWithinDurationLst[idx][0] == val[0]:
            finalCostDict.append((val[0], "The Tax is: " + str(cheapestPlaceWithinDurationLst[idx][1]) +" And it is: " + str(cheapestPlaceWithinDurationLst[idx][2]) + " Minutes away. Average Room price is "+str(val[1]), str(((cheapestPlaceWithinDurationLst[idx][1]/100)*100000)+(val[1]*12))))

    return sorted(finalCostDict, key=lambda x: x[2])


if __name__ == '__main__':
    duration = int(input('Was ist die maximale zeit die du benutzen willst?'))
    p = Pool(10)
    # comparisRequests("zürich")
    # test = load_obj("1800ToLastBern")

    lst = readCsv("Steuersatz100.txt")
    # lst = lst[150:]
    # lst = readCsv("SteuersatzTo900.txt")
    #fz = p.map(getConnectionsFromList, lst)

    #save_obj(fz, "requests{}".format(workPlace))
    fz = load_obj("requestsBern")

    cheapestPlaceWithinDurationLst = getCheapestPlacesWithinDuration(duration, fz)
    averageCostLst = p.map(comparis.comparisRequests, cheapestPlaceWithinDurationLst[0:20])
    save_obj(averageCostLst, "cheapestHousingCostBern")
    averageCostLst = load_obj("cheapestHousingCostBern")
    print(findCheapestOverallWithTaxAndLoan(cheapestPlaceWithinDurationLst, averageCostLst))

