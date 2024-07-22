import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
"""Функции активации"""


def activ_func_linear(x):
    """Линейная функция активации"""
    return x


def activ_func_binary_step(x):
    """Пороговая функция (binary step function)"""
    return np.where(x >= 0, 1, 0)


def activ_func_sigmoid(x):
    """Сигмовидная функция активации"""
    return 1 / (1 + np.exp(-x))


def activ_func_relu(x):
    """Функция активации ReLU (Rectified Linear Unit)"""
    return np.maximum(0, x)


def activ_func_leaky_relu(x, alpha=0.01):
    """Функция активации Leaky ReLU (Leaky Rectified Linear Unit)"""
    return np.where(x > 0, x, alpha * x)


def activ_func_elu(x, alpha=1.0):
    """Функция активации ELU (Exponential Linear Unit)"""
    return np.where(x > 0, x, alpha * (np.exp(x) - 1))


def activ_func_tanh(x):
    """Гиперболический тангенс (Tanh)"""
    return np.tanh(x)

# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
