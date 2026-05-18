#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Это симулятор учебного стенда из статьи.
Он симулирует датчики (классы с именами датчиков) и динамику стенда

UDP server for returning measured data from the spacecraft simulator testbed

accepts double [-1..+1] - fan control, eff. PWM

returns:
1. current control u
2. vector of 9 double elements (MPU9250)
wx, wy, wz [deg/s]
ax, ay, az [g]
mx, my, mz [mT]
3. vector of 3 double elements (QMC5883)
m2x, m2y, m2z [mT]

All vectors in instrumental coordinate system, unfiltered, unbiased
"""

import time

import libKernel
import numpy as np
from scipy.integrate import odeint


class Sensor:
    """моделируем датчик с _векторным_ выходом (3)"""

    def __init__(self, mu, sigma, isEME=False):
        """isEME если измеряемый вектор в инерциальной СК (датчик освещённости)
        исключение - угловая скорость, она всегда в EME

        Накладываем Гауссов шум

        Args:
            mu (array 3): смещения
            sigma (array 3): стандартные отклонения"""
        self.mu, self.sigma = mu, sigma
        self.isEME = isEME
        self.out = np.zeros(3)

    def tick(self, v, theta=0.0):
        """генерация выходной измеренной величины (+шум)

        Args:
            v - расчётное значение, np.array(3)
            theta - угол поворота I относительно B, для паресчёта вектора в ССК [рад]
        """
        if self.isEME:
            c, s = np.cos(-theta), np.sin(-theta)
            R = np.array(((c, -s, 0), (s, c, 0), (0, 0, 1)))
            self.out = np.matmul(R, v) + np.random.normal(self.mu, self.sigma, 3)
        else:
            self.out = v + np.random.normal(self.mu, self.sigma, 3)


class MPU9250:
    def __init__(self):
        """модель датчика MPU92/50
        wx, wy, wz [deg/s]
        ax, ay, az [g]
        mx, my, mz [mT]
        """
        self.r2d = 180 / np.pi
        self.Magnetometer = Sensor(
            mu=np.array([2.8, -3.1, 2.0]) * 1e-6, sigma=3.0e-6, isEME=True
        )
        self.Accelerometer = Sensor(
            mu=np.random.normal(0, 0.05, 3), sigma=0.01, isEME=True
        )
        self.Gyroscope = Sensor(
            mu=np.random.normal(0, 2, 3) / self.r2d, sigma=1.1 / self.r2d
        )
        # вектора (физика)
        self.B = np.array([0.0, 40e-6, 0.0])  # магнитное поле (I), [T]
        self.G = np.array([0, 0, -1])
        # выход датчиков
        self.gyro = np.zeros(3)
        self.accel = np.zeros(3)
        self.mag = np.zeros(3)

    def tick(self, theta, omega):
        self.Magnetometer.tick(self.B, theta)
        self.Accelerometer.tick(self.G, theta)
        self.Gyroscope.tick(omega)
        self.mag = self.Magnetometer.out * 1e3  # [mT]
        self.accel = self.Accelerometer.out  # [g]
        self.gyro = self.Gyroscope.out * self.r2d  # [deg/s]


class QMC5883:
    def __init__(self):
        """модель датчика QMC5883
        m2x, m2y, m2z [mT]"""
        self.Magnetometer = Sensor(
            mu=np.array([2.8, -1.1, 1.0]) * 1e-6, sigma=2.0e-6, isEME=True
        )
        self.B = np.array([0.0, 40e-6, 0.0])  # магнитное поле (I), [T]

    def tick(self, theta):
        self.Magnetometer.tick(self.B, theta)

    def measure(self):
        """чтение выхода датчика"""
        return self.Magnetometer.out * 1e3  # [mT]


# %%
class Simulator(libKernel.TaskTemplate):
    """Интерфейс к датчикам и вентиляторам стенда"""

    def Setup(self):
        # ka, ku, J - идентифицированы! dt=140мс
        ka = 3.32914427e-05
        ku = 6.36414245e-02
        Jres = 1 / 6.24375258e-02

        # array([1.43155798e-07, 5.88172838e-01, 4.74464837e-02])
        def myode(y, t, u):
            """система ДУ, описывающая вертушку"""
            theta, omega = y
            Mu = ku * u
            dydt = [omega, (Mu - ka * omega**2 * np.sign(omega)) * Jres]
            return dydt

        self.ODE = myode

        self.imu = MPU9250()
        self.compass = QMC5883()

    def Initialize(self):
        self.State = [0.0, 0.0]  # theta, omega in rad
        self.tPrev = time.time()

    def Run(self):
        """вычисление состояния системы"""
        fan = np.clip(self.U, -1.0, 1.0)
        tNow = time.time()
        sol = odeint(
            self.ODE, self.State, [0, tNow - self.tPrev], args=(fan,), hmax=0.01
        )  # , hmax=0.01

        self.State = sol[-1, :]
        self.tPrev = tNow

        self.imu.tick(self.State[0], self.State[1])
        self.compass.tick(self.State[0])

        self.W_MPU = list(self.imu.gyro)
        self.A_MPU = list(self.imu.accel)
        self.B_MPU = list(self.imu.mag)
        self.B_QMC = list(self.compass.measure())  # m2x, m2y, m2z [mT] (QMC5883)


import db

# % Главный цикл
model = Simulator(TaskList=db.Tasks, DB=db.DataBase())
model.Manager.Loop()
