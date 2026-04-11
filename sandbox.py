"""Разовые скрипты. Запуск из корня репозитория: python sandbox.py"""

from pathlib import Path
import os
import json
import logging
from utils.sama_project_handler import DatasetSAMAHandler
from utils.az_prj_stats import ProjectGroupsStats
from utils.az_geomatcher import GeoObjectMatcher, analyze_results, export_matching_table

logger = logging.getLogger(__name__)
SANDBOX_LOG_FILE = Path(__file__).resolve().parent / "sandbox.log"


def _configure_logging(level: int = logging.INFO) -> None:
    """Append-only file logging to sandbox.log (next to this file); no console."""
    if logger.handlers:
        return
    logger.setLevel(level)
    handler = logging.FileHandler(SANDBOX_LOG_FILE, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.propagate = False


def make_global_ids(
    json_path: Path, 
    result_json_file: Path, 
    map_files_dir: Path, 
    limit_dist: float = 10.0, 
    export_csv: bool = False):
    """Make global ids for objects in the project by matching with map files (geolocation matching)."""
    # Initialize variables
    sama_data = DatasetSAMAHandler()
    sama_data.load(str(json_path))

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matcher = GeoObjectMatcher(threshold_distance=limit_dist) 
    result_data = matcher.assign_global_object_ids(
        data, 
        map_files_directory=map_files_dir
    )
    
    # Save results
    with open(result_json_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    analyze_results(result_data)
    export_matching_table(result_data, result_json_file.with_suffix(".csv"))
    logger.info("Completed.")


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
        logger.error("Не удалось загрузить SAMA-проект: %s", json_path)
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
    logger.info(
        "Было изображений: %s, удалено: %s, осталось: %s. Сохранено: %s",
        before,
        removed,
        after,
        output_path,
    )
    return removed


if __name__ == "__main__":
    _configure_logging()
    
    input_data = [
        Path("/home/azura/data_sets/oil_refinery/data/crop_data/vika_fan_full/fans.json"),
        Path("/home/azura/data_sets/oil_refinery/data/crop_data/vika_flare_full/flares.json"), 
        Path("/home/azura/data_sets/oil_refinery/data/crop_data/vika_marinenode_full/marinenodes.json")
    ]
    # json_path = Path("/home/azura/data_sets/oil_refinery/data/labeled_data/paper_with_Vika/final_only_marinnode+global_ids.json")
    # result = json_path.with_name("final_global_only_marinnode.json")
    # make_global_ids(json_path, result, Path("/home/azura/data_sets/oil_refinery/data/init/lrm_maps"), 10.0, export_csv=False)
    
    prj_sama = ProjectGroupsStats(input_data[2], logger=logger)
    # prj_sama.check_issues()
    prj_sama.get_statistic(save=True, save_plot=True, show_plot=False)
    # kill_from_list()


