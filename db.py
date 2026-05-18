#!/usr/bin/env python3
# -*- coding: utf-8 -*-                      """ База данных и задач диспетчера """
import numpy as np


class DataBase:
    # --- общие переменные ---
    t = 0.0  # время
    dt = 1.0 / 60  # шаг задач
    tmax = 120.0  # время моделирования
    cmd = 0  # команда всем задачам

    w = -0.25  # угловая скорость, рад/с
    phi = 0.0  # угол, рад
    Q_IB = np.array([1, 0, 0, 0])
    # псевдотрехмерные - только для отработки алгоритмов
    B = 41e-6 * np.array([np.cos(phi), np.sin(phi), 0])  # МПЗ, T
    U = 0.0  # управление

    # датчики
    B_QMC = np.zeros(3)
    B_MPU = np.zeros(3)
    W_MPU = np.zeros(3)
    A_MPU = np.zeros(3)


# Список задач
# задачи вызываются в порядке следования в словаре
# выполняются параллельно - в смысле модельного времени
Tasks = {
    "ADCS": {"Keys": "t,cmd"},
    # 'Emulator': {'Keys':"""t,cmd,
    #                        B_QMC,B_MPU,W_MPU,A_MPU,
    #                        U""",
    #               'Addr':('192.168.43.77', 6502)},
    "Simulator": {
        "Keys": """t,cmd,
                           B_QMC,B_MPU,W_MPU,A_MPU,
                           U"""
    },
}
