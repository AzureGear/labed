from unittest.mock import patch, mock_open
import pytest  # pip install pytest
from utils.az_converter import convert_labelme_to_sama
from pathlib import Path
import utils.helper as helper
import ujson
import shutil
import os

here = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def json_files(request):
    """Фикстура, возвращая файлы json из тестового каталога данных data."""
    data_dir = os.path.join(here, "data")
    project_dir = os.path.join(data_dir, request.param)
    json_files = [os.path.join(project_dir, f) for f in os.listdir(
        project_dir) if helper.check_ext(f, "json")]
    return json_files


@pytest.fixture
def temp_output_dir(request):
    """Создает временный каталог test/data/<заданное имя>. Удаляет содержимое, если оно присутствует."""
    temp_dir = Path(os.path.join(here, "data", request.param))
    os.makedirs(temp_dir, exist_ok=True)  # создаем каталог
    for item in temp_dir.iterdir():  # удаляем внутри все объекты
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    return Path(temp_dir)


@pytest.mark.parametrize("json_files, expected_count, expected_filenames",
                         [("imgs1", 5, ["001.json", "002.json", "003.json", "004.json", "005.json"]),
                          ("imgs2", 3, ["002.json", "004.json", "006.json"]),],
                         indirect=["json_files"])
def test_json_files(json_files, expected_count, expected_filenames):
    # Проверяем, что количество файлов
    assert len(
        json_files) == expected_count, f"Expected {expected_count} files, but got {len(json_files)}"

    # Проверяем имена файлов
    actual_filenames = [os.path.basename(f) for f in json_files]
    assert set(actual_filenames) == set(
        expected_filenames), f"Expected filenames {expected_filenames}, but got {actual_filenames}"


@pytest.mark.parametrize("json_files", ["imgs1"], indirect=True)
@pytest.mark.parametrize("temp_output_dir", ["test_output"], indirect=True)
def test_convert_labelme_to_sama(json_files, temp_output_dir):
    """Тестирование конвертации labelme в SAMA"""
    input_files = json_files
    output_file = os.path.join(temp_output_dir, "convert_to_sama_result.json")
    assert len(input_files) == 5
    assert temp_output_dir.exists(), "Temp dir not exists"
    assert not any(temp_output_dir.iterdir()), "Temp dir not empty"
    result = convert_labelme_to_sama(input_files, output_file)
    assert result is True, "Return result False"
    assert os.path.exists(output_file), f"File wasn't create: '{output_file}'"

    with open(output_file, 'r') as f:
        output_data = ujson.load(f)

    # Проверяем структуру выходного файла
    assert "path_to_images" in output_data, "There is no key 'path_to_images'"
    assert "images" in output_data, "There is no key 'images'"
    assert "labels" in output_data, "There is no key  'labels'"
    assert "labels_color" in output_data, "There is no key 'labels_color'"

    # Проверяем содержимое ключей
    assert output_data["path_to_images"] == os.path.dirname(
        json_files[0]), "Path key not match"
    assert len(output_data["images"]) == 5, "Number of images not match"

    # Проверяем содержимое меток и их цветов
    for label in output_data["labels"]:
        assert label in output_data["labels_color"], f"There is no color for '{label}'"

    # Проверим выборочно первое изображение с shape
    img_dict = output_data["images"]["001.png"]
    expected = {"shapes":[{"cls_num":0,"id":0,"points":[[7.907563025210084,8.257703081232497],[7.487394957983195,52.51540616246499],[74.71428571428572,52.93557422969188],[74.57422969187675,7.697478991596643]]},{"cls_num":0,"id":1,"points":[[0.9047619047619087,99.43417366946778],[74.57422969187675,99.0140056022409],[74.99439775910365,111.89915966386555],[1.1848739495798348,111.75910364145658]]},{"cls_num":1,"id":2,"points":[[92.92156862745098,42.29131652661065],[106.3669467787115,13.85994397759104],[119.81232492997198,40.75070028011205]]},{"cls_num":2,"id":3,"points":[[81.85714285714286,66.80112044817928],[88.29971988795518,72.96358543417367],[85.9187675070028,81.78711484593838],[92.0812324929972,76.88515406162465],[99.08403361344537,81.92717086834735],[96.98319327731092,72.82352941176471],[104.12605042016806,67.22128851540616],[95.86274509803921,66.10084033613445],[92.64145658263305,56.997198879551824],[89.70028011204482,65.40056022408963]]},{"cls_num":3,"id":4,"points":[[93.06162464985994,93.69187675070027],[98.52380952380952,90.19047619047619],[104.406162464986,88.92997198879551],[110.98879551820728,89.7703081232493],[115.05042016806722,93.69187675070027],[119.81232492997198,99.15406162464986],[120.93277310924368,105.03641456582633],[119.11204481792716,111.75910364145658],[113.92997198879551,116.94117647058823],[107.76750700280111,120.44257703081232],[100.48459383753502,119.32212885154061],[93.76190476190476,116.80112044817928],[90.40056022408963,110.63865546218487],[89.56022408963585,104.19607843137254],[90.5406162464986,97.4733893557423]]}],"lrm":None,"status":"empty"}
    assert img_dict == expected


def test_convert_labelme_with_dublicate_to_sama(json_files, temp_output_dir):
    """Тестирование конвертации labelme c повторными данными в SAMA"""
    input_files = json_files
    output_file = os.path.join(temp_output_dir, "convert_to_sama_result.json")
    assert len(input_files) == 5
    assert temp_output_dir.exists(), "Temp dir not exists"
    assert not any(temp_output_dir.iterdir()), "Temp dir not empty"
    result = convert_labelme_to_sama(input_files, output_file)
    assert result is True, "Return result False"
    assert os.path.exists(output_file), f"File wasn't create: '{output_file}'"

    with open(output_file, 'r') as f:
        output_data = ujson.load(f)

    # Проверяем структуру выходного файла
    assert "path_to_images" in output_data, "There is no key 'path_to_images'"
    assert "images" in output_data, "There is no key 'images'"
    assert "labels" in output_data, "There is no key  'labels'"
    assert "labels_color" in output_data, "There is no key 'labels_color'"

    # Проверяем содержимое ключей
    assert output_data["path_to_images"] == os.path.dirname(
        json_files[0]), "Path key not match"
    assert len(output_data["images"]) == 5, "Number of images not match"

    # Проверяем содержимое меток и их цветов
    for label in output_data["labels"]:
        assert label in output_data["labels_color"], f"There is no color for '{label}'"

    # Проверим выборочно первое изображение с shape
    img_dict = output_data["images"]["001.png"]
    expected = {"shapes":[{"cls_num":0,"id":0,"points":[[7.907563025210084,8.257703081232497],[7.487394957983195,52.51540616246499],[74.71428571428572,52.93557422969188],[74.57422969187675,7.697478991596643]]},{"cls_num":0,"id":1,"points":[[0.9047619047619087,99.43417366946778],[74.57422969187675,99.0140056022409],[74.99439775910365,111.89915966386555],[1.1848739495798348,111.75910364145658]]},{"cls_num":1,"id":2,"points":[[92.92156862745098,42.29131652661065],[106.3669467787115,13.85994397759104],[119.81232492997198,40.75070028011205]]},{"cls_num":2,"id":3,"points":[[81.85714285714286,66.80112044817928],[88.29971988795518,72.96358543417367],[85.9187675070028,81.78711484593838],[92.0812324929972,76.88515406162465],[99.08403361344537,81.92717086834735],[96.98319327731092,72.82352941176471],[104.12605042016806,67.22128851540616],[95.86274509803921,66.10084033613445],[92.64145658263305,56.997198879551824],[89.70028011204482,65.40056022408963]]},{"cls_num":3,"id":4,"points":[[93.06162464985994,93.69187675070027],[98.52380952380952,90.19047619047619],[104.406162464986,88.92997198879551],[110.98879551820728,89.7703081232493],[115.05042016806722,93.69187675070027],[119.81232492997198,99.15406162464986],[120.93277310924368,105.03641456582633],[119.11204481792716,111.75910364145658],[113.92997198879551,116.94117647058823],[107.76750700280111,120.44257703081232],[100.48459383753502,119.32212885154061],[93.76190476190476,116.80112044817928],[90.40056022408963,110.63865546218487],[89.56022408963585,104.19607843137254],[90.5406162464986,97.4733893557423]]}],"lrm":None,"status":"empty"}
    assert img_dict == expected




# if __name__ == "__main__":
#     here = os.path.dirname(os.path.abspath(__file__))
#     data_dir = os.path.join(here, "data")
#     prj_01 = os.path.join(data_dir, "txt_files")
#     in_files = [os.path.join(prj_01, f) for f in os.listdir(prj_01) if helper.check_ext(f, "text")]
