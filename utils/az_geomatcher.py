from collections import defaultdict
from pathlib import Path

from utils.sama_project_handler import DatasetSAMAHandler
import numpy as np
import json
import math
import re
import os

class GeoObjectMatcher:
    def __init__(self, threshold_distance=10.0):
        """
        threshold_distance: максимальное расстояние в метрах для считать объекты одинаковыми
        """
        self.geodata_files_dir = None
        self.threshold_distance = threshold_distance
        
    def parse_map_file(self, map_file_path):
        """Парсинг .map файла и создание преобразователя координат"""
        try:
            with open(map_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            return None
            
        points = []
        for line in lines:
            if line.startswith('Point') and 'xy' in line:
                parts = line.split(',')
                if len(parts) >= 12:
                    try:
                        # Извлекаем пиксельные координаты
                        x_pixel = int(parts[2].strip())
                        y_pixel = int(parts[3].strip())
                        
                        # Извлекаем географические координаты
                        lat_deg = float(parts[6].strip())
                        lat_min = float(parts[7].strip())
                        lat_dir = parts[8].strip()
                        
                        lon_deg = float(parts[9].strip())
                        lon_min = float(parts[10].strip())
                        lon_dir = parts[11].strip()
                        
                        # Конвертируем в десятичные градусы
                        lat = lat_deg + lat_min / 60.0
                        if lat_dir == 'S':
                            lat = -lat
                            
                        lon = lon_deg + lon_min / 60.0
                        if lon_dir == 'W':
                            lon = -lon
                            
                        points.append((x_pixel, y_pixel, lon, lat))
                    except ValueError:
                        continue
        
        if len(points) < 3:
            return None
            
        return self._create_coordinate_transformer(points)
    
    def _create_coordinate_transformer(self, points):
        """Создает функцию для преобразования пикселей в географические координаты"""
        # Используем билинейную интерполяцию
        points = np.array(points)
        
        def pixel_to_geo(x, y):
            # Находим ближайшие точки для интерполяции
            distances = np.sqrt((points[:, 0] - x)**2 + (points[:, 1] - y)**2)
            nearest_idx = np.argsort(distances)[:4]  # 4 ближайшие точки
            
            if len(nearest_idx) < 3:
                return None
                
            nearest_points = points[nearest_idx]
            
            # Взвешенная интерполяция по расстоянию
            weights = 1.0 / (distances[nearest_idx] + 1e-9)
            weights /= np.sum(weights)
            
            lon = np.sum(nearest_points[:, 2] * weights)
            lat = np.sum(nearest_points[:, 3] * weights)
            
            return (lon, lat)
        
        return pixel_to_geo
    
    def haversine_distance(self, coord1, coord2):
        """Вычисляет расстояние в метрах между двумя точками на Земле"""
        lon1, lat1 = coord1
        lon2, lat2 = coord2
        
        R = 6371000  # Радиус Земли в метрах
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2)**2 + 
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def compute_polygon_centroid(self, points):
        """Вычисляет центроид многоугольника"""
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        centroid_x = sum(x) / len(x)
        centroid_y = sum(y) / len(y)
        return centroid_x, centroid_y
    
    def group_images(self, image_names, pattern = r"^([^_]+)_([^_]+)"):
        """Группирует изображения по паттерну"""
        groups = defaultdict(list)
        
        for img_name in image_names:
            match = re.match(pattern, img_name)
            if match:
                group_key = f"{match.group(1)}_{match.group(2)}"
                groups[group_key].append(img_name)
        
        return groups
    
    def assign_global_object_ids(self, json_data, map_files_directory):
        """Основная функция для присвоения глобальных ID объектам"""
        images = json_data["images"]
        image_names = list(images.keys())
        
        # Группируем изображения
        groups = self.group_images(image_names)
        
        # Счётчики уникальных объектов по классу: global_id = "{cls_num}_{n}"
        global_objects_map = {}  # (group_name, geo_hash) -> global_id str
        next_id_by_class = defaultdict(int)
        
        for group_name, group_images in groups.items():
            print(f"Обрабатываю группу: {group_name}")
            
            # Собираем все объекты в группе с их геокоординатами
            group_objects = []
            
            for img_name in group_images:
                map_file_path = os.path.join(
                    map_files_directory, 
                    os.path.splitext(img_name)[0] + ".map"
                )
                
                transformer = self.parse_map_file(map_file_path)
                if not transformer:
                    print(f"Не удалось загрузить .map файл для {img_name}")
                    continue
                
                shapes = images[img_name]["shapes"]
                for shape in shapes:
                    centroid = self.compute_polygon_centroid(shape["points"])
                    geo_coord = transformer(centroid[0], centroid[1])
                    
                    if geo_coord:
                        group_objects.append({
                            'image': img_name,
                            'shape': shape,
                            'geo_coord': geo_coord,
                            'class': shape['cls_num'],
                            'local_id': shape['id']
                        })
            
            # Сопоставляем объекты внутри группы
            processed_ids = set()
            
            for i, obj1 in enumerate(group_objects):
                if i in processed_ids:
                    continue
                    
                # Находим похожие объекты
                similar_objects = [i]
                base_coord = obj1['geo_coord']
                base_class = obj1['class']
                
                for j, obj2 in enumerate(group_objects[i+1:], i+1):
                    if j in processed_ids:
                        continue
                        
                    if obj2['class'] != base_class:
                        continue
                    
                    distance = self.haversine_distance(base_coord, obj2['geo_coord'])
                    if distance <= self.threshold_distance:
                        similar_objects.append(j)
                
                # Создаем геохэш для группы объектов
                avg_lon = np.mean([group_objects[idx]['geo_coord'][0] for idx in similar_objects])
                avg_lat = np.mean([group_objects[idx]['geo_coord'][1] for idx in similar_objects])
                geo_hash = f"{base_class}_{avg_lon:.6f}_{avg_lat:.6f}"
                
                object_key = (group_name, geo_hash)
                
                if object_key not in global_objects_map:
                    n = next_id_by_class[base_class]
                    global_objects_map[object_key] = f"{base_class}_{n}"
                    next_id_by_class[base_class] += 1

                global_id = global_objects_map[object_key]
                
                # Присваиваем глобальный ID
                for idx in similar_objects:
                    obj = group_objects[idx]
                    images[obj['image']]["shapes"][obj['shape']['id']]['global_id'] = global_id
                    processed_ids.add(idx)
        
        return json_data

# ----------------------------------------------------------------------------------------------------------------------
# Аналитические функции
def analyze_results(json_data):
    """Анализ результатов сопоставления"""
    global_ids = defaultdict(list)
    
    for img_name, img_data in json_data["images"].items():
        for shape in img_data["shapes"]:
            if 'global_id' in shape:
                global_ids[shape['global_id']].append({
                    'image': img_name,
                    'class': shape['cls_num'],
                    'local_id': shape['id']
                })
    
    print(f"Всего уникальных объектов: {len(global_ids)}")
    
    for global_id, occurrences in list(global_ids.items())[:10]:
        print(f"Объект {global_id} встречается в {len(occurrences)} изображениях:")
        for occ in occurrences:
            print(f"  - {occ['image']} (класс: {occ['class']})")

def export_matching_table(json_data, output_file):
    """Экспорт таблицы сопоставления в CSV"""
    import csv
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Global_ID', 'Image', 'Class', 'Local_ID', 'Points_Count'])
        
        for img_name, img_data in json_data["images"].items():
            for shape in img_data["shapes"]:
                if 'global_id' in shape:
                    writer.writerow([
                        shape['global_id'],
                        img_name,
                        shape['cls_num'],
                        shape['id'],
                        len(shape['points'])
                    ])

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()