#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощённая дипольная модель магнитного поля Земли.
Поле вычисляется в инерциальной системе координат (J2000 Earth Inertial).
Орбита предполагается круговой, в экваториальной плоскости, высота 550 км.
Ось магнитного диполя совпадает с осью Z инерциальной СК (ось вращения Земли).
"""

from importlib import reload

import db
import numpy as np
from pysimscheduler import libKernel

# Магнитная постоянная / 4π
MU0_4PI = 1e-7  # Тл·м/А

# Параметры Земли и орбиты
R_E = 6371e3  # радиус Земли, м
H = 550e3  # высота орбиты, м
R = R_E + H  # радиус орбиты, м
M_E = 7.84e22  # магнитный дипольный момент Земли, А·м²

# Гравитационная постоянная Земли (м³/с²)
MU = 3.986e14

# Среднее движение (рад/с) для высоты 550 км
n = np.sqrt(MU / R**3)  # ≈ 1.097e-3 рад/с
T_ORBIT = 2 * np.pi / n  # период, ≈ 5730 с

# Наклонение солнечно-синхронной орбиты для 550 км (в радианах)
INCLINATION_DEG = 97.6  # градусы
INCLINATION = np.radians(INCLINATION_DEG)


class EarthField(libKernel.TaskTemplate):
    """Модель магнитного поля Земли (осевой диполь)."""

    def Setup(self):
        # Начальная фаза (аргумент широты) в момент t=0
        self.u0 = 0.0
        # Ось диполя (по Z инерциальной системы)
        self.dipole_axis = np.array([0, 0, 1])

    def Initialize(self):
        self.u0 = 0.0

    def Run(self):
        tboost = 1
        # Аргумент широты (орбитальная фаза)
        u = n * self.t * tboost + self.u0

        # Радиус-вектор КА в инерциальной СК
        r_vec = R * np.array(
            [
                np.cos(u),
                np.sin(u) * np.cos(INCLINATION),
                np.sin(u) * np.sin(INCLINATION),
            ]
        )
        r_hat = r_vec / R

        # Вектор магнитного момента Земли
        m_vec = M_E * self.dipole_axis

        # Дипольное поле: B = μ0/(4π) * (3 (m·r̂) r̂ - m) / r³
        m_dot_r_hat = np.dot(m_vec, r_hat)
        B_I = (MU0_4PI / R**3) * (3 * m_dot_r_hat * r_hat - m_vec)

        # Запись в общую базу данных
        self.B_I = B_I


# % Главный цикл
reload(db)
model = EarthField(TaskList=db.Tasks, DB=db.DataBase())
model.Manager.Loop()
