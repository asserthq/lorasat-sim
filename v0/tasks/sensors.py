from importlib import reload

import db
import numpy as np
from pysimscheduler import libKernel

NOISE_STD = 4e-6


class Sensors(libKernel.TaskTemplate):
    """Модель датчиков КА."""

    def Setup(self):
        self.rng = np.random.default_rng(seed=67)

    def Initialize(self):
        self.B_mag = self.B_B

    def Run(self):
        self.B_mag = self.B_B + self.rng.normal(0, NOISE_STD, 3)
        # self.B_mag = self.B_B


# % Главный цикл
reload(db)
model = Sensors(TaskList=db.Tasks, DB=db.DataBase())
model.Manager.Loop()
