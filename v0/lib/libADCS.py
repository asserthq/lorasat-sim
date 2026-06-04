#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
created on Jan 28 2025 by alex

специальные алгоритмы для СОС

Везде кватернионы ковариантные, т.е. задают поворот в том же направлении,
что и их ось/угол

Поворот связанной относительно инерциальной СК:
Q_IB = Quaternion(axis=X, degrees=30).unit
Q_BI = Q_IB.inverse

Z_IB = Q_IB.rotate(Z) # оси B в системе I
компоненты меняются «так же, как» базисные векторы новой системы.
Z = Q_BI.rotate(Z_IB) # возвращаем назад


Z_BI = Q_BI.rotate(Z_B) # оси I в системе B
компоненты меняются «противоположно» преобразованию координат

B_B = self.Q_IB.rotate(self.B_I)
# константные вектора

Соглашение о именовании кватернионов и векторов:
    Кватернионы имеют двойной верхний индекс. Имя начинается с q или Q.
    Индексы могут быть только I, B, O (или др.) - по именам СК.
    Первый символ - это базовая СК, относительно которой совершается поворот, она "неподвижна"
    Второй - поворачиваемая СК, которая подвижна

    Вектора могут иметь нуль, один или два верхних индекса.
    Без индексов они всегда взяты в инерциальной СК, или в задаче рассматривается только одна СК,
        другая не имеет смысла или не нужна. Или и так понятно где взят.
    Один индекс - когда есть один вектор, просто он может быть записан (измерен) в выбранной СК.
        Например вектор МПЗ или Солнца.
    Два индекса - смысл похож на кватернионы, когда по задаче нужны оси СК взятые в другой СК.
        например IB - ось связанной ск в инерциальной системе координат
        BI - оси ИСК, записанные в ССК

"""

import numpy as np
from pyquaternion import Quaternion

# при тестах и т.п. импортируем графику
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from pysimscheduler import libGraphQ

X = np.array([1.0, 0, 0])
Y = np.array([0, 1.0, 0])
Z = np.array([0, 0, 1.0])
O = np.zeros(3)
Q_1 = Quaternion()  # единичный кватернион


# %% Кватернионы
def qConj(q):
    """сопряженный кватернион"""
    return np.array([q[0], -q[1], -q[2], -q[3]])


def qV2Q(v):
    """кватернионое представление вектора"""
    return np.array([0, v[0], v[1], v[2]])


def qVect(q):
    """верзор кватерниона"""
    return q[1:]


def qMul(q, p):
    """кватернионное умножение"""
    return np.array(
        [
            q[0] * p[0] - q[1] * p[1] - q[2] * p[2] - q[3] * p[3],
            q[0] * p[1] + q[1] * p[0] + q[2] * p[3] - q[3] * p[2],
            q[0] * p[2] - q[1] * p[3] + q[2] * p[0] + q[3] * p[1],
            q[1] * p[3] + q[1] * p[2] - q[2] * p[1] + q[3] * p[0],
        ]
    )


def qRotateQ(m, q):
    """Поворачиваем кватернион m на кватернион q
    ! Кватернионы нормированы !"""
    return qMul(q, qMul(m, qConj(q)))


def qRotateV(v, q):
    """Поворачиваем вектор v на кватернион q"""
    if np.linalg.norm(v) > 1e-12:
        qVR = qRotateQ(qV2Q(v), q)
        return qVR[1:]  # возврат векторной части
    else:
        return v


def qSuperposeVectors(a, b):
    """кватернион поворота, совмещающий вектора a -> b
    quatP2P https://nabbla1.livejournal.com/187019.html"""
    # ax, an = rotAxisAngle(a, b)
    # return Quaternion(axis=ax, angle=an)
    q = Quaternion(scalar=1 + np.dot(a, b), vector=np.cross(a, b))
    return q.unit


def vec2quat(V):
    if np.linalg.norm(V) > 0:
        return Quaternion(axis=V, angle=np.linalg.norm(V))
    else:
        return Quaternion()


def qIntegrateW_1(q, w, dt):
    """поворачиваем кватернион, угловая скорость и шаг по времени
    интегрирование на один шаг, метод 1-го порядка
    https://nabbla1.livejournal.com/190195.html
    проверено.
    ! Сохраняем результат в q
    Args:
        q (Quaternion): кватернион, который поворачиваем
        w (numpy.array): угловая скорость
        dt (float): шаг по времени
    """
    mu = [1, w[0] * dt / 2, w[1] * dt / 2, w[2] * dt / 2]
    l0 = q[0] - q[1] * mu[1] - q[2] * mu[2] - q[3] * mu[3]
    l1 = q[1] + q[0] * mu[1] + q[2] * mu[3] - q[3] * mu[2]
    l2 = q[2] + q[0] * mu[2] + q[3] * mu[1] - q[1] * mu[3]
    l3 = q[3] + q[0] * mu[3] + q[1] * mu[2] - q[2] * mu[1]
    kn = 1.5 - 0.5 * (
        l0 * l0 + l1 * l1 + l2 * l2 + l3 * l3
    )  # нормировочный коэфф. (можно не каждый шаг)
    q[0], q[1], q[2], q[3] = (
        l0 * kn,
        l1 * kn,
        l2 * kn,
        l3 * kn,
    )  # + нормализация кватерниона, аппроксимация 1 членом ряда


def qNormalizeL(q):
    """нормализация кватерниона, аппроксимация 1 членом ряда"""
    return (1.5 - 0.5 * (q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])) * q


def qDelta(q1, q2):
    """метрика разности кватернионов"""
    # https://nabbla1.livejournal.com/196144.html?es=4
    d = q1 - q2
    return 2 * d.norm * np.sqrt(1 - d.norm**2 / 4)


def qPrint(name, q):
    """Печатает кватернион .3f.

    Args:
        name (str): имя кватерниона
        q (Quaternion, array4): кватернион"""
    print(f"{name} {q[0]:.3f}, {q[1]:.3f}, {q[2]:.3f}, {q[3]:.3f}")


def qSqrt(C):
    """корень кватерниона C"""
    C_dot = np.linalg.norm(C.vector)
    C_e = C.vector / C_dot
    C_norm = np.linalg.norm(C.elements)

    f_0 = np.sqrt((C_norm + C.scalar) / 2)
    f_dot = np.sqrt((C_norm - C.scalar) / 2) * C_e

    sqrtC_pos = Quaternion(scalar=f_0, vector=f_dot)
    # sqrtC_neg = Quaternion(scalar=f_0, vector=-f_dot)
    return sqrtC_pos


# %% Алгоритмы
def algTriangle(N, EMF):
    """алгоритм расчета поворотов методом треугольника дуг
    первый поворот xA, затем xB, т.е. N = xB*xA
    умножение кватернионов обычное, слева
    Args:
        N (Quaternion): заданный кватернион поворота
        EMF (array[3]): вектор МПЗ"""
    if np.abs(np.dot(EMF, N.axis)) > 0.9999999:
        # исключаем особую точку, когда EMF = +/- N.axis
        EMF += np.random.rand(3) * 1e-5
    # Проекция EMF на плоскость, перп
    E = crossLinePlane(EMF, N.axis, N.axis)
    # точка пересечения со сферой, ближайшая к B
    A = normalizeL2(E)
    # нормаль к плоскости NxEMF
    n = normalizeL2(np.cross(N.axis, EMF))
    # ищем точки начала и конца дуги
    Aa = Quaternion(axis=N.axis, angle=-N.angle / 4).rotate(A)

    # выбор ближайшей точки (с прошлой версии кода, см ниже)
    k = np.sign(np.dot(EMF, A))
    # k = 1 if np.dot(EMF, A)>0 else -1
    axis, angle = rotAxisAngle(Aa, k * EMF)  # к ближайшей
    xA = Quaternion(axis=axis, angle=angle * 2)
    axis = vSymmetricalOfPlane(axis, n)
    xB = Quaternion(axis=axis, angle=angle * 2)

    # axis, angle = rotAxisAngle(Aa, -k*EMF) # к противоположной
    # xC = Quaternion(axis=axis, angle=angle*2)
    # axis = vSymmetricalOfPlane(axis, n)
    # xD = Quaternion(axis=axis, angle=angle*2)

    # так поворот не задать. Всегда будет A=C, B=D, так как
    # 1. Quaternion(w=cosa2, x=a[0]*sina2, y=a[1]*sina2, z=a[2]*sina2)
    # а sin, cos - периодические, они переведут угол больший pi в 2pi-a
    # 2. Поворот на a и на 2pi-a - совпадают, тождественно равны.
    # Чтобы сделать поворот на больший чем pi угол, придется его дробить на
    # композицию меньших поворотов
    return xA, xB


#


# def quatArc(B, C, EMF):
#     """ алгоритм нахождения кватерниона кратчайшего поворота B->C
#     вокруг перпендикуляра к EMF
#     см. Дуга перевода zB-zO.ggb в GeoGebra """
#     if np.linalg.norm(C-B)<0.05:
#         return Quaternion()
#     # находим середину отрезка v-vT
#     D = (B + C)/2
#     # print('D =', D)
#     # проецируем на единичную сферу
#     E = normalizeL2(D)
#     # print('E =', E)
#     # находим линию перпендикуляра к векторам |CB| и oE
#     g = np.cross(C-B, E) # вектор линии, проходящий через точку E
#     # print('g =', g)
#     # ищем точку пересечения линии g и плоскости, перпендикулярной B
#     F = crossLinePlane(E, g, EMF)
#     # F = E - g * np.dot(EMF, E) / np.dot(EMF,g) # Воднев, стр. 58
#     # print('F =', F)
#     if any(np.isnan(F)):
#         return Quaternion()
#     # oF - ось кватерниона.  Находим угол
#     # расстояние от точки v до оси
#     d = np.linalg.norm(np.cross(C, F)) / np.linalg.norm(F)
#     # print('d =', d)
#     y = np.linalg.norm(B-C)
#     # print('y =', y)
#     y2d = y/2/d if y/2/d<1 else 1.0 # при углах, близких к 180 бывало y/2/d=1.0000000000000002
#     rho = 2*np.arcsin(y2d)
#     # print('rho =', rho)
#     return Quaternion(axis=F, angle=rho)

# def quatArc2(B, C, EMF):
#     """ алгоритм нахождения кватерниона кратчайшего поворота B->C
#     вокруг перпендикуляра к EMF
#     вариант 2 """
#     BC = np.linalg.norm(B-C)
#     if BC<0.05:
#         return Quaternion() # возможно, это стоит проверять снаружи
#     # находим середину отрезка v-vT
#     E = (B + C)/2
#     # находим линию перпендикуляра к векторам |CB| и oE
#     g = np.cross(C-B, E) # вектор линии
#     # ищем точку пересечения линии g и плоскости, перпендикулярной B
#     F = crossLinePlane(E, g, EMF)
#     # a - ось кватерниона.  Находим угол
#     d2 = BC/2
#     r  = np.linalg.norm(F - B)
#     sina2 = d2/r
#     cosa2 = np.sqrt(1 - sina2*sina2)
#     a = normalizeL2(F)
#     return Quaternion(w=cosa2, x=a[0]*sina2, y=a[1]*sina2, z=a[2]*sina2)

# def algArcB2(u, v, EMF):
#     """ Кватернион кратчайшего поворота u->v, верзор которого перпендикулярен EMF
#     Args:
#         u (np.array 3): вектор z_B
#         v (np.array 3): вектор z_O (z_I)
#         EMF (np.array 3): вектор МПЗ
#     вариант 2 """
#     uv = np.linalg.norm(u-v)
#     # if uv<0.05:
#     #     return Quaternion() # возможно, это стоит проверять снаружи
#     # находим середину отрезка v-vT
#     M = (u + v)/2
#     # находим линию перпендикуляра к векторам |CB| и oE
#     g = np.cross(v-u, M) # вектор линии

#     if np.dot(EMF,g) != 0: # ищем точку пересечения линии g и плоскости, перпендикулярной B
#         F = crossLinePlane(M, g, EMF)
#     else:
#         F = g

#     # a - ось кватерниона.  Находим угол
#     d2 = uv/2
#     r  = np.linalg.norm(F - u)
#     sina2 = d2/r
#     cosa2 = np.sqrt(1 - sina2*sina2) # здесь так можно
#     a = normalizeL2(F)
#     if np.isnan(cosa2) or any(np.isnan(a)):
#         print(f'NaN qArcB: u={u}, v={v}, EMF={EMF}')
#     return Quaternion(w=cosa2, x=a[0]*sina2, y=a[1]*sina2, z=a[2]*sina2)


def vAngle(a, b):
    """угол между векторами, в радианах"""
    return np.arccos(np.dot(a, b) / np.sqrt(np.dot(a, a) * np.dot(b, b)))


def algArcB(u, v, B, tol=0.01):
    """Кватернион кратчайшего поворота u->v, верзор которого перпендикулярен EMF
    Args:
        u (np.array 3): вектор z_B
        v (np.array 3): вектор z_O (z_I)
        EMF (np.array 3): вектор МПЗ
    """
    uv = np.linalg.norm(u - v)
    if uv < tol:
        # не поворачиваемся, слишком близко
        return Quaternion()  # возможно, это стоит проверять снаружи
    # проецируем точки u,v на плоскость, перпендикулярную EMF
    U = u - B * np.dot(B, u)
    V = v - B * np.dot(B, v)
    # Через них проходит прямая j с направл. вектором
    r0 = V
    a = U - V
    # находим середину отрезка v-vT
    M = (u + v) / 2
    # через него проводим перпендикулярно ему плоскость q
    n = u - v
    D = np.dot(n, -M)
    # Пересечение прямой j и плоскости q - центр дуги, ось кватерниона
    F = r0 - a * (np.dot(n, r0) + D) / np.dot(n, a)

    g = u - F
    h = v - F

    an = vAngle(g, h)
    # ax = normalizeL2(F)
    lenF = np.linalg.norm(F)
    ax = lenF * normalizeL2(F) + (1 - lenF) * np.cross(g, h)

    if np.dot(ax, np.cross(g, h)) < 0:
        ax = -ax
    # axis, angle = rotAxisAngle(g, h)
    return Quaternion(axis=ax, angle=an)


# % Тесты
if __name__ == "__main__":

    def plotTestCase(fig, ax, u, v, B):
        q = algArcB(u, v, B)
        # print('   целевой v:', v)
        # print('повернутый u:', q.rotate(u))
        qList = list(Quaternion.intermediates(Q_1, q, 16, include_endpoints=True))

        Fig = libGraphQ.PersistentPlot3D(fig, ax)
        ax = Fig.ax
        Sph = libGraphQ.Sphere(ax)
        Fig.equal()

        Line = libGraphQ.Line1OnSphere(ax, qList, v=u)
        uV = libGraphQ.Vector(ax, vector=u, label="u", color="C1")
        vV = libGraphQ.Vector(ax, vector=v, label="v", color="C2")
        BV = libGraphQ.Vector(ax, vector=B, label="B", color="C3")
        qV = libGraphQ.Vector(ax, vector=q.axis, label="q", color="C4")
        dv = np.linalg.norm(v - q.rotate(u))
        title = f"dv = {dv:.2g}"
        ax.set_title(title, fontsize=10)

    fig, axs = plt.subplots(
        ncols=2, nrows=2, figsize=(9.5, 9.5), subplot_kw={"projection": "3d"}
    )  # layout="constrained")
    fig.canvas.manager.set_window_title("Figure: algArcB")
    v = Z
    # рядом с большой дугой
    B = -Y
    u = Quaternion(axis=X, degrees=-40).rotate(v)
    plotTestCase(fig, axs[0][0], u, v, B)
    # по большой дуге
    u = Quaternion(axis=X, degrees=40).rotate(v)
    plotTestCase(fig, axs[0][1], u, v, B)
    # классика
    B = X
    u = Quaternion(axis=X - 0.2 * Y, degrees=40).rotate(v)
    plotTestCase(fig, axs[1][0], u, v, B)
    # классика наоборот
    B = X
    u = Quaternion(axis=X + 0.2 * Y, degrees=40).rotate(v)
    plotTestCase(fig, axs[1][1], u, v, B)


# # libGraphQ.Vector(ax, vector=g, label='g', color='C5')
# # libGraphQ.Vector(ax, vector=h, label='h', color='C6')

# %%


# z_B=B=np.array([0.741,-0.146,0.655])
# z_O=C=np.array([0,0,1])
# b=EMF=np.array([0,0.981,0.196])
# Q2 = quatArc2(z_B, z_O, b)
# Q1 = quatArc(z_B, z_O, b)

# проверка quatArc
# q = quatArc2(np.array([0,1,0]), np.array([0,0,1]), np.array([1,0,0]))
# q.axis # array([0.     , 0.70711, 0.70711])
# q.degrees # 180.0

# проверка quatArc вторая
# x_I = np.array([1,0,0])
# y_I = np.array([0,1,0])
# z_I = np.array([0,0,1])
# Q_IB = Quaternion(axis=[1,0,0], degrees=20)
# Q_None = Quaternion()
# EMF = np.array([1,0,0])
# 1.
# qLongArc(z_I, z_I, EMF) # = Quaternion(1.0, 0.0, 0.0, 0.0), OK
# 2.
# x_B, y_B, z_B = multiRotate(Q_IB, [x_I, y_I, z_I])
# q = qLongArc(z_B, z_I, EMF)
# libADCS.vAngle(q.rotate(z_B), z_I) # = 0.0, OK


def algApproxSuperpose(n, u, v):
    """Кватернион поворота по заданной оси, наиболее точно совмещающий два направления
    Args:
        n: ось поворота (единичный вектор направления на первый объект),
        u: текущее направление второго объектива,
        v: направление на второй объект

    Найти угол φ, на который надо произвести поворот вокруг оси n,
    чтобы вектор u (повёрнутый ) максимально точно совместился с v

    https://nabbla1.livejournal.com/194753.html"""

    phi = np.arctan2(
        np.dot(np.cross(n, u), v), np.dot(u, v) - np.dot(n, v) * np.dot(n, u)
    )
    return Quaternion(axis=n, angle=phi)
    # quatApproxCombine([0,0,1], [0,1,0], [1,0,0])


# def quatShortest():
#     """ Кватернион кратчайшего поворота системы координат (Мортари-Маркли)
#     Args:
#         fX, fZ: оси фактические
#         tX, tZ: оси требуемые"""

#     return Quaternion()


def algMortariMarkley(R, B, weights=None):
    """Алгоритм Мортари-Маркли: OLAE (Optimal Linear Attitude Estimator)
    находим кватернион, переводящий эталонные вектора R в измеренные B
    https://nabbla1.livejournal.com/200050.html

    Args:
        R, B: list из векторов np.array(3)
            R в EME, B в Body
    Returns:
        qIB: Кватернион кратчайшего поворота системы координат
    """
    N = len(R)
    if weights is None:
        weights = np.ones(len(R))

    # 1. Из "эталонных" и "измеренных" векторов строим суммы и разности:
    S, D = [], []
    for i in range(N):
        S.append(R[i] + B[i])
        D.append(R[i] - B[i])

    # % 2. По векторам сумм и разности вычисляем вектор v и матрицу M:
    v = np.zeros(3)
    M = np.zeros((3, 3))
    for i in range(N):
        v += weights[i] * np.cross(S[i], D[i])

        SCI = np.array(
            [[0, -S[i][2], S[i][1]], [S[i][2], 0, -S[i][0]], [-S[i][1], S[i][0], 0]]
        )
        M += weights[i] * np.matmul(SCI.T, SCI)

    # % 3. Решаем линейное матричное уравнение
    # (что то же самое - систему из 3 уравнений с 3 неизвестными):
    theta = np.linalg.solve(M, -v)

    # % 4. Из вектора Родрига получаем кватернион
    Lnu = Quaternion(scalar=1, vector=theta).normalised
    # ниже: поворот вектора на кватернион (который ищет Мортари-Маркли)
    # соответствует повороту системы координат на обратный поворот (mortari.py)
    # возвращает qIB
    return Lnu.inverse


# %% Вектора
def vAngle(a, b):
    """угол между векторами, в радианах"""
    return np.arccos(np.dot(a, b) / np.sqrt(np.dot(a, a) * np.dot(b, b)))


def vDelta(ax1, ax2):
    """метрика разности векторов"""
    return np.linalg.norm(ax1 - ax2)


def vSymmetricalOfPlane(v, n):
    """расчет вектора, симметричного относительно плоскости,
    !! проходящей через O !!

    Args:
        v (array[3]): вектор
        n (array[3]): нормальный вектор плоскости"""
    return v - 2 * np.dot(v, n) * n


def vCollinearPlusNormal(a, b):
    """разложить a вектор на сумму коллинеарного с и нормального n вектору b"""
    c = np.dot(a, b) * normalizeL2(b)  # коллинеарная B
    n = a - c  # перпендикуляр
    return c, n


def vNormalVsCollinear(v, vBase):
    """метрика - отношение нормальной и коллинеарной составл. вектора v
    относительно базового вектора vBase
    возврат числа 0..1"""
    c, n = vCollinearPlusNormal(v, vBase)  # коллинеарная и нормальная составляющие
    # соотношение этих составляющих, нормируем к 0..1
    return np.arctan2(np.linalg.norm(n), np.linalg.norm(c)) / (np.pi / 2)


def norm1(v, length=1.0):
    """нормирует вектор v к длине length
    Args:
        v: вектор (массив numpy)"""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm * length


def normalizeL0(v):
    """ничего не делает"""
    return v


def normalizeL1(v):
    """нормирует вектор v по прямоугольной норме L1
    сумма компонентов v будет равна 1
    Args:
        v: вектор (массив numpy)"""
    norm = np.sum(np.abs(v))
    if norm == 0:
        return v
    return v / norm


def normalizeL2(v):
    """нормирует вектор v по Евклидовой норме L2
    сумма квадратов компонентов v (и его длина) будет равна 1
    Args:
        v: вектор (массив numpy)"""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def rotAxisAngle(a, b):
    """возврат оси и угла поворота от вектора a к b
    угол в радианах, ось нормирована"""
    angle = vAngle(a, b)
    if abs(angle) <= 1e-3:
        axis = np.array([1, 0, 0])
    elif abs(angle) == np.pi:  # редкий случай для a = -b
        axis = np.random.rand(3)
        Warning("rotAxisAngle: abs(angle)==np.pi, возвращаю случайную ось!")
    else:
        axis = np.cross(a, b)
    return normalizeL2(axis), angle


def normalizeMax1(v):
    """максимальный компонент v будет = 1
    Args:
        v: вектор (массив numpy)"""
    m = np.max(v)
    if m == 0:
        return v
    return v / m


def vIsPerp(A, B, tolerance=1e-9):
    """перперндикулярен ли A к B"""
    return np.dot(A, B) <= tolerance


# %% Сф. геометрия
def CartesianToSpherical(v):
    """Прямоугольные координаты в сферические
    Args:
        v (float 3): вектор"""
    r = np.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    theta = np.arccos(v[2] / r)
    phi = np.arctan2(v[1], v[0])
    return r, theta, phi


def SphericalToCartesian(theta, phi, r=1):
    """сферические координаты в прямоугольные"""
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return np.stack((x, y, z))


def CartesianToAttackSideslip(v):
    """вектор в углы атаки/скольжения
    Args:
        v: вектор
    Returns:
        aoa, aos: углы атаки и скольжения, рад"""
    _, theta, aos = CartesianToSpherical(v)
    # phi — азимутальный угол (угол в плоскости XY), радианы - равен aos
    # theta — полярный угол (угол между положительной осью Z и радиусом).
    aoa = -(theta - np.pi / 2)  # в угол атаки
    return aoa, aos


def AttackSideslipToCartesian(aoa, aos):
    """углы атаки/скольжения -> вектор
    Args:
        aoa: угол атаки
        aos: угол скольжения
    Returns:
        v: вектор
    """
    theta = -aoa + np.pi / 2  # в угол атаки
    return SphericalToCartesian(theta, aos)


# np.rad2deg(cart2as(as2cart(np.deg2rad(-2), np.deg2rad(6.89))))

# def cart2AS(v):
#     """ вектор в углы атаки/скольжения """
#     r       =  np.linalg.norm(v, axis=1)
#     theta   =  np.arccos(v[:,2]/r)
#     phi     =  np.arctan2(v[:,1],v[:,0])
#     # phi — азимутальный угол (угол в плоскости XY), радианы
#     # theta — полярный угол (угол между положительной осью Z и радиусом).
#     alpha = -theta + np.pi/2 # в угол атаки
#     return alpha, phi


def SphericalUniformMesh(samples=1, randomize=True):
    """генерирует равномерно распределенные точки на сфере
    алгоритм с числами Фибоначчи
    https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere
    """
    rnd = 1.0
    if randomize:
        rnd = np.random.rand() * samples

    points = []
    offset = 2.0 / samples
    increment = np.pi * (3.0 - np.sqrt(5.0))
    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2)
        r = np.sqrt(1 - pow(y, 2))

        phi = ((i + rnd) % samples) * increment

        x = np.cos(phi) * r
        z = np.sin(phi) * r

        points.append([x, y, z])
    return points


# %% 3D геометрия
def crossLinePlane(r0, a, n, D=0):
    """точка пересечения прямой r=r0+at и плоскости с норм вектором n, членом D
    см. Воднев, стр. 58)
    """
    return r0 - a * (np.dot(n, r0) + D) / np.dot(n, a)


def sphVectorsInsideCircle(Vectors, D=30):
    """Выбирает из векторов Vectors такие, которые будут внутри круга с углом D.
    равномерная сетка на шаре, ограниченная кругом
    TODO: ввести ось axis
    Args:
        axis: ось, вокруг которой берется окружность
        Vectors: список (массив Nx3) векторов
        D: сферический угол обзора
    + возвращает углы атаки/скольжения"""
    axis = np.array([1, 0, 0])
    v = [np.cos(np.deg2rad(D)), np.sin(np.deg2rad(D)), 0]  # поворот на D вокруг oZ
    delta = np.linalg.norm(v - axis)  # считаем расстояние
    P, aoA, aoS = [], [], []
    for (
        v
    ) in Vectors:  # выбираем только точки, которые не слишком далеко от оси вращения
        if np.linalg.norm(v - axis) <= delta:
            P.append(v)
    aoA, aoS = CartesianToAttackSideslip(np.array(P))
    return P, np.rad2deg(aoA), np.rad2deg(aoS)


# def planePoint(p, A, B, C, D):
#     return A*p[0] + B*p[1] + C*p[2] + D


def planeEq(a, b, c):
    """расчет уравнения плоскости, проходящей через три точки"""
    # Найдем два вектора, лежащих в данной плоскости
    ab = b - a
    ac = c - a
    # Определим нормальный вектор плоскости
    A, B, C = np.cross(ab, ac)
    # уравнение плоскости Ax+By+Cz+D=0, где A,B,C - компоненты n
    D = -(A * a[0] + B * a[1] + C * a[2])
    return A, B, C, D


def planePartDeriv(a, b, c):
    """частные производные по плоскости, проходящей через три точки"""
    A, B, C, D = planeEq(a, b, c)
    # считаем производные z по x,y = -A/C, -B/C
    return np.array([-A / C, -B / C])


def MfromAoAS(aoa, aos, da, ds):
    """расчёт вектора момента, требуемого для поворота на da,ds
    вектор момента нормирован"""
    V1 = AttackSideslipToCartesian(aoa, aos)
    V2 = AttackSideslipToCartesian(aoa + da, aos + ds)
    M = np.cross(V1, V2)
    return M


def vPrint(name, v):
    print(f"{name} {v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f}")


# %% 2D геометрия
def rotMatrixIB(x):
    """возврат матрицы поворота 2D, Воднев с.50(26)
    при умножении на вектор дает повернутый вектор в инерциальной системе"""
    return np.array([[np.cos(x), -np.sin(x)], [np.sin(x), np.cos(x)]])


# def rotateV2(phi, v):
#     """ поворачивает вектор на phi """


# %% Модели
class PID:
    def __init__(self, p=1, i=0.0, d=0.0):
        """простейший пид регулятор"""
        self.p, self.i, self.d = p, i, d
        self.reset()

    def reset(self):
        self.I = np.zeros(3)  # интеграл
        self.Eprev = np.zeros(3)

    def out(self, PV, SetPoint, dt):
        self.E = SetPoint - PV
        self.dEdt = (self.E - self.Eprev) / dt
        self.I += self.E * dt
        self.Eprev = self.E
        return self.p * self.E + self.i * self.I + self.d * self.dEdt


# R = PID(i=0.1, d=-10)

# dt = 0.1
# for i in range(10):
#     print(R.out(np.array([0,0,0])+0.1*i, 1, dt))


class EMUs:
    def __init__(self, T1=0.2, Tcycle=0.25):
        """модель ЭМУ. Катушки расположены пАрами, по строительным осям КА
        ЭМУ работает часть (время Т1) цикла СОС (Tcycle)
        """
        self.kEMU = 0.25  # коэфф. катушек, u(-1..+1) -> L [А*м2]
        self.T1 = T1
        self.Tcycle = Tcycle
        self.On = True

    def M_B(self, U, B_B):
        """суммарный момент ЭМУ
        Args:
            U (np.array(3)) - Управление [-1..+1]
        """
        self.L_B = self.kEMU * U
        return np.cross(self.L_B, B_B)

    def isWorks(self, t):
        """множитель момента ЭМУ, по сути ШИМ-сигнал.
        ЭМУ работает часть (время Т1) цикла СОС (Tcycle)
        Returns:
            isCoilWorks (float): 1 - до Т1, 0 после.
        """
        return (t % self.Tcycle <= self.T1) and self.On


# %% Некатегоризируемое
class Container:
    pass


def readTleFile(fileTLE):
    """чтение файла с TLE. В финале будет загрузка строк по радио"""
    with open(fileTLE, "r") as file:
        lines = [line.rstrip() for line in file]
    return lines


def iko(y, dt, Td2=250**2, idxIKO=20):
    """Метрика ИКО
    Args:
        y (array): вектор переходного процесса
        dt (float): dt
        Td2 (float): желаемая постоянная времени в квадрате
        idxIKO (int): с какого индекса с начала начинаем расчет - до него отбрасываем
    """
    if len(y.shape) > 1:
        ny = np.linalg.norm(y, axis=1)
    else:
        ny = y
    dny = 1 / dt * np.diff(ny)
    return np.sum(ny[idxIKO:] ** 2) + 200 * np.sum(
        dny[idxIKO:] ** 2
    )  # вырежем первоначальный разгон
