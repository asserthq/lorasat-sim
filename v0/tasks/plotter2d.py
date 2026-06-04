#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Плоттер, для разгрузки проца
"""

from importlib import reload

import db
import matplotlib.pyplot as plt
import numpy as np
from pysimscheduler import libKernel
from pysimscheduler.libGraph2D import Plot2D

RAD2DEG = 180 / np.pi
DEG2RAD = np.pi / 180


# %% Плоттер
class Plotter2D(libKernel.TaskTemplate):
    def __init__(self, tasks, db, interactive=False):
        self.interactive = interactive
        super().__init__(TaskList=tasks, DB=db)

    def Setup(self):
        if self.interactive:
            plt.ion()

        self.plot1 = Plot2D(DB=self)
        # self.plot1.Setup("t", [["B_mag"], ["Omega_B"], ["Uemu"]], name="Body")
        self.plot1.Setup(
            "t", [["B_I"], ["B_B"], ["B_mag"], ["Uemu"], ["Omega_B"]], name="Body"
        )
        # self.plot2 = Plot2D(DB=self)
        # self.plot2.Setup('t', [["B_I"], ["Uemu_I"], ['Omega_I'], ["Q_IB"]], name='Inertial')

    def Initialize(self):
        if self.interactive:
            plt.show(block=False)
        self.plot1.Initialize()
        # self.plot2.Initialize()

    def Run(self):
        self.plot1.Run()
        # self.plot2.Run()

    def Finalize(self):
        self.plot1.Finalize()
        # self.plot2.Finalize()
        if self.interactive:
            plt.ioff()
        plt.show()


# % Главный цикл
reload(db)
model = Plotter2D(db.Tasks, db.DataBase(), interactive=False)
model.Manager.Loop()
