#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Задача для отрисовки графиков и рисунков
"""

import db
import matplotlib.pyplot as plt
from pysimscheduler import libKernel
from pysimscheduler.libGraph3D import Figure3D, PlotterCS, PlotterSat, PlotterVector

# %%


class Plotter3D(libKernel.TaskTemplate):
    """Рисует КА в инерциальной системе координат I (EME)
    c векторами
    """

    def Setup(self):
        plt.ion()
        self.fig = Figure3D(name="КА (EME)", dt=0.15)

    def Initialize(self):
        plt.show(block=False)
        self.fig.Initialize()
        ax = self.fig.ax

        # добавляем на оси объекты
        self.Sat = PlotterSat(ax)
        self.Body = PlotterCS(ax, length=1.4, suffix="B")

        self.EME = PlotterCS(ax, length=2, suffix="I")
        self.Emf = PlotterVector(ax, length=2, label="B", vector=[1, 0, 0])
        self.Umf = PlotterVector(ax, length=2, label="U", vector=[1, 0, 0])

        self.Text = ax.text2D(0.05, 0.95, self.getStatusStr(), transform=ax.transAxes)
        self.fig.Update()

    def Run(self):
        self.Sat.rotate(self.Q_IB)
        self.Body.rotate(self.Q_IB)
        self.Emf.replace(self.B_I)
        self.Umf.replace(self.Uemu_I)

        self.Text.set_text(self.getStatusStr())
        self.fig.Update()

    def Finalize(self):
        plt.ioff()
        plt.show()

    def getStatusStr(self):
        ax = self.Q_IB.axis
        an = self.Q_IB.degrees
        s = "t: %.2f s\nqIB: ax %+.2f %+.2f %+.2f | deg %+.2f" % (
            self.t,
            ax[0],
            ax[1],
            ax[2],
            an,
        )
        return s


model = Plotter3D(TaskList=db.Tasks, DB=db.DataBase())
model.Manager.Loop()
