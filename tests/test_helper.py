import pytest
import random
import ujson
from unittest.mock import mock_open, patch
from utils import helper


def test_random_color_with_seed():
    # Одинаковый seed формирует одинаковые цвета
    seed = 42
    color1 = helper.random_color(seed)
    color2 = helper.random_color(seed)
    assert color1 == color2

def test_random_color_without_seed():
    # Осутствие seed возвращает разные цвета
    color1 = helper.random_color()
    color2 = helper.random_color()
    assert color1 != color2

def test_color_format():
    # Цвет соответствует формату [R, G, B, A], а A по умолчанию == 120
    color = helper.random_color()
    assert len(color) == 4
    for i in range (len(color)):
        assert 0 <= color[i] <= 255
    assert color[3] == 120

def test_save_json():
    # Сохранение json
    json_path = 'test_save.json'
    data = {'key': 'value'}

    # Заменяем реальную функцию open на мок-объект, который можно проверять и контролировать
    with patch('builtins.open', mock_open()) as mocked_open: 
        helper.save_json(json_path, data)

        # Проверка, что функция open была вызвана ровно один раз с аргументами json_path и 'w'.
        mocked_open.assert_called_once_with(json_path, 'w')
        mocked_file = mocked_open() # Получаем мок объекта файла

        # Проверяем, что ujson.dump был вызван с правильными аргументами
        mocked_file.write.assert_called_once_with(ujson.dumps(data))


def test_load_json():
    # Загрузка json
    file_path = 'test_load.json'
    data = {'key': 'value'}

    # Мокируем и указываем данные для чтения
    with patch('builtins.open', mock_open(read_data=ujson.dumps(data))) as mocked_open:
        result = helper.load_json(file_path)

        # Проверяем, что open был вызван с правильными аргументами
        mocked_open.assert_called_once_with(file_path, 'r')

        # Проверяем, что результат совпадает с ожидаемыми данными
        assert result == data


def test_load_invalid_json():
    # Загрузка json с некорректными данными
    file_path = 'test.json'
    invalid_data = 'invalid json data'

    with patch('builtins.open', mock_open(read_data=invalid_data)) as mocked_open:
        result = helper.load_json(file_path)
        mocked_open.assert_called_once_with(file_path, 'r')
        assert result is None


def test_load_empty_file():
    # Загрузка пустого json
    file_path = 'test.json'
    empty_data = ''

    with patch('builtins.open', mock_open(read_data=empty_data)) as mocked_open:
        result = helper.load_json(file_path)
        mocked_open.assert_called_once_with(file_path, 'r')
        assert result is None