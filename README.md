# ClimatePlots DaysOver: Heiße Tage pro gewähltem Standort

ClimatePlots DaysOver generiert "Heiße Tage" für einzelne, frei wählbare Wetter-Stationen.  
Quelle Daten: [MeteoStat](https://meteostat.net/de).

Vorschau auf ein mögliches Ergebnis:

<img width="1000" height="1000" alt="Wetter Trend spezial mit allen Schwell-Werten ab 30°C" src="https://github.com/user-attachments/assets/cdfbfaa7-dd25-4a38-b60d-b4c941d3213c" />


## Wie nutzen?

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

