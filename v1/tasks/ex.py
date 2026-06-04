#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from importlib import reload

# from time import sleep
import db
from pysimscheduler import libKernel


class Ex(libKernel.TaskTemplate):
    def Setup(self):
        print("[Ex Setup]")

    def Initialize(self):
        print("[Ex Init]")
        self.x = 67

    def Run(self):
        print(f"[Ex Run] t = {self.t} x = {self.x}")
        # sleep(1)

    def Finalize(self):
        print("[Ex Fin]")


# % Главный цикл
reload(db)
model = Ex(TaskList=db.Tasks, DB=db.DataBase(), isSheduler=True, isRealTime=True)
model.Manager.Loop()
