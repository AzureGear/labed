"""Разовые скрипты. Запуск из корня репозитория: python sandbox.py"""

from pathlib import Path
import os
import re
import json
import logging
from utils import helper
from collections import defaultdict
from utils.sama_project_handler import DatasetSAMAHandler
from utils.az_geomatcher import GeoObjectMatcher, analyze_results, export_matching_table
from ui.az_proc_sorting import get_group_objects

logger = logging.getLogger(__name__)

SANDBOX_LOG_FILE = Path(__file__).resolve().parent / "sandbox.log"

PREFIX_RE = re.compile(r"^([^_]+)_([^_]+)_")


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


def get_images_info():
    """Get images info from the project"""
    json_path = Path("/home/azura/data_sets/oil_refinery/data/labeled_data/paper_with_Vika/final.json")
    sama_data = DatasetSAMAHandler()
    sama_data.load(json_path)
    group_and_validate(sama_data.data["images"].keys())
    

def check_issues(filename: str) -> list[str]:
    issues = []
    if " " in filename:
        issues.append("пробел в имени")
    # убираем расширение и берём часть после префикса
    stem = Path(filename).stem
    parts = stem.split("_")
    after_prefix = "_".join(parts[2:])
    if not re.match(r"\s*\d{4}", after_prefix):
        issues.append("после префикса не год")
    return issues


def group_and_validate(image_names: list[str]):
    groups: dict[str, list[str]] = defaultdict(list)
    ungrouped: list[str] = []

    for name in sorted(image_names):
        m = PREFIX_RE.match(name)
        if m:
            key = f"{m.group(1)}_{m.group(2)}"
            groups[key].append(name)
        else:
            ungrouped.append(name)

    for group_key in sorted(groups):
        imgs = groups[group_key]
        issues_found = [(n, check_issues(n)) for n in imgs if check_issues(n)]
        marker = f"  [{len(issues_found)} с ошибкой]" if issues_found else ""
        logger.info(f"\n=== {group_key}{marker} ===")
        for name in imgs:
            issues = check_issues(name)
            flag = f"  ← {', '.join(issues)}" if issues else ""
            logger.info(f"  {'⚠' if issues else ' '} {name}{flag}")

    if ungrouped:
        logger.info("\n=== не распознан префикс ===")
        for name in ungrouped:
            logger.info(f"  ✗ {name}")


def make_global_ids():
    """Make global ids for objects in the project"""
    # Initialize variables
    json_path = Path("/home/azura/data_sets/oil_refinery/data/labeled_data/paper_with_Vika/final.json")
    map_files_dir = Path("/home/azura/data_sets/oil_refinery/data/init/lrm_maps")
    limit_dist = 10.0 # threshold distance for matching objects
    result_json_file = json_path.with_name("final+global_ids.json")
    
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
    # kill_from_list()
    # make_global_ids()
    # get_images_info()

