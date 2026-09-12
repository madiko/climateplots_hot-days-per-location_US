import requests
import json
from datetime import date
import os
import time
  
today = date.today()
datafolder = 'data'
RapidAPIKey = "<YOUR_API_KEY_HERE>", # <-- INSERT YOUR API KEY HERE !!! It looks something like this: f6e36......89caadb
url = "<YOUR_URL_HERE>" # <-- INSERT YOUR URL HERE !!!
querystring = "<YOUR_QUERYSTRING_HERE>" # <-- INSERT YOUR QUERYSTRING HERE !!!

# Examples for the URL and querystring:
#  Gerlingen (interpolated point)
#    url = "https://meteostat.p.rapidapi.com/point/daily"  
#    querystring = {"lat":"48.79954","lon":"9.06316","start":strdatestart,"end":strdateend,"alt":"336"}
#
#  Karlsruhe (Station)
#    url = "https://meteostat.p.rapidapi.com/stations/daily"
#    querystring = {"station":"10727","start":strdatestart,"end":strdateend,"model":"false"}

def downloadTimespan(yearstart: int, yearend: int):

    strmonthend = "12"
    strdayend   = "31"

    if yearend >= today.year:
        yearend = today.year
        strmonthend = f'{today.month:02d}'
        strdayend   = f'{today.day:02d}'
        
    strdatestart = str(yearstart) + "-01-01"
    strdateend   = str(yearend)   + "-" + strmonthend + "-" + strdayend

    headers = {
        "X-RapidAPI-Key": RapidAPIKey,
        "X-RapidAPI-Host": "meteostat.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    time.sleep(1)

    ret = response.json()

    if response.status_code != 200:
        print("getData: downloadTimespan: WARNING: download failed! Return Code:"+str(response.status_code))
        print("Received Response:")
        print(response)
        ret = {'data': []}

    return ret


def main():
    
    try:
        os.mkdir(datafolder)
    except OSError as error:
        print("getData: main: ERROR: folder creation failed!")
        print(error)
        quit()
    
    for year in range(1900, today.year, 5):
        print("getData: Downloading time span " + str(year) + "-" + str(year+4) + " ...")
        timespanJson = downloadTimespan(year, year+4)
        print("getData: Storing time span " + str(year) + "-" + str(year+4) + " ...")
        try:
            out_file = open(datafolder + "/" + str(year) + ".json", "w")
            json.dump(timespanJson, out_file, indent = 6)
            out_file.close()
        except OSError as error:
            print("getData: main: ERROR: Dump failed!")
            print(error)
            quit()
        print()

    print("getData: done.")
    print()


if __name__ == "__main__":
    main()
    