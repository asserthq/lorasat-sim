#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from pyquaternion import Quaternion

# %% Главная БД, + начальные значения
# ! внимательно задать типы !

# Зарезервированы имена: Manager (менеджер БД), name (имя задачи)
# нельзя чтобы имена переменных совпали с методами задач (в текущей версии менеждер перезапишет имена)
# Имена начинаются с большой буквы. Могут иметь префикс:
# префикс m-model с бортовой модели, s-sensor с датчика, o-observed наблюдаемая
# без префикса - "истинная"


class DataBase:
    # --- общие переменные ---
    t = 0.0  # время
    dt = 0.25  # шаг задач
    tmax = 500.0  # время моделирования np.pi/6 / 0.1
    cmd = 0  # команда всем задачам

    # --- пользовательские переменные ---
    # начальные значения задаются в задаче simulator.py
    Omega_B = np.zeros(3)
    Omega_I = np.zeros(3)

    Q_IB = Quaternion()  # кватернион связанной СК относительно инерциальной
    Uemu = np.zeros(3)  # управление катушками
    B_B = 40e-6 * np.array([1, 0, 0])  # МПЗ, [T]
    B_I = B_B


# задачи вызываются в порядке следования в словаре
Tasks = {
    "ADCS": {"Keys": """t,cmd,dt"""},
    "Physics": {
        "Keys": """t,cmd,dt,
                          Uemu,
                          Omega_B,Q_IB,Omega_I,
                          B_B"""
    },
    "plot3D": {
        "Keys": """t,cmd,dt,
                          Q_IB,B_I""",
        "noAnswer": True,
    },
    # "Plotter2D": {
    #     "Keys": """t,cmd,dt,
    #                       Uemu,
    #                       Omega_B,Omega_I,
    #                       B_B,B_I,
    #                       Q_IB,sQ_IB,OrbX_B,Ma_B""",
    #     "noAnswer": True,
    # },
    "Plotter2D": {
        "Keys": """t,cmd,dt,
                          Uemu,
                          Omega_B,Omega_I,
                          B_B,B_I,
                          Q_IB""",
        "noAnswer": True,
    },
}
