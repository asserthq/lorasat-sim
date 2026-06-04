#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from importlib import reload
import numpy as np
import time
#%%
from pysimscheduler import libKernel
import db


class Controller(libKernel.TaskTemplate):
    """  Задача просто печатает вектор w,
    Компонента w[0] инкрементируется в с++ задаче каждую итерацию
    """

    def Initialize(self):
        self.t0 = time.time()
        self.tStart = time.time()
        self.N = 0
        self.w = np.array([1, 2, -11.458435])

    def Run(self):
        """ просто отображаем данные датчиков """
        t = time.time()
        print(f'\t t={self.t},\t w = [{self.w[0]}, {self.w[1]}, {self.w[2]}]', flush=True)
        self.t0 = t
        self.N += 1

        # self.w = np.random.randn(3)

    def Finalize(self):
        t = time.time() - self.tStart
        print('Общее время работы:', t)
        print('период средний:', t/self.N)

#% Главный цикл
reload(db)
model = Controller(TaskList=db.Tasks, DB=db.DataBase(), isSheduler=True, isRealTime=False)
model.Manager.Loop()
