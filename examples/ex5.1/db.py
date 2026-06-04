#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
База данных и задач диспетчера
------------------------------
"""
class DataBase():
    # --- общие переменные ---
    t = 0.   # время
    dt = 0.25 # шаг задач
    tmax = 0.25*10  # время моделирования
    cmd = 0 # команда всем задачам

    u = 1.0 # float [-1..+1] - fan control, eff. PWM
    # трехкомпонентные вектора из float
    w =  [0.]*3 # wx, wy, wz [deg/s]
    a =  [0.]*3 # ax, ay, az [g]
    m =  [0.]*3 # mx, my, mz [mT]
    m2 = [0.]*3 # m2x, m2y, m2z [mT] (QMC5883)

# Список задач
Tasks = {
    'Controller':{'Keys':'t,cmd,dt,u,w,m,m2',
                  'Addr':('127.0.0.1', 6501)},
    'RemoteSys': {'Keys':'t,cmd,dt,u,w,m2',
                  'Addr':('127.0.0.1', 2910)}, # 192.168.1.5 | 188.162.92.100

    }


# import libKernel

# class RemoteSys(libKernel.TaskTemplate):
#     pass

# #% Главный цикл
# model = RemoteSys(TaskList=Tasks, DB=DataBase())
# model.Manager.CppCode()
