"""Разовые скрипты. Запуск из корня репозитория: python sandbox.py"""

from pathlib import Path
import os
import json
from utils.sama_project_handler import DatasetSAMAHandler
from utils.az_geomatcher import GeoObjectMatcher

def make_global_ids():
    """Make global ids for objects in the project"""
    # Initialize variables
    json_path = "/home/azura/data_sets/oil_refinery/data/labeled_data/paper_with_Vika/small_test_subset.json"
    map_files_dir = "/home/azura/data_sets/oil_refinery/data/init/lrm_maps"
    limit_dist = 5.0 # threshold distance for matching objects
    result_json_file = Path(json_path).with_name("vika_paper+global_ids.json")
    
    sama_data = DatasetSAMAHandler()
    sama_data.load(json_path)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matcher = GeoObjectMatcher(threshold_distance=limit_dist) 
    result_data = matcher.assign_global_object_ids(
        data, 
        map_files_directory=map_files_dir
    )
    
    # Сохранение результата
    with open(result_json_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print("Обработка завершена!")


def kill_from_list():
    """Удалить все изображения, кроме тех, чьё имя (ключ) содержит любую из подстрок списка.

    Использует DatasetSAMAHandler.remove_images_with_pattern(..., invert=True).
    """
    imgs_for_test = ["029n_BEL", "124_FRA", "127_FRA", "206_ITA", "388n_USA", "389_USA", "425_USA"]

    keep_substrings = list(imgs_for_test)

    if json_path is None:
        if os.name == "nt":
            base_dir = Path("D:/data_sets/oil_refinery/")
        else:
            base_dir = Path("/home/azura/data_sets/oil_refinery/")
        json_path = base_dir.joinpath("data/labeled_data/paper_with_Vika/small_test.json")
    json_path = Path(json_path)

    sama = DatasetSAMAHandler()
    sama.load(str(json_path))
    if not sama.is_correct_file:
        print(f"Не удалось загрузить SAMA-проект: {json_path}")
        return None

    before = len(sama.data["images"])
    removed = sama.remove_images_with_pattern(keep_substrings, invert=True)
    sama.update_ids()

    if output_path is None:
        output_path = json_path.with_name(f"{json_path.stem}_subset.json")
    else:
        output_path = Path(output_path)

    sama.save(str(output_path))
    after = len(sama.data["images"])
    print(
        f"Было изображений: {before}, удалено: {removed}, осталось: {after}. "
        f"Сохранено: {output_path}"
    )
    return removed


if __name__ == "__main__":
    # kill_from_list()
    make_global_ids()
