0. kostenlosen Basic-Account auf RapidAPI erstellen und API-Key erzeugen: https://dev.meteostat.net/api
1. RapidAPIKey in getData.py anpassen
2. Wenn Daten einer konkreten offiziellen Wetterstation verwendet werden sollen:
   Stationsnummer auf https://meteostat.net/de/ herausfinden und
   in getData.py "https://meteostat.p.rapidapi.com/stations/daily" als URL
   und den Querystring mit der Stationsnummer eintragen.
   Wenn stattdessen Daten verwendet werden sollen, die für einen beliebigen geografischen Ort aus den umliegenden Wetterstationen interpoliert werden:
   in getData.py "https://meteostat.p.rapidapi.com/point/daily" als URL
   und den Querystring mit der Geolocation eintragen.
3. getData.py ausführen
4. mergeData.py ausführen
5. Einstellungen in days_over.py anpassen
6. days_over.py ausführen

