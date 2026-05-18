#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from importlib import reload

import libKernel
import numpy as np
from libGraph2D import Plot2D, Storager

import db
from backend import GraphicsBackend


# %%
class ADCS(libKernel.TaskTemplate):
    """система ориентации"""

    # ********************* Алгоритмы *********************
    def Idle(self):
        self.U = 0.0

    # ********************* Методы модели *********************
    def Setup(self):
        # подготовка графиков, логов, буфера
        self.plot1 = Plot2D(DB=self)
        self.storager = Storager(DB=self)
        self.graphics = GraphicsBackend()

        self.plot1.Setup("t", [["B_QMC", "B_MPU"], ["W_MPU"], ["U"]], name="EMF + w")
        self.storager.Setup("t", ["B_QMC", "B_MPU", "W_MPU", "A_MPU"])
        self.graphics.Setup()

    def Initialize(self):
        self.storager.Initialize()
        self.plot1.Initialize()
        self.graphics.Initialize()

        # Обновляем график с той же частотой, что и шаг симуляции (dt).
        self.plot1.dtPlot = self.dt

        self.Uemf = np.zeros(3)  # задаём начальное состояние (нулевые НУ)

    def Run(self):
        self.storager.Run()
        # сохраняем графики, буфер, логи
        self.plot1.Run()
        self.graphics.Run()

        # проверка
        if self.t < 5.0:
            self.U = -1.0
        else:
            self.U = 0.0

    def Finalize(self):
        path = "C:/Users/sanya/dev/lesson1/data/"
        now = datetime.now()
        name = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_ADCS_{self.tmax:.0f}.csv"
        self.storager.Finalize(path + name)
        self.plot1.Finalize()
        self.graphics.Finalize()


# % Главный цикл
reload(db)
model = ADCS(TaskList=db.Tasks, DB=db.DataBase(), isSheduler=True, isRealTime=True)
model.Manager.Loop()
