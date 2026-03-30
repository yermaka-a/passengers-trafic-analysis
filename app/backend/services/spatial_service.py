"""
Сервис пространственных вычислений на базе Shapely

Используется для:
- Проверки принадлежности точки полигону
- Поиска ближайшей точки на линии
- Вычисления расстояний между объектами

Установка: uv add shapely
"""
from typing import List, Dict, Optional, Tuple
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import nearest_points
import math


class SpatialService:
    """Сервис для работы с геопространственными данными"""

    def __init__(self):
        pass

    def is_point_in_polygon(self, lat: float, lng: float, polygon_coords: List[Dict]) -> bool:
        """
        Проверить: принадлежит ли точка полигону
        
        Args:
            lat: Широта точки
            lng: Долгота точки
            polygon_coords: Координаты полигона [{lat, lng}, ...]
            
        Returns:
            True если точка внутри полигона
        """
        try:
            point = Point(lng, lat)  # Shapely использует (lng, lat)
            polygon = Polygon([(c['lng'], c['lat']) for c in polygon_coords])
            return polygon.contains(point) or polygon.touches(point)
        except Exception as e:
            print(f"SpatialService.is_point_in_polygon error: {e}")
            return False

    def is_point_near_line(self, lat: float, lng: float, line_coords: List[Dict], 
                           tolerance_meters: float = 50.0) -> bool:
        """
        Проверить: находится ли точка возле линии (с допуском)
        
        Args:
            lat: Широта точки
            lng: Долгота точки
            line_coords: Координаты линии [{lat, lng}, ...]
            tolerance_meters: Допуск в метрах
            
        Returns:
            True если точка ближе чем tolerance_meters
        """
        try:
            point = Point(lng, lat)
            line = LineString([(c['lng'], c['lat']) for c in line_coords])
            
            # Находим ближайшую точку на линии
            nearest = nearest_points(point, line)[1]
            
            # Вычисляем расстояние в метрах
            distance_meters = self._haversine_distance(
                lat, lng,
                nearest.y, nearest.x
            )
            
            return distance_meters <= tolerance_meters
        except Exception as e:
            print(f"SpatialService.is_point_near_line error: {e}")
            return False

    def distance_point_to_line(self, lat: float, lng: float, 
                                line_coords: List[Dict]) -> float:
        """
        Вычислить расстояние от точки до линии (в метрах)
        
        Args:
            lat: Широта точки
            lng: Долгота точки
            line_coords: Координаты линии [{lat, lng}, ...]
            
        Returns:
            Расстояние в метрах
        """
        try:
            point = Point(lng, lat)
            line = LineString([(c['lng'], c['lat']) for c in line_coords])
            
            # Находим ближайшую точку на линии
            nearest = nearest_points(point, line)[1]
            
            # Вычисляем расстояние в метрах
            return self._haversine_distance(
                lat, lng,
                nearest.y, nearest.x
            )
        except Exception as e:
            print(f"SpatialService.distance_point_to_line error: {e}")
            return float('inf')

    def find_stops_in_polygon(self, stops: List[Dict], polygon_coords: List[Dict]) -> List[Dict]:
        """
        Найти все остановки в полигоне
        
        Args:
            stops: Список остановок [{"id": "...", "lat": ..., "lng": ...}, ...]
            polygon_coords: Координаты полигона [{lat, lng}, ...]
            
        Returns:
            Список остановок внутри полигона
        """
        try:
            polygon = Polygon([(c['lng'], c['lat']) for c in polygon_coords])
            result = []
            
            for stop in stops:
                point = Point(stop['lng'], stop['lat'])
                if polygon.contains(point) or polygon.touches(point):
                    result.append(stop)
            
            return result
        except Exception as e:
            print(f"SpatialService.find_stops_in_polygon error: {e}")
            return []

    def find_stops_near_polyline(self, stops: List[Dict], polyline_coords: List[Dict],
                                  tolerance_meters: float = 50.0) -> List[Dict]:
        """
        Найти все остановки возле полилинии
        
        Args:
            stops: Список остановок [{"id": "...", "lat": ..., "lng": ...}, ...]
            polyline_coords: Координаты полилинии [{lat, lng}, ...]
            tolerance_meters: Допуск в метрах
            
        Returns:
            Список остановок возле полилинии
        """
        try:
            line = LineString([(c['lng'], c['lat']) for c in polyline_coords])
            result = []
            
            for stop in stops:
                point = Point(stop['lng'], stop['lat'])
                nearest = nearest_points(point, line)[1]
                
                distance_meters = self._haversine_distance(
                    stop['lat'], stop['lng'],
                    nearest.y, nearest.x
                )
                
                if distance_meters <= tolerance_meters:
                    result.append(stop)
            
            return result
        except Exception as e:
            print(f"SpatialService.find_stops_near_polyline error: {e}")
            return []

    def _haversine_distance(self, lat1: float, lng1: float, 
                            lat2: float, lng2: float) -> float:
        """
        Вычислить расстояние между двумя точками (в метрах)
        Формула Haversine
        
        Args:
            lat1, lng1: Координаты первой точки
            lat2, lng2: Координаты второй точки
            
        Returns:
            Расстояние в метрах
        """
        R = 6371000  # Радиус Земли в метрах
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    def calculate_polygon_area(self, polygon_coords: List[Dict]) -> float:
        """
        Вычислить площадь полигона (в квадратных метрах)
        
        Args:
            polygon_coords: Координаты полигона [{lat, lng}, ...]
            
        Returns:
            Площадь в квадратных метрах
        """
        try:
            polygon = Polygon([(c['lng'], c['lat']) for c in polygon_coords])
            
            # Для точного вычисления площади нужно проекция
            # Используем приближённую формулу
            return polygon.area * 111000 * 111000  # Грубая оценка
        except Exception as e:
            print(f"SpatialService.calculate_polygon_area error: {e}")
            return 0.0

    def calculate_line_length(self, line_coords: List[Dict]) -> float:
        """
        Вычислить длину линии (в метрах)
        
        Args:
            line_coords: Координаты линии [{lat, lng}, ...]
            
        Returns:
            Длина в метрах
        """
        try:
            total_length = 0.0
            
            for i in range(len(line_coords) - 1):
                total_length += self._haversine_distance(
                    line_coords[i]['lat'], line_coords[i]['lng'],
                    line_coords[i + 1]['lat'], line_coords[i + 1]['lng']
                )
            
            return total_length
        except Exception as e:
            print(f"SpatialService.calculate_line_length error: {e}")
            return 0.0

    def get_nearest_stop(self, lat: float, lng: float, stops: List[Dict]) -> Optional[Dict]:
        """
        Найти ближайшую остановку
        
        Args:
            lat: Широта точки
            lng: Долгота точки
            stops: Список остановок [{"id": "...", "lat": ..., "lng": ...}, ...]
            
        Returns:
            Ближайшая остановка или None
        """
        try:
            if not stops:
                return None
            
            nearest_stop = None
            min_distance = float('inf')
            
            for stop in stops:
                distance = self._haversine_distance(
                    lat, lng,
                    stop['lat'], stop['lng']
                )
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_stop = stop
            
            if nearest_stop:
                nearest_stop['distance_meters'] = min_distance
            
            return nearest_stop
        except Exception as e:
            print(f"SpatialService.get_nearest_stop error: {e}")
            return None
