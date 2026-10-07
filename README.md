# ClimatePlots DaysOver: Heiße Tage pro gewähltem Standort

ClimatePlots DaysOver generiert "Heiße Tage" für einzelne, frei wählbare Wetter-Stationen.  
Quelle Daten: [MeteoStat](https://meteostat.net/de).

Vorschau auf ein mögliches Ergebnis:

<img width="1000" height="1000" alt="Wetter Trend spezial mit allen Schwell-Werten ab 30°C" src="/media/wetter_trend_special_alle_schwellenwerte.png" />


## Wie nutzen?

### Acount via MeteoStat anlegen

Vorbereiten: 

- kostenlosen Basic-Account auf RapidAPI erstellen.
- API-Key erzeugen: https://dev.meteostat.net/api
- RapidAPIKey in `getData.py` anpassen

### Daten holen

#### Daten einer konkreten, offiziellen Wetter-Station

Wenn Daten einer konkreten offiziellen Wetterstation verwendet werden sollen:

- Stationsnummer auf https://meteostat.net/de/ herausfinden und
- in `getData.py` eintragen:
   - URL: `https://meteostat.p.rapidapi.com/stations/daily`  
   - Query-String: Stationsnummer  

#### Daten eines beliebigen geografischen Orts und umliegende Wetter-Stationen interpolieren

Wenn stattdessen Daten verwendet werden sollen, die für einen beliebigen geografischen Ort aus den umliegenden Wetterstationen interpoliert werden:

- in `getData.py` eintragen:
   - URL: `https://meteostat.p.rapidapi.com/point/daily`
   - Query-String: Geolocation des Orts

### Gewünschte Einstellungen für Ergebnis-Plot

Einstellungen in days_over.py anpassen  


#### Scripte ausführen

1. getData.py  
2. mergeData.py  
3. days_over.py ausführen


## Lizenz 

Bitte ergänzen 