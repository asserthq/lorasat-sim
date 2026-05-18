import matplotlib.pyplot as plt


class GraphicsBackend:
    def __init__(self, DB=None):
        self.DB = DB

    def Setup(self):
        # Включаем интерактивный режим Matplotlib, чтобы окна рисовались
        # и обновлялись во время работы симуляции (draw_idle/flush_events внутри pysimsheduler).
        plt.ion()

    def Initialize(self):
        # даём GUI-циклу стартовать
        plt.show(block=False)

    def Run(self):
        return
        # Минимально обслуживаем GUI event-loop.
        # Основной вывод делает Plot2D (draw_idle/flush_events), но пауза помогает не "подвисать" окнам.
        # plt.pause(1.0 / 120)

    def Finalize(self):
        # После завершения/interrupt держим окна открытыми.
        plt.ioff()
        plt.show()
