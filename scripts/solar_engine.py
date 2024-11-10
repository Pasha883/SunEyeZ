import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import pvlib
import ephem
import requests
import math
import numpy as np

import scripts.gui_module as gui


def get_elevation(lat, lon):
    try:
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
        response = requests.get(url)
        if response.status_code == 200:
            elevation_data = response.json()
            elevation = elevation_data['results'][0]['elevation']
            return elevation
        else:
            return None
    except:
        return None

def solar_processor(cord, start1, end1, shape1, KPD1, tarif1):
    #Инициализируем данные
    shape = 1
    KPD = 100
    tarif = 6.73

    if shape1 != "":
        shape = float(shape1)
    if KPD1 != "":
        KPD = int(KPD1)
    if tarif1 != "":
        tarif = float(tarif1)

    start = datetime.today()
    end = start + timedelta(days=1)

    if start1 != "" and end1 != "":
        start = pd.to_datetime(start1)
        end = pd.to_datetime(end1)

    camera_data = pd.read_csv("./temp/processed_data.csv")
    camera_data = camera_data.apply(pd.to_numeric, errors='coerce')
    gui.progress_plus(10)

    cords_str = str.split(cord, ", ")
    cords = [float(num) for num in cords_str]

    alt = get_elevation(cords[0], cords[1])
    alt = 0 if alt == None else alt
    ##############

    loc = pvlib.location.Location(cords[0], 
                                cords[1], 
                                tz='Europe/Moscow', 
                                altitude=alt, 
                                name='Moscow')


    times = pd.date_range(start=start, # Момент начала периода моделирования
             end=end, # Момент окончания периода моделирования
             freq='1h') # Дискретность моделирования
    
    # "Локализация" моентов времени
    times_loc = times.tz_localize(tz=loc.tz)

    #Определение положения солнца на небосводе
    SPA = pvlib.solarposition.spa_python(times_loc, 
                                     loc.latitude, 
                                     loc.longitude, 
                                     altitude=loc.altitude)
    
    SPA['azimuth'] = SPA['azimuth'].round()

    SPA_copy = SPA.copy()
    gui.progress_plus(10)
    ##############

    #print(SPA)

        
    for index, row in camera_data.iterrows():
        value_A = row["Azimuth"]
        elevation = row["Elevation"]
        
        if value_A in SPA['azimuth'].values:
            # Получаем соответствующие значения из 'apparent_elevation' для `value_A`
            sort = SPA.loc[SPA['azimuth'] == value_A]
            times = sort.index
            
            # Проверяем, если все значения меньше `row["Elevation"]`
            for time in times:
                cur = SPA.loc[(SPA['azimuth'] == value_A) & (SPA.index ==time)]
                if ((cur["elevation"] < elevation).all()):
                    # Только для строк с этим `value_A` изменяем значение `apparent_elevation` на 0
                    SPA.loc[(SPA['azimuth'] == value_A) & (SPA.index == time), 'apparent_elevation'] = 0
        gui.progress_plus(100/len(camera_data))           

    SPA['apparent_elevation'] = SPA['apparent_elevation'].clip(lower=0)

    DNI_extra = pvlib.irradiance.get_extra_radiation(times_loc, # Расчёт методом Specer
                                                 solar_constant=1366.1, 
                                                 method='spencer')
    
    gui.progress_plus(10)
    
    #Простая модель атмосферы    
    VerySimpleClearSky = pvlib.clearsky.simplified_solis(SPA['apparent_elevation'], 
                                                     aod700=0.1, 
                                                     precipitable_water=1.0, 
                                                     pressure=101325.0, 
                                                     dni_extra=DNI_extra)
    ##############

    gui.progress_plus(10)
    

    VerySimpleClearSky['ghi'].plot(label='GHI') 
    plt.grid(linestyle='--')
    plt.legend()
    plt.ylabel('Интенсивность солнечного излучения, Вт/кв.м')
    plt.xlabel('Время')
    plt.title('Приход солнечной радиации на горизонтальную площадку')    

    fig = plt.gcf()        
    ax = fig.gca()       

    line = ax.lines[0]
    time_values = line.get_xdata() 
    radiation_values = line.get_ydata()
    time_values = [pd.Timestamp(t.to_timestamp()) if isinstance(t, pd.Period) else pd.Timestamp(t) for t in time_values]
    time_values = pd.DatetimeIndex(time_values).tz_localize(None)
    time_values_hours = time_values.astype('int64') / 3_600_000_000_000 
    positive_radiation = np.maximum(0, radiation_values)
    total_radiation = np.trapz(positive_radiation, x=time_values_hours)

    gui.progress_plus(10)

    gui.show_text_window(round(total_radiation / 1000, 2), round(total_radiation * KPD * shape / 100 / 1000, 2), round(total_radiation * KPD * shape / 100 * tarif / 1000, 2))

    print("Суммарная солнечная радиация за период (кВт*ч/м²):", total_radiation / 1000)
    print("Количество вырабатанной энергии с учётом КПД (кВт*ч):", total_radiation * KPD * shape / 100 / 1000)
    print("Стоимость вырабатанной энергии (руб):", total_radiation * KPD * shape / 100 * tarif / 1000)

    gui.show_plot_in_window(plt, "Солнечная радиация")

    gui.progress_plus(-150)

    

    
    
