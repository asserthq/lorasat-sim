#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модель вращательного движения в трёхмерном пространстве кубсата, 3D

- Только магнитные катушки (ЭМУ)
- астродинамика упрощённая

Ядро модели составляют два уравнения:
1. уравнение динамики, по которому рассчитывается угловая скорость $\omega^B$ и
2. уравнение кинематики, по которому получается кватернион поворота связанной системы координат $\Lambda^{IB}$ относительно инерциального пространства I.

Физику поворотов проверил. Кватернионы ковариантные.
"""

from cmath import pi
from importlib import reload

import db
import numpy as np
from pyquaternion import Quaternion
from pysimscheduler import libADCSMini as libADCS
from pysimscheduler import libKernel
from scipy.integrate import odeint

X_I, Y_I, Z_I = libADCS.X, libADCS.Y, libADCS.Z
NORM_STEP = 15  # шаг нормировки кватерниона
N_STEPS = 5  # колво шагов по времени, НОД(T1,Tcycle) в class EMUs

OMEGA_INIT = np.array([(pi / 6) / (3**0.5), (pi / 6) / (3**0.5), (-pi / 6) / (3**0.5)])
# OMEGA_INIT = np.zeros(3)


class EMUs:
    def __init__(self, T1=0.15, Tcycle=0.2):
        """модель ЭМУ. Катушки расположены пАрами, по строительным осям КА (по осям ССК / B)
        ЭМУ работает часть (время Т1) цикла СОС (Tcycle)
        """
        # катушек - пара на ось
        self.kEMU = 2 * 0.2  # коэфф. катушек, u(-1..+1) -> L [А*м2]
        self.T1 = T1
        self.Tcycle = Tcycle
        self.On = True
        self.U = np.zeros(3)  # Управление [-1..+1]
        self.R = 40  # сопротивление одной катушки [Ом], их две в параллель
        self.Ucc = 3.8 * 2  # напряжение питания катушки, два аккума последовательно
        self.Icc = self.Ucc / self.R  # ток катушки
        self.Initialize()

    def Initialize(self):
        self.E = 0  # энергия, затраченная на управление

    def M_B(self, B_B):
        """суммарный момент ЭМУ
        Args:
            B_B (np.array(3)): МПЗ [T]
            t (float): время
        """
        self.L_B = self.kEMU * self.U
        return np.cross(self.L_B, B_B)

    def Pwr(self):
        """энергопотребление катушек [W]"""
        return 2 * np.sum((self.Icc * self.U) ** 2 * self.R)

    def isWorks(self, t):
        """множитель момента ЭМУ, по сути ШИМ-сигнал.
        ЭМУ работает часть (время Т1) цикла СОС (Tcycle)
        Returns:
            isCoilWorks (float): 1 - до Т1, 0 после.
        """
        return (t % self.Tcycle <= self.T1) and self.On


# %% Физика
# Класс с описанием физики движения
class Physics(libKernel.TaskTemplate):
    def __init__(self, tasks, db, cycle):
        self.cycle = cycle
        super().__init__(TaskList=tasks, DB=db)

    # --- Параметры модели ---
    J = np.diag([0.0122] * 3)  # момент инерции кубсата
    # J *= 1 +  0.05 * J * np.random.standard_normal(3) # добавляем 5% неопределённости
    invJ = np.linalg.inv(J)

    def ODE_Rotational(self, x, t):
        """ДУ в форме Коши.
        Момент создают дипольные катушки, расположены пАрами, по строительным осям КА

        Args:
            x: угловая скорость (рад/с), кватернион Q_IB, затраченная катушками энергия (Дж)"""
        W, Q = x[:3], x[3:7]
        M_B = self.Coils.isWorks(t) * self.Mm_B
        dW = np.matmul(self.invJ, M_B - np.cross(W, np.matmul(self.J, W)))
        dQ0 = -0.5 * (Q[1] * W[0] + Q[2] * W[1] + Q[3] * W[2])
        dQ1 = 0.5 * (Q[0] * W[0] - Q[3] * W[1] + Q[2] * W[2])
        dQ2 = 0.5 * (Q[0] * W[1] - Q[1] * W[2] + Q[3] * W[0])
        dQ3 = 0.5 * (Q[0] * W[2] - Q[2] * W[0] + Q[1] * W[1])
        dQ = np.array([dQ0, dQ1, dQ2, dQ3])
        dE = self.Coils.Pwr()
        return np.hstack((dW, dQ, dE))

    def Astro(self):
        """Упрощённая модель астродинамики (I тождественна O)
        Returns:
            X_B, Z_B - вектора ИСК, взятые в ССК
            B_B - МПЗ в ССК"""
        X_B = self.Q_BI.rotate(X_I)
        Z_B = self.Q_BI.rotate(Z_I)
        B_B = self.Q_BI.rotate(self.B_I)
        return X_B, Z_B, B_B

    def Setup(self):
        self.Coils = EMUs(self.cycle * 0.8, self.cycle)  #
        self.ODE = lambda x, t: self.ODE_Rotational(x, t)
        self.tSol = np.linspace(0, self.dt, N_STEPS)

    def Initialize(self, Omega_I=OMEGA_INIT, Q_IB=Quaternion()):
        self.NS = NORM_STEP
        self.Omega_I = Omega_I
        self.Q_IB = Q_IB
        self.Uemu = np.zeros(3)  # управление катушками выключаем
        self.Q_BI = self.Q_IB.conjugate
        self.B_B = self.Q_BI.rotate(self.B_I)
        self.Omega_B = self.Q_BI.rotate(self.Omega_I)
        self.Coils.Initialize()

    def Run(self):
        self.Coils.U = self.Uemu  # получаем управление с предыдущего цикла
        self.Mm_B = self.Coils.M_B(self.B_B)
        self.Uemu_I = self.Q_IB.rotate(self.Uemu)

        x0 = [
            self.Omega_B[0],
            self.Omega_B[1],
            self.Omega_B[2],
            self.Q_IB[0],
            self.Q_IB[1],
            self.Q_IB[2],
            self.Q_IB[3],
            self.Coils.E,
        ]
        sol = odeint(self.ODE, x0, self.tSol)  # решаем ДУ физики
        self.Omega_B = sol[-1, :3]
        self.Q_IB[0] = sol[-1, 3]
        self.Q_IB[1] = sol[-1, 4]
        self.Q_IB[2] = sol[-1, 5]
        self.Q_IB[3] = sol[-1, 6]
        self.Coils.E = sol[-1, 7]
        self.NS -= 1  # поднормируем кватернион на нужном шаге
        if self.NS <= 0:
            self.NS = NORM_STEP
            self.Q_IB = libADCS.qNormalizeL(self.Q_IB)
        # повороты проверены - кватернионы соотв угловым скоростям
        self.Q_BI = self.Q_IB.conjugate
        self.Omega_I = self.Q_IB.rotate(self.Omega_B)
        self.X_B, self.Z_B, self.B_B = self.Astro()
        self.npQ_IB = self.Q_IB.elements


# % Главный цикл
reload(db)
model = Physics(db.Tasks, db.DataBase(), cycle=0.5)
model.Manager.Loop()
