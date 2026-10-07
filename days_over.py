import json
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.cm as cm
from scipy.optimize import curve_fit
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import FancyArrowPatch

input_json_file = "merged.json"  # JSON-Datei mit den Wetterdaten (Pfad: relativ zum Skript)
locationName = "Name der Stadt"  # Name des Ortes, der in den Diagrammen angezeigt wird
outputFunction = False  # True -> Namen der Fitfunktion wird ausgegeben
outputParams = False    # True -> Fit-Parameter werden ausgegeben
outputQuality = False   # True -> R²-Werte werden ausgegeben
drawArrow = True       # True -> Pfeil wird gezeichnet, der die Zunahme der Hitzetage über die Zeit anzeigt
drawMultiplier = True  # True -> Vervielfachungsfaktor wird im Diagramm angezeigt


# Die Fit-Funktion ist mathematisch-physikalisch motivierte Funktion, die die Anzahl der Tage mit Temperaturen über einem bestimmten Schwellenwert modelliert.
# Das zugrundeliegende Modell geht von folgenden Annahmen aus:
# 1. Die Verteilung der täglichen Maximaltemperaturen folgt einer Normalverteilung, die sich im Laufe der Zeit verschiebt.
#    Daraus ergibt sich dass die Anzahl der Tage mit Temperaturen über einem bestimmten Schwellenwert (z.B. 30°C) einer Sigmoid-Kurve (logistische Funktion) folgt.
# 2. Die Verschiebung der Normalverteilung erfolgt in drei Phasen:
#    a) bis zum Jahr t0: keine Klimaveränderung ("vorindustrielle Zeit")
#    b) zwischen den Jahren t0 und t1: kurze Phase mit exponentieller Veränderung der Temperaturanomalie ("Beschleunigungsphase")
#    c) ab dem Jahr t1: lineare Klimaveränderung (konservative Annahme, dass aktuell die Erderwärmung linear verläuft)
#    Diese drei Phasen werden realisiert, indem das Argument (shift) der logistischen Funktion aus einer stetig differenzierbaren abschnittsweise
#    definierten Funktion zusammengesetzt wird: konsant bis t0, exponentiell zwischen t0 und t1, linear ab t1.
# 3. Klimamoden auf Zeitskalen von wenigen Jahren werden wie statistische Schwankungen behandelt und nicht modelliert.
#    Die Fit-Funktion modelliert nur den langfristigen Trend.
# Das Modell nimmt nicht an, dass sich das Klima erwärmt. Es ist auch kompatibel mit einer Abkühlung oder einem konstanten Klima.
def fit_func(t, h0, t0, Deltat, nd, m):
    t1 = t0 + Deltat # Ende der Beschleunigungsphase
    d = Deltat / nd # Verdopplungszeit
    a = (m * d / np.log(2)) * np.exp(-1 * np.log(2) * Deltat / d) # Amplitude der exponentiellen Zunahme
    y0 = -1 * np.log(365 / h0 - 1) # shift-Wert vor der Beschleunigungsphase, der der vorindustriellen Anzahl an Hitzetagen entspricht
    conditions = [t <= t0, 
                  (t0 < t) & (t <= t1), 
                  t > t1]
    choices = [y0, 
               y0 + a * (np.exp(np.log(2) * (t - t0) / d) - 1), 
               y0 + a * (np.exp(np.log(2) * Deltat / d) - 1) + m * (t - t1)]
    # shift = Maß für die Temperaturanomalie, normiert auf eine Erhöhung von 1 Tag pro Jahr für Tage mit Temperatuen > der Durchschnittstemperatur im Jahr t0 
    shift = np.select(conditions, choices)
    return 365 / (1 + np.exp(-1 * shift))


def generate_weather_plots(json_filepath, output_folder="./wetter_plots"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Lese JSON-Datei ein...")
    with open(json_filepath, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year

    all_years = sorted(df["year"].unique())
    # Beschränkung auf 30 bis 35 Grad (6 Werte)
    thresholds = list(range(30, 36))

    max_year = (max(all_years) // 10) * 10
    decade_ticks = np.arange(1900, max_year + 11, 10)

    # Farbverlauf für genau 6 Werte
    colors = cm.autumn(np.linspace(0, 1, len(thresholds)))

    special_fits_data = {}
    multipliers_data = {}
    global_X_smooth = None

    for idx, thresh in enumerate(thresholds):
        print(f"Verarbeite Schwellenwert: {thresh}°C...")

        df_filtered = df[df["tmax"] > thresh]
        yearly_counts = df_filtered.groupby("year").size().reindex(all_years, fill_value=0)

        X = np.array(yearly_counts.index)
        Y = np.array(yearly_counts.values)

        X_smooth = np.linspace(max(1900, X.min()), X.max(), 300)
        if global_X_smooth is None:
            global_X_smooth = X_smooth

        fig, ax = plt.subplots(figsize=(24, 24))
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')

        ax.tick_params(colors='white', which='both', labelsize=48, width=4, length=16, pad=15)
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
            spine.set_linewidth(4)
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')

        ax.bar(X, Y, color="#5dade2", alpha=0.7, edgecolor="none", label=f"Tage > {thresh}°C")

        # Fitparameter: p = [y0, t0, Deltat, d, m]
        # y0: vorindustrielle durchschnittliche jährl. Anzahl an Hitzetagen, die bis zur Beschleunigung des Temperaturanstiegs konstant bleibt
        # t0: das Jahr, in dem die Temperatur beginnt anzusteigen (Beschleunigung des Temperaturanstiegs)
        # Deltat: Anzahl der Jahre, die der Temperaturanstieg nach t0 beschleunigt
        # nd: Härte der exponentiellen Zunahme. (Anzahl der Verdoppelungen der Temperaturanomalie während der Beschleunigungsphase)
        # m: Steigung der linearen Temperaturzunahme nach der Beschleunigungsphase.
        #    (m = 1 bedeutet, dass die Anzahl der Tage mit Temperaturen > der Durchschnittstemperatur des Jahres t0+Deltat
        #     nach der Beschleunigungsphase linear um 1 Tag pro Jahr zunimmt)
        # Startwerte für die Parameter:
        p_init = [5, 1950, 30, 4, 0.1]
        # Grenzen für die Parameter (pmin, pmax)
        p_bounds = ([0, 1900, 30, 2, -1], [364, 1970, 50, 5, 1])

        fit_text = ""
        try:
            popt_fit, _ = curve_fit(fit_func, X, Y, p0=p_init, bounds=p_bounds, maxfev=50000, x_scale='jac')
            
            # R² berechnen
            Y_fit = fit_func(X, *popt_fit)
            ss_res = np.sum((Y - Y_fit) ** 2)
            ss_tot = np.sum((Y - np.mean(Y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            
            # Smooth Plot 
            Y_smooth = fit_func(X_smooth, *popt_fit)
            ax.plot(X_smooth, Y_smooth, color=colors[idx], linewidth=8.0, label="Trend")
            special_fits_data[thresh] = Y_smooth
            
          
            if drawArrow or drawMultiplier:
                if Y_smooth[0] != 0:
                    multiplier = Y_smooth[-1] / Y_smooth[0]
                else:
                    multiplier = 9999 # sollte eigentlich nicht vorkommen
                multipliers_data[thresh] = multiplier
            
            if drawArrow:
                # Pfeil zeichnen
                x_span = X[-1] - X[0]
                y_span_fit = max(Y_smooth) - min(Y_smooth) if max(Y_smooth) > min(Y_smooth) else 1.0
                dx_right = x_span * 0.1
                dx_left = x_span * 0.2
                dy = y_span_fit * 0.4
                x_start = X[0] + dx_left
                y_start = Y_smooth[0] + dy
                x_end = X[-1] - dx_right
                y_end = Y_smooth[-1]
                curve_color = colors[idx]
                arrow = FancyArrowPatch(
                    (x_start, y_start), (x_end, y_end),
                    connectionstyle="angle3,angleA=45,angleB=0",
                    arrowstyle="->,head_length=8,head_width=4",
                    linestyle=":",
                    color=curve_color,
                    linewidth=5,
                    mutation_scale=5
                )
                ax.add_patch(arrow)
                if np.abs(multiplier - np.round(multiplier)) >= 0.25:  
                    text_str = f"\u00d7 {multiplier:.1f}"
                else:
                    text_str = f"\u00d7 {multiplier:.0f}"
                x_text = (x_start + 3*x_end) / 4
                y_limits = ax.get_ylim()
                y_axis_span = y_limits[1] - y_limits[0]
                y_text = max(y_start, y_end) + (y_axis_span * 0.02)
                ax.text(
                    x_text, y_text, text_str,
                    color=curve_color,
                    backgroundcolor='black',
                    fontsize=42,
                    fontweight="bold",
                    ha="center",
                    va="bottom"
                )
            
            # Text mit Fit-Parametern und R² zusammenstellen
            h0_fit, t0_fit, Deltat_fit, nd_fit, m_fit = popt_fit
            if outputFunction:
                fit_text = (f"Fit: Sigmoid(Temperaturanomalie(Zeit))\n"
                            f"      mit Anomalie = konst. -> exp. -> lin.\n")
            if outputParams:
                if not outputFunction:
                    fit_text = f"Fit-Parameter:\n"
                fit_text += (f"  vorindustrielle Anzahl: {h0_fit:.1f} Tage\n"
                             f"  Startjahr der Beschleunigung: {t0_fit:.0f}\n"
                             f"  Dauer der Beschleunigung: {Deltat_fit:.0f} Jahre\n"
                             f"  Härte der Beschleunigung: {nd_fit:.1f} Verdoppelungen\n"
                             f"  lineare Zunahme nach Beschl.: {m_fit:.2f}\n")
            if outputQuality:
                fit_text += f"Fit-Qualität: R² = {r_squared:.4f}"
            
        except Exception as e:
            print(f"  -> Spezial-Fit für {thresh}°C fehlgeschlagen: {e}")
            fit_text = "Fit fehlgeschlagen"

        ax.set_title(f"Anzahl der Tage pro Jahr in {locationName}\nmit Temperaturen über {thresh}°C", fontsize=64, fontweight="bold", pad=40)
        ax.set_xlabel("Jahr", fontsize=56, labelpad=20)
        ax.set_xticks(decade_ticks)
        ax.set_xticklabels(decade_ticks, rotation=45)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True, steps=[1, 2, 5, 10]))
        ax.grid(axis="y", linestyle=":", alpha=0.3, color="white", linewidth=4)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], loc="upper left", frameon=True, facecolor="black", edgecolor="white", labelcolor="white", fontsize=48)
        plt.tight_layout(pad=3.0, rect=[0, 0.15, 1, 1])
        fig.text(0.05, 0.16, fit_text, ha="left", va="top", fontsize=30, color="white", alpha=0.7)
        fig.text(0.7, 0.16, "Datenquelle: meteostat.net", ha="left", va="top", fontsize=30, color="white", alpha=0.7)

        output_filename = os.path.join(output_folder, f"wetter_trend_{thresh}C.png")
        plt.savefig(output_filename, dpi=150, facecolor=fig.get_facecolor())
        plt.close()

    # Zusammenfassung der Trends
    if special_fits_data:
        fig, ax = plt.subplots(figsize=(24, 24))
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        ax.tick_params(colors='white', which='both', labelsize=48, width=4, length=16, pad=15)
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
            spine.set_linewidth(4)
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')

        for idx, thresh in enumerate(thresholds):
            if thresh in special_fits_data:
                ax.plot(global_X_smooth, special_fits_data[thresh], color=colors[idx], linewidth=8.0, label=f"> {thresh}°C")

        ax.set_title(f"Anzahl der Tage pro Jahr in {locationName}\nmit Temperaturen über 30°C ... 35°C", fontsize=72, fontweight="bold", pad=40)
        ax.set_xlabel("Jahr", fontsize=56, labelpad=20)
        ax.set_ylim(0, None)
        ax.set_xticks(decade_ticks)
        ax.set_xticklabels(decade_ticks, rotation=45)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True, steps=[1, 2, 5, 10]))
        ax.grid(axis="y", linestyle=":", alpha=0.3, color="white", linewidth=4)
        ax.grid(axis="x", linestyle=":", alpha=0.3, color="white", linewidth=4)
        ax.legend(loc="upper left", frameon=True, facecolor="black", edgecolor="white", labelcolor="white", fontsize=48)
        plt.tight_layout(pad=3.0, rect=[0, 0.04, 1, 1])
        fig.text(0.7, 0.02, "Datenquelle: meteostat.net", ha="left", va="bottom", fontsize=30, color="white", alpha=0.7)

        combined_filename = os.path.join(output_folder, "wetter_trend_alle_schwellwerte.png")
        plt.savefig(combined_filename, dpi=150, facecolor=fig.get_facecolor())
        plt.close()
        
    # Zusammenfassung der Vervielfachungsfaktoren
    if multipliers_data:
        fig, ax = plt.subplots(figsize=(24, 24))
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        ax.tick_params(colors='white', which='both', labelsize=48, width=4, length=16, pad=15)
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
            spine.set_linewidth(4)
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')

        # Daten filtern und vorbereiten (nur erfolgreich gefittete Schwellenwerte)
        x_labels = [f">{thresh} °C" for thresh in thresholds if thresh in multipliers_data]
        y_values = [multipliers_data[thresh] for thresh in thresholds if thresh in multipliers_data]
        bar_colors = [colors[idx] for idx, thresh in enumerate(thresholds) if thresh in multipliers_data]

        # Bar-Plot
        bars = ax.bar(x_labels, y_values, color=bar_colors, edgecolor="none", width=0.6)
        ax.set_title(f"Vervielfachung der Hitzetage\n (Tage mit Temperaturen über ... °C)\ndurch die Erderwärmung in {locationName}", fontsize=64, fontweight="bold", pad=40)
        ax.set_ylabel("Vervielfachung der jährlichen Hitzetage", fontsize=56, labelpad=20)
        ax.set_xlabel("Hitzetag-Temperatur", fontsize=56, labelpad=20)
        ax.grid(axis="y", linestyle=":", alpha=0.3, color="white", linewidth=4)
        for bar in bars:
            height = bar.get_height()
            # Falls ein Fit fehlschlug und der Dummy-Wert 9999 aktiv ist, diesen überspringen
            if height < 9000:
                ax.annotate(f"\u00d7{height:.1f}",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 15),  # 15 Punkte Abstand nach oben
                            textcoords="offset points",
                            ha='center', va='bottom', 
                            fontsize=48, color='white', fontweight='bold')
        if y_values:
            valid_values = [v for v in y_values if v < 9000]
            if valid_values:
                ax.set_ylim(0, max(valid_values) * 1.15)
        plt.tight_layout(pad=3.0, rect=[0, 0.04, 1, 1])
        fig.text(0.7, 0.02, "Datenquelle: meteostat.net", ha="left", va="bottom", fontsize=30, color="white", alpha=0.7)

        summary_bar_filename = os.path.join(output_folder, "wetter_trend_vervielfachung.png")
        plt.savefig(summary_bar_filename, dpi=150, facecolor=fig.get_facecolor())
        plt.close()

if __name__ == "__main__":
    if os.path.exists(input_json_file):
        generate_weather_plots(input_json_file)
        print("\nFertig!")
