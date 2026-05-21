#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Плоттер, для разгрузки проца
"""

from importlib import reload

import libKernel
import matplotlib.pyplot as plt
import numpy as np
from libGraph2D import Plot2D
from libUtils import DataBuffer

import db

RAD2DEG = 180 / np.pi
DEG2RAD = np.pi / 180


# %% Плоттер
class Plotter2D(libKernel.TaskTemplate):
    def Setup(self):
        plt.ion()
        self.wn_B = np.linalg.norm(self.Omega_B) * RAD2DEG  # норма угловой скорости
        self.dBB = 0
        self.dBI = 0
        self.i = 30

        self.plot1 = Plot2D(DB=self)
        self.plot1.Setup("t", [["Omega_B"], ["Omega_I"], ["wn_B"]], name="Omega")
        self.plot2 = Plot2D(DB=self)
        # self.plot2.Setup('t', [['B_B'], ['B_I'], ['dBB', 'dBI']], name='EMF')
        self.plot2.Setup("t", [["Q_IB"], ["sQ_IB"], ["Ma_B"]], name="Quaternions")
        # self.Buf = DataBuffer(Obj=self)
        # self.Buf.Setup('t', ['B_B', 'B_I'], N=2) # 5c

    def Initialize(self):
        plt.show(block=False)
        self.Omega_I = self.Q_IB.rotate(self.Omega_B)
        self.plot1.Initialize()
        self.plot2.Initialize()
        # self.Buf.Initialize()

    def Run(self):
        self.wn_B = np.linalg.norm(self.Omega_B) * RAD2DEG
        # для проверки идеи о измерении dB
        # self.dBB = np.linalg.norm(self.B_B - self.Buf.B_B[0])
        # self.dBI = np.linalg.norm(self.B_I - self.Buf.B_I[0])

        # self.i -= 1
        # if self.i <= 0:
        #     self.i = 30
        #     self.Buf.Run()

        self.plot1.Run()  # отправляем результаты расчёта на график
        self.plot2.Run()

    def Finalize(self):
        self.plot1.Finalize()
        self.plot2.Finalize()
        plt.ioff()
        plt.show()


# % Главный цикл
reload(db)
model = Plotter2D(TaskList=db.Tasks, DB=db.DataBase())
model.Manager.Loop()
