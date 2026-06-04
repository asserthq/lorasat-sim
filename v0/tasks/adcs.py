#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from importlib import reload

import db
import numpy as np
from lib import libADCS
from pysimscheduler import libKernel

X_I, Y_I, Z_I = libADCS.X, libADCS.Y, libADCS.Z


class ADCS(libKernel.TaskTemplate):
    """система ориентации"""

    kBDot = 25.0
    kBCross = -250.0

    def Idle(self):
        self.U = np.zeros(3)

    def BDot(self):
        """алгоритм B-Dot (всё в ССК), классика"""
        # отнормируем вектор МПЗ (коэфф в контуре не будет зависеть от вариаций поля)
        Bn = libADCS.normalizeL2(self.B_mag)
        # считаем приращения dB, dt
        self.dt = self.t - self.tp
        self.dB = Bn - self.Bp

        u = -self.kBDot * self.dB / self.dt  # B-dot
        self.Uemu = np.clip(
            u, -1.0, 1.0
        )  # напряжение на катушках, ШИМ линеен, предел \pm 1
        self.tp, self.Bp = self.t, Bn  # сохранение переменных на след итерацию

    def BCross(self):
        """алгоритм B-Cross (всё в ССК), классика"""
        Bn = libADCS.normalizeL2(self.B_mag)
        T = self.kBCross * np.cross(Bn, self.Bp)  # вектора уже нормированы
        u = np.cross(Bn, T)  # B-Cross
        self.Uemu = np.clip(u, -1.0, 1.0)
        self.tp, self.Bp = self.t, Bn  # сохранение переменных на след итерацию

    def Setup(self):
        return

    def Initialize(self):
        self.Uemu = np.zeros(3)  # задаём начальное состояние (нулевые НУ)
        self.tp, self.Bp = 0.0, np.zeros(3)

    def Run(self):
        if self.t == 0:
            return

        self.Uemu = np.array([0, 0, -1])
        # self.BDot()

    def Finalize(self):
        return


# % Главный цикл
reload(db)
model = ADCS(TaskList=db.Tasks, DB=db.DataBase(), isSheduler=True, isRealTime=False)
model.Manager.Loop()
