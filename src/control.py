#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from importlib import reload

import libKernel
import matplotlib.pyplot as plt
import numpy as np
from libGraph2D import Storager

import db
import libADCS

X_I, Y_I, Z_I = libADCS.X, libADCS.Y, libADCS.Z


# %%
class ADCS(libKernel.TaskTemplate):
    """система ориентации"""

    # ********************* Алгоритмы *********************
    def Idle(self):
        self.U = np.zeros(3)

    kBDot = 25.0

    def BDot(self):
        """алгоритм B-Dot (всё в ССК), классика"""
        # отнормируем вектор МПЗ (коэфф в контуре не будет зависеть от вариаций поля)
        Bn = libADCS.normalizeL2(self.sensMag.out)
        # считаем приращения dB, dt
        self.dt = self.t - self.tp
        self.dB = Bn - self.Bp

        u = -self.kBDot * self.dB / self.dt  # B-dot
        self.Uemu = np.clip(
            u, -1.0, 1.0
        )  # напряжение на катушках, ШИМ линеен, предел \pm 1
        self.tp, self.Bp = self.t, Bn  # сохранение переменных на след итерацию

    kBCross = -250.0

    def BCross(self):
        """алгоритм B-Cross (всё в ССК), классика"""
        Bn = libADCS.normalizeL2(self.sensMag.out)
        T = self.kBCross * np.cross(Bn, self.Bp)  # вектора уже нормированы
        u = np.cross(Bn, T)  # B-Cross
        self.Uemu = np.clip(u, -1.0, 1.0)
        self.tp, self.Bp = self.t, Bn  # сохранение переменных на след итерацию

    # ********************* Методы модели *********************
    def Setup(self):
        # plt.ion()
        # подготовка графиков, логов, буфера
        # self.plot1 = Plot2D(DB=self)
        self.storager = Storager(DB=self)

        # self.plot1.Setup("t", [["Omega_I"], ["Uemu"]], name="EMF + w")
        self.storager.Setup("t", ["B_B", "Omega_I"])

    def Initialize(self):
        # plt.show(block=False)
        self.storager.Initialize()
        # self.plot1.Initialize()

        # Обновляем график с той же частотой, что и шаг симуляции (dt).
        # self.plot1.dtPlot = self.dt
        self.Uemu = np.zeros(3)  # задаём начальное состояние (нулевые НУ)

        self.tp, self.Bp = 0.0, np.zeros(3)

    def Run(self):
        self.storager.Run()
        # сохраняем графики, буфер, логи
        # self.plot1.Run()

        # проверка
        if self.t < 105.0:
            self.Uemu = libADCS.normalizeL2(np.array([1, 1, 1]))
        else:
            self.Uemu = np.zeros(3)

    def Finalize(self):
        path = "/home/lynx/dev/1440/adcs-sim/data/"
        now = datetime.now()
        name = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_ADCS_{self.tmax:.0f}.csv"
        self.storager.Finalize(path + name)
        # self.plot1.Finalize()


# % Главный цикл
reload(db)
model = ADCS(TaskList=db.Tasks, DB=db.DataBase(), isSheduler=True, isRealTime=False)
model.Manager.Loop()
