#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from importlib import reload

# from time import sleep
import db
from pysimscheduler import libKernel


class Ex1(libKernel.TaskTemplate):
    def Setup(self):
        print("[Ex1 Setup]")

    def Initialize(self):
        print("[Ex1 Init]")

    def Run(self):
        print(f"[Ex1 Run] t = {self.t} x += 1")
        self.x += 1
        # sleep(1)

    def Finalize(self):
        print("[Ex1 Fin]")


# % Главный цикл
reload(db)
model = Ex1(TaskList=db.Tasks, DB=db.DataBase())
model.Manager.Loop()
