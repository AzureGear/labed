import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
"""Функции активации"""


def get_activ_func(name, x):
    """Автоматизированное использование функции активации через словарь. Доступно 7 функций. Может быть расширен."""
    activation_functions = {
        "sigmoid": activ_func_sigmoid,
        "ReLU": activ_func_relu,
        "linear": activ_func_linear,
        "binary step": activ_func_binary_step,
        "leaky ReLU": activ_func_leaky_relu,
        "exponential linear unit": activ_func_elu,
        "Tanh": activ_func_tanh}
    return activation_functions[name](x)


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
