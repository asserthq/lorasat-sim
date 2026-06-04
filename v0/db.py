#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# %% Главная БД, + начальные значения
# ! внимательно задать типы !
# Зарезервированы имена: Manager (менеджер БД), name (имя задачи)
# нельзя чтобы имена переменных совпали с методами задач (в текущей версии менеждер перезапишет имена)
# Имена начинаются с большой буквы. Могут иметь префикс:
# префикс m-model с бортовой модели, s-sensor с датчика, o-observed наблюдаемая
# без префикса - "истинная"
from math import pi
from pathlib import Path

import numpy as np
from pyquaternion import Quaternion

# Путь к папке, где лежит текущий файл
current_dir = Path(__file__).resolve().parent

OUTPUT_DIR = current_dir / "output"


class DataBase:
    t = 0.0  # время
    dt = 0.5  # шаг задач
    tmax = 6000.0  # время моделирования
    cmd = 0  # команда всем задачам

    Omega_B = np.zeros(3)
    Omega_I = np.zeros(3)

    Q_IB = Quaternion()  # кватернион связанной СК относительно инерциальной
    Uemu = np.zeros(3)  # управление катушками
    Uemu_I = np.zeros(3)
    B_I = np.zeros(3)
    B_B = np.zeros(3)

    B_mag = np.zeros(3)


# задачи вызываются в порядке следования в словаре
Tasks = {
    "ADCS": {
        "Keys": """
            t,cmd,dt,
            B_mag,
            Uemu
        """
    },
    "Physics": {
        "Keys": """
            t,cmd,dt,
            B_B, B_I, Uemu,
            Omega_B, Q_IB, Omega_I, Uemu_I
        """
    },
    "EarthField": {
        "Keys": """
            t,cmd,dt,
            B_I
        """
    },
    "Sensors": {
        "Keys": """
            t,cmd,dt,
            B_B,
            B_mag
        """
    },
    "Plotter3D": {
        "Keys": """
            t,cmd,dt,
            Q_IB, B_I, Uemu_I
        """,
        "noAnswer": True,
    },
    "Plotter2D": {
        "Keys": """
            t,cmd,dt,
            B_B, B_mag, Omega_B, Uemu,
            B_I, Omega_I, Uemu_I, Q_IB
        """,
        "noAnswer": True,
    },
}
