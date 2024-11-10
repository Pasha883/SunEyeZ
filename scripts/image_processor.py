import numpy as np
from scipy.signal import medfilt
import cv2
import pathlib
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import PhotoImage
import pvlib
import datetime

import scripts.solar_engine as eng


def image_processor(path, ang, cords):
    #plt.clf()

    #Инициализируем данные
    angle = int(ang)

    cords_str = str.split(cords, ", ")
    cords = [float(num) for num in cords_str]

    alt = eng.get_elevation(cords[0], cords[1])

    loc = pvlib.location.Location(
                                    cords[0], 
                                    cords[1], 
                                    tz='Europe/Moscow', 
                                    altitude=alt, 
                                    name='loc')
    
    times = pd.date_range(start=datetime.datetime(2021,6,20), # Момент начала периода моделирования
             end=datetime.datetime(2021,6,21), # Момент окончания периода моделирования
             freq='1h') # Дискретность моделирования
    
    times_loc = times.tz_localize(tz=loc.tz)

    times2 = pd.date_range(start=datetime.datetime(2021,12,20), # Момент начала периода моделирования
             end=datetime.datetime(2021,12,21), # Момент окончания периода моделирования
             freq='1h') # Дискретность моделирования
    
    times_loc2 = times2.tz_localize(tz=loc.tz)

    SPA1 = pvlib.solarposition.spa_python(times_loc, 
                                     loc.latitude, 
                                     loc.longitude, 
                                     altitude=loc.altitude)
    
    SPA2 = pvlib.solarposition.spa_python(times_loc2, 
                                     loc.latitude, 
                                     loc.longitude, 
                                     altitude=loc.altitude)
    ##############
    

    #Стартовая обработка изображения
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 1, 200)
    edges = cv2.Canny(gray, 1, 200)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    ##############

    # Находим контуры
    contours = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    ##############

    #Отделяем самые крупные контуры
    fin_contours = []
    result = img.copy()
    i = 1

    fin_contours = sorted(contours, key=lambda x: cv2.arcLength(x, True), reverse=True)
    
    """
    for c in contours:
        perimeter = cv2.arcLength(c, True)
        if perimeter > 10000: 
            cv2.drawContours(result, c, -1, (0,255), 1)
            contour_img = np.zeros_like(img, dtype=np.uint8)
            cv2.drawContours(contour_img, c, -1, (0,0,255), 1)
            cv2.imwrite("temp/short_title_contour_{0}.jpg".format(i),contour_img)
            fin_contours.append(c)
        i = i + 1
    """
    ##############
    
    #Узнаём реальный радиус окружности фишая
    i = int(gray.shape[0] / 2) 
    j = 0
    px = 0
    while px==0:
        j += 1
        px = gray[i, j]

    mid = (img.shape[1] / 2, img.shape[0] / 2 )

    r = mid[0] - j
    ##############
    

    #Определяем угловые размеры каждой точки контура
    countour = np.round(fin_contours[1].reshape(fin_contours[1].shape[0], 2))
      

    lst = []
    for contour_dot in countour:
        lst.append(90 - (((mid[0] - contour_dot[0])**2 + (mid[1] - contour_dot[1])**2)**0.5)/r * angle/2) 
    ##############
    
    #Отрисовываем изображение с контуром и координатами
    res = img.copy()
    cv2.drawContours(res, fin_contours, 1, (0,0,255), 2)
 
    r = np.ones(90)

    fig = plt.gcf()
    axes_coords = [0.15, 0.03, 0.7, 0.95]
    ax_polar = fig.add_axes(axes_coords, projection = 'polar', zorder=2)
    ax_polar.patch.set_alpha(0.1)
    ax_polar.set_rmin(90)
    ax_polar.set_rmax(90 - angle/2)
    ax_polar.set_rticks(np.append(np.arange(90 - angle/2, 90, 15), 90))
    ax_polar.set_theta_zero_location("N")
    ax_image = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax_image.imshow(res, alpha = .6, zorder=1)
    ax_image.set_axis_off()
    fig.canvas.manager.set_window_title("Обработанное изображение")
    ##############
    
    #Определяем азимут каждой точки контура и производим сортировку значений
    azimuth = []
    for point in countour:
        a = abs(mid[0] - point[0])
        b = abs(point[1] - mid[1])
        if point[0] - mid[0] < 0 and point[1] - mid[1] < 0:
            azimuth.append(np.rad2deg(np.arctan(a/b)))

        elif point[0] - mid[0] < 0 and point[1] - mid[1] > 0:
            azimuth.append(180 - np.rad2deg(np.arctan(a/b)))
        
        elif point[0] - mid[0] > 0 and point[1] - mid[1] > 0:
            azimuth.append(180 + np.rad2deg(np.arctan(a/b)))
        
        else:
            if b == 0:
                azimuth.append(360)
                continue

            azimuth.append(360 - np.rad2deg(np.arctan(a/b)))

    res = []
    for val1, val2 in zip(azimuth, lst):
        res.append([val1, val2])

    res = np.asarray(res)
    res = res[res[:, 0].argsort()]
    res = np.round(res)
    ##############

    #Сохраняем данные обработки
    df = pd.DataFrame(res, columns=["Azimuth", "Elevation"])
    df.to_csv("./temp/processed_data.csv")
    ##############

    print("Done")

    #Отрисовываем полученные данные
    fig, ax = plt.subplots()
    ax.plot(res[:, 0], res[:,1])
    ax.plot(SPA1["azimuth"], SPA1["elevation"])
    ax.plot(SPA2["azimuth"], SPA2["elevation"])
    fig.canvas.manager.set_window_title("Перевод в Декартову систему координат")
    ax.set_ylim((0, 90))
    ax.fill_between(res[:, 0], res[:, 1], 0)
    plt.show()
    ##############

    plt.clf()
    ax.cla()
    fig.clf()

