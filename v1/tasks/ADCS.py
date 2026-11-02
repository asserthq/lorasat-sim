#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from importlib import reload

# from time import sleep
import db
from pysimscheduler import libKernel


class ADCS(libKernel.TaskTemplate):
    def Setup(self):
        print("[ADCS Setup]")

    def Initialize(self):
        print("[ADCS Init]")
    def Run(self):
        print(f"[ADCS Run] получила: t = {self.t}, cmd = {self.cmd}")
        self.x += 1
        print(f"[ADCS Run] отправляю: t = {self.t}, cmd = {self.cmd}")
    # def Run(self):
    #     print(f"[ADCS Run] t = {self.t} x += 1")
    #     self.x += 1
        # sleep(1)

    def Finalize(self):
        print("[ADCS Fin]")


# % Главный цикл
reload(db)
model = ADCS(TaskList=db.Tasks, DB=db.DataBase())
model.Manager.Loop()
