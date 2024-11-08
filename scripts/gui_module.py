from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import END
from tkinter import messagebox
from tkinter import PhotoImage
import os
from pathlib import Path

import  scripts.ip_camera_shot_module as ip
import scripts.image_processor as prc
import scripts.solar_engine as eng

def main():

    cwd = os.getcwd()

    def make_photo():
        ip.capture_image()

    def process_image():
        ang = entr3.get()
        path = entr.get()

        file_path = Path(path)

        if path != "" and ang != "":
            if file_path.is_file():
                prc.image_processor(path, ang)
            else:
                messagebox.showerror("Ошибка", "Некоректный путь к файлу!")
        elif path == "":
            messagebox.showerror("Ошибка", "Укажите путь к файлу!")
            pass
        elif ang == "":
            messagebox.showerror("Ошибка", "Введите номинальный угол камеры рыбьего глаза!")
            pass

    def process_solar():
        file_path = Path("./temp/processed_data.csv")
        crd = entr2.get()
        start = entr4.get()
        end = entr5.get()
        shape = entr6.get()
        KPD = entr7.get()

        if file_path.is_file():
            if crd == "":
                messagebox.showerror("Ошибка", "Введите координаты!")
                pass
            eng.solar_processor(crd, start, end, shape, KPD)
        else:
            messagebox.showerror("Ошибка", "Выполните обработку изображения!")
            

    root = Tk()
    root.title("SunEyeZ")
    root.geometry("400x400")
    root.resizable(False, False)

    icon = PhotoImage(file="./data/ui/ZZ.png")

    root.iconphoto(False, icon)

    btn = ttk.Button(text="Сделать фото", command=make_photo)
    btn.pack()

    # Первый фрейм для пути к файлу
    frame = ttk.Frame(borderwidth=1, relief=SOLID, padding=[8, 10])
    frame.pack(anchor=NW, fill=X, padx=5, pady=5)

    label = ttk.Label(frame, text="Путь к файлу: ")
    label.grid(row=0, column=0)

    entr = ttk.Entry(frame)
    entr.grid(row=0, column=1)

    def load_image():
        entr.delete(0, END)
        filename = filedialog.askopenfile(initialdir=cwd, title="Choose photo", filetypes=(("Images", "*.jpg"),))
        if filename:  # Проверка, что файл выбран
            entr.insert(0, filename.name)

    btn_2 = ttk.Button(frame, text="Загрузить изображение", command=load_image)
    btn_2.grid(row=0, column=2)

    # Второй фрейм для угла
    frame3 = ttk.Frame(borderwidth=1, relief=SOLID, padding=[8, 10])
    frame3.pack(anchor=NW, fill=X, padx=5, pady=5)

    label3 = ttk.Label(frame3, text="Номинальный угол камеры рыбьего глаза:")
    label3.grid(row=0, column=0)

    entr3 = ttk.Entry(frame3)
    entr3.grid(row=0, column=1)

    # Кнопка для обработки изображения
    btn_3 = ttk.Button(text="Выполнить обработку изображения", command=process_image)
    btn_3.pack()

    # Третий фрейм для физических данных
    frame2 = ttk.Frame(borderwidth=1, relief=SOLID, padding=[8, 10])
    frame2.pack(anchor=NW, fill=X, padx=5, pady=5)

    label2 = ttk.Label(frame2, text="Географические координаты:")
    label2.grid(row=0, column=0)

    entr2 = ttk.Entry(frame2)
    entr2.grid(row=0, column=1)

    label4 = ttk.Label(frame2, text="**Начало периода отсчёта:")
    label4.grid(row=1, column=0)

    entr4 = ttk.Entry(frame2)
    entr4.grid(row=1, column=1)

    label5 = ttk.Label(frame2, text="**Конец периода отсчёта:")
    label5.grid(row=2, column=0)

    entr5 = ttk.Entry(frame2)
    entr5.grid(row=2, column=1)

    # Четвёртый фрейм для данных панели
    frame4 = ttk.Frame(borderwidth=1, relief=SOLID, padding=[8, 10])
    frame4.pack(anchor=NW, fill=X, padx=5, pady=5)

    label6 = ttk.Label(frame4, text="**Площадь панели (кв. м.):")
    label6.grid(row=0, column=0)

    entr6 = ttk.Entry(frame4)
    entr6.grid(row=0, column=1)

    label7 = ttk.Label(frame4, text="**КПД модуля (%):")
    label7.grid(row=1, column=0)

    entr7 = ttk.Entry(frame4)
    entr7.grid(row=1, column=1)


    btn_4 = ttk.Button(text="Выполнить расчёт", command=process_solar)
    btn_4.pack()

    root.mainloop()
