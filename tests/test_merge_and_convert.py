from unittest.mock import patch, mock_open
import pytest  # pip install pytest
from utils.az_converter import convert_labelme_to_sama, merge_sama_to_sama
from pathlib import Path
import utils.helper as helper
import ujson
import shutil
import os

here = os.path.dirname(os.path.abspath(__file__))


def get_input_files(dir_name: str, ext_template: str):
    """Возвращает файлы заданного шаблона расширений из тестового каталога данных data."""
    data_dir = os.path.join(here, "data")
    project_dir = os.path.join(data_dir, dir_name)
    files = [os.path.join(project_dir, f) for f in os.listdir(project_dir) if helper.check_ext(f, ext_template)]
    return files


@pytest.fixture(params=[("", "json")])
# Набор файлов json SAMA
def json_SAMA(request):
    dir_name, ext_template = request.param
    return get_input_files(dir_name, ext_template)


@pytest.fixture(params=[("imgs1", "json")])
# Набор файлов imgs1
def json_files(request):
    dir_name, ext_template = request.param
    return get_input_files(dir_name, ext_template)


@pytest.fixture(params=[("imgs2", "json")])
# Набор файлов imgs2
def json_files2(request):
    dir_name, ext_template = request.param
    return get_input_files(dir_name, ext_template)


@pytest.fixture
def temp_output_dir():
    """Создает временный каталог test/data/<заданное имя>. Удаляет содержимое, если оно присутствует."""
    temp_dir = Path(os.path.join(here, "data", "test_output"))
    os.makedirs(temp_dir, exist_ok=True)  # создаем каталог
    for item in temp_dir.iterdir():  # удаляем внутри все объекты
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    return Path(temp_dir)


def test_json_files(json_files):
    # Проверяем, количество файлов
    assert len(json_files) == 5, f"Expected 5 files, but got {len(json_files)}"
    # Проверяем имена файлов
    expected_filenames = ["001.json", "002.json", "003.json", "004.json", "005.json"]
    actual_filenames = [os.path.basename(f) for f in json_files]
    assert set(actual_filenames) == set(
        expected_filenames), f"Expected filenames {expected_filenames}, but got {actual_filenames}"


def test_convert_labelme_to_sama(json_files, temp_output_dir):
    """Тестирование конвертации labelme в SAMA"""
    output_file = os.path.join(temp_output_dir, "convert_to_sama_result.json")
    assert len(json_files) == 5
    assert temp_output_dir.exists(), "Temp dir not exists"
    assert not any(temp_output_dir.iterdir()), "Temp dir not empty"
    flag, info = convert_labelme_to_sama(json_files, output_file)
    assert flag is True, "Return result False"
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
    os.remove(output_file)
    assert not os.path.exists(output_file)


def test_convert_labelme_with_duplicate_to_sama(json_files, json_files2, temp_output_dir):
    """Тестирование конвертации двух проектов с присутствием дубликатов данных в SAMA"""
    assert temp_output_dir.exists(), "Temp dir not exists"
    sum_list = json_files + json_files2
    print(sum_list)
    output_file = os.path.join(temp_output_dir, "convert_to_sama_dup_result.json")
    flag, info = convert_labelme_to_sama(sum_list, output_file)
    assert flag is True, "Return result False"
    assert os.path.exists(output_file), f"File wasn't create: '{output_file}'"
    dublicated_data = info.get('dublicated_data', [])
    expected_dublicate = ['imgs2\\002.json', 'imgs2\\004.json']
    # Должно быть дублирование для файла "002.png" и "004.png".
    for expected_value in expected_dublicate:
        assert any(expected_value in item for item in dublicated_data), \
            f"Expected value '{expected_value}' not found in dublicated_data"
    with open(output_file, 'r') as f:
        output_data = ujson.load(f)
    # Проверяем, что появился "006.png"
    img_dict = output_data["images"]["006.png"]
    expected = {"shapes":[{"cls_num":2,"id":17,"points":[[39.67567567567568,32.81496881496882],[42.37837837837838,20.548856548856556],[33.64656964656965,12.02494802494803],[45.4968814968815,12.02494802494803],[49.23908523908524,0.3825363825363891],[51.52598752598753,0.17463617463618125],[54.436590436590436,11.609147609147614],[66.28690228690229,12.02494802494803],[57.97089397089397,19.92515592515593],[60.881496881496886,33.85446985446986],[50.07068607068608,25.746361746361753]]},{"cls_num":3,"id":18,"points":[[50.9022869022869,67.95010395010394],[56.723492723492726,58.38669438669439],[64.41580041580042,51.31808731808732],[76.05821205821206,47.36798336798337],[87.9085239085239,48.61538461538462],[98.0956340956341,54.852390852390855],[104.54054054054053,62.75259875259876],[108.28274428274428,73.14760914760915],[108.6985446985447,83.54261954261953],[104.54054054054053,92.89812889812889],[95.8087318087318,101.4220374220374],[87.07692307692308,105.16424116424115],[73.77130977130977,105.37214137214136],[65.87110187110187,102.46153846153845],[60.25779625779626,97.67983367983368],[57.76299376299376,94.35343035343034],[68.57380457380458,84.16632016632016],[67.11850311850311,81.04781704781703],[53.60498960498961,80.63201663201663],[51.11018711018711,78.96881496881497],[50.07068607068608,73.14760914760915]]},{"cls_num":2,"id":19,"points":[[44.24948024948025,65.45530145530145],[50.278586278586275,82.08731808731808],[65.66320166320166,83.54261954261953],[53.81288981288982,93.1060291060291],[57.97089397089397,110.36174636174636],[44.66528066528067,101.006237006237],[30.320166320166322,110.36174636174636],[34.8939708939709,94.35343035343034],[22.212058212058217,83.33471933471932],[38.220374220374225,81.67151767151766]]}],"lrm":None,"status":"empty"}
    assert img_dict == expected
    os.remove(output_file)
    assert not os.path.exists(output_file)


def test_merge_sama_to_sama_no_copy(json_SAMA, temp_output_dir):
    """Тестирование объединения двух проектов SAMA"""
    output_file = os.path.join(temp_output_dir, "merge_sama_result.json")
    assert len(json_SAMA) == 2
    assert temp_output_dir.exists(), "Temp dir not exists"
    assert not any(temp_output_dir.iterdir()), "Temp dir not empty"
    for f in json_SAMA:
        assert os.path.exists(f), f"File not exist: {f}"
    print(json_SAMA)
    info = merge_sama_to_sama(json_SAMA, output_file)
    assert os.path.exists(output_file), f"File wasn't create: '{output_file}'"
    with open(output_file, 'r') as f:
        output_data = ujson.load(f)
    img_dict = output_data["images"]["002.png"]
    expected = {"shapes":[{"cls_num":2,"id":5,"points":[[85.2855543113102,63.784994400895854],[77.97536394176932,85.2855543113102],[57.764837625979844,85.57222844344905],[73.38857782754759,99.61926091825308],[68.65845464725643,120.68980963045912],[85.71556550951848,109.0795072788354],[103.2026875699888,121.11982082866741],[97.46920492721165,99.61926091825308],[113.52295632698768,86.86226203807391],[93.3124300111982,86.43225083986562]]},{"cls_num":0,"id":6,"points":[[107.93281075027996,25.370660694288915],[96.60918253079507,49.5946248600224],[121.5498320268757,49.5946248600224]]},{"cls_num":1,"id":7,"points":[[4.443449048152296,0.0],[2.1500559910414334,1.0033594624860023],[0.8600223964165734,1.5767077267637177],[0.0,2.5930978316196684],[0.0,33.125690234390085],[3.1534154535274355,34.97424412094065],[7.453527435610303,37.12430011198208],[11.896976483762598,37.267637178051515],[15.050391937290033,37.6976483762598],[20.64053751399776,36.837625979843224],[24.51063829787234,34.25755879059351],[29.097424412094064,31.10414333706607],[31.820828667413213,27.950727883538633],[33.827547592385216,23.507278835386337],[33.97088465845465,18.633818589025758],[33.97088465845465,15.050391937290033],[32.96752519596865,11.753639417693169],[31.534154535274357,7.883538633818589],[29.67077267637178,4.5867861142217246],[26.660694288913774,2.1500559910414334],[23.937290033594625,0.5733482642777156],[23.220604703247478,0.0],[4.443449048152296,0.0]]},{"cls_num":4,"id":15,"points":[[10.033594624860022,70.9518477043673],[9.603583426651737,90.87569988801792],[28.237402015677493,100.62262038073908],[48.161254199328106,90.73236282194848],[48.5912653975364,71.38185890257559],[28.954087346024636,61.778275475923856]]}],"lrm":None,"status":"empty","last_user":None}
    assert len(info["success"]) == 7
    assert img_dict == expected
    os.remove(output_file)
    assert not os.path.exists(output_file)


def test_merge_sama_to_sama_with_copy(json_SAMA, temp_output_dir):
    """Тестирование объединения двух проектов SAMA"""
    output_file = os.path.join(temp_output_dir, "merge_sama_result.json")
    assert len(json_SAMA) == 2
    assert temp_output_dir.exists(), "Temp dir not exists"
    assert not any(temp_output_dir.iterdir()), "Temp dir not empty"
    flag, info = merge_sama_to_sama(json_files, output_file)
    assert flag is True, "Return result False"
    assert os.path.exists(output_file), f"File wasn't create: '{output_file}'"
