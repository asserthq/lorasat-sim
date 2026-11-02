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
        print(f"[Ex1 Run] получила: t = {self.t}, cmd = {self.cmd}, x = {self.x}")
        self.x += 1
        print(f"[Ex1 Run] отправляю: t = {self.t}, cmd = {self.cmd}, x = {self.x}")

    def Finalize(self):
        print("[Ex1 Fin]")


# % Главный цикл
reload(db)
model = Ex1(TaskList=db.Tasks, DB=db.DataBase())
model.Manager.Loop()
