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


activation_functions = {
    "sigmoid": activ_func_sigmoid,
    "relu": activ_func_relu,
    "linear": activ_func_linear,
    "binary step": activ_func_binary_step,
    "leaky relu": activ_func_leaky_relu,
    "exponential linear unit": activ_func_elu,
    "tanh": activ_func_tanh}


def get_activ_func(name, x):
    """Автоматизированное использование функции активации через словарь. Доступно 7 функций. Может быть расширен."""
    return activation_functions[name](x)


# ----------------------------------------------------------------------------------------------------------------------
"""Функции интерполяции"""


def interpolation_line(min_val, max_val, n):
    """Линейная функция. Возвращает перечень значений включая исходные."""
    return [min_val + (max_val - min_val) * (x / n) for x in range(n + 1)]


def interpolation_quadr(min_val, max_val, n):
    """Квадратичная функция. Возвращает перечень значений включая исходные."""
    return [min_val + (max_val - min_val) * (x / n) ** 2 for x in range(n + 1)]


def interpolation_exp(min_val, max_val, n):
    """Экспоненциальная функция. Возвращает перечень значений включая исходные."""
    return [min_val + (max_val - min_val) * (np.exp(x / n) - 1) for x in range(n + 1)]


def interpolation_log(min_val, max_val, n):
    """Логарифмическая функция. Возвращает перечень значений включая исходные."""
    return [min_val + (max_val - min_val) * np.log10(1 + x / n) for x in range(n + 1)]


def interpolation_hyper(min_val, max_val, n):
    """Гиперболическая функция. Возвращает перечень значений включая исходные."""
    return [min_val + (max_val - min_val) * np.tanh(x / n) for x in range(n + 1)]


interpolation_functions = {
    "linear": interpolation_line,
    "quadratic": interpolation_quadr,
    "exponential": interpolation_exp,
    "logarithmic": interpolation_log,
    "hyperbolic": interpolation_hyper
}


def use_interpolation_func(name, min_val, max_val, n):
    """Автоматизированное использование функции интерполяции через словарь. Доступно 5 функций. Может быть расширен."""
    return interpolation_functions[name](min_val, max_val, n)

# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
