"""
Overpass API клиент для получения остановок общественного транспорта из OpenStreetMap

Использует асинхронные запросы с rate limiting (2 запроса/сек)
"""
# -*- coding: utf-8 -*-

import httpx
import asyncio
from typing import List, Dict, Optional
from ..schemas.stop_import import OverpassStop
from ..logger import log


class OverpassClient:
    """Клиент для Overpass API"""
    
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    RATE_LIMIT_DELAY = 0.5  # 2 запроса в секунду
    TIMEOUT = 120.0  # 120 секунд таймаут (для больших городов)
    MAX_RETRIES = 3  # Количество попыток при ошибке
    
    def __init__(self):
        self._last_request_time = 0.0
    
    async def _rate_limit(self):
        """Rate limiting для Overpass API"""
        import time
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()
    
    async def fetch_stops(self, cities: List[str], stop_types: List[str]) -> List[OverpassStop]:
        """
        Получить остановки для списка городов
        
        Args:
            cities: Список городов (например: ["Ангарск", "Москва"])
            stop_types: Список типов остановок (например: ["bus_stop", "platform"])
        
        Returns:
            Список остановок
        """
        all_stops = []
        
        for city in cities:
            log.info("overpass_fetch_city", extra={"city": city})
            await self._rate_limit()
            try:
                stops = await self._fetch_city_stops(city, stop_types)
                log.info("overpass_city_result", extra={"city": city, "count": len(stops)})
                all_stops.extend(stops)
            except Exception as e:
                log.error("overpass_fetch_error", extra={"city": city, "error": str(e)})
        
        log.info("overpass_total_result", extra={"total": len(all_stops), "cities": len(cities)})
        return all_stops
    
    async def _fetch_city_stops(self, city: str, stop_types: List[str]) -> List[OverpassStop]:
        """Получить остановки для одного города с retry логикой"""
        query = self._build_query(city, stop_types)
        
        log.info("overpass_sending_query", extra={"city": city, "query_length": len(query)})
        print(f'[Overpass] Отправка запроса для города: {city}')
        print(f'[Overpass] Query: {query[:200]}...')  # Первые 200 символов
        
        # Retry логика для обработки временных ошибок
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                    response = await client.post(
                        self.OVERPASS_URL,
                        data={"data": query},
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                    response.raise_for_status()
                    data = response.json()
                
                print(f'[Overpass] Получено элементов: {len(data.get("elements", []))}')
                return self._parse_response(data, city)
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 504 and attempt < self.MAX_RETRIES - 1:
                    # Gateway Timeout - пробуем снова
                    wait_time = 2 ** attempt  # Экспоненциальная задержка: 1s, 2s, 4s
                    log.warning("overpass_504_retry", extra={"city": city, "attempt": attempt + 1, "wait_seconds": wait_time})
                    print(f'[Overpass] 504 ошибка, попытка {attempt + 1}/{self.MAX_RETRIES}. Ждём {wait_time}s...')
                    await asyncio.sleep(wait_time)
                    last_error = e
                else:
                    raise
            except httpx.ReadTimeout as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    log.warning("overpass_timeout_retry", extra={"city": city, "attempt": attempt + 1, "wait_seconds": wait_time})
                    print(f'[Overpass] Timeout, попытка {attempt + 1}/{self.MAX_RETRIES}. Ждём {wait_time}s...')
                    await asyncio.sleep(wait_time)
                    last_error = e
                else:
                    raise
        
        # Все попытки исчерпаны
        raise last_error or Exception("Неизвестная ошибка Overpass API")
    
    def _build_query(self, city: str, stop_types: List[str]) -> str:
        """
        Построить Overpass QL запрос
        
        Args:
            city: Название города
            stop_types: Список типов остановок
        
        Returns:
            Overpass QL запрос
        """
        type_queries = []
        
        for stop_type in stop_types:
            if stop_type == "bus_stop":
                type_queries.append('node["highway"="bus_stop"](area.searchArea);')
                type_queries.append('way["highway"="bus_stop"](area.searchArea);')
            elif stop_type == "platform":
                type_queries.append('node["public_transport"="platform"](area.searchArea);')
                type_queries.append('way["public_transport"="platform"](area.searchArea);')
            elif stop_type == "tram_stop":
                type_queries.append('node["railway"="tram_stop"](area.searchArea);')
            elif stop_type == "train_station":
                type_queries.append('node["railway"="station"](area.searchArea);')
                type_queries.append('way["railway"="station"](area.searchArea);')
        
        query = f"""
        [out:json][timeout:{int(self.TIMEOUT)}];
        area["name"="{city}"]->.searchArea;
        (
            {''.join(type_queries)}
        );
        out center;
        """
        
        log.debug("overpass_query", extra={"city": city, "query_length": len(query)})
        return query
    
    def _parse_response(self, data: Dict, city: str) -> List[OverpassStop]:
        """
        Распарсить JSON ответ от Overpass
        
        Args:
            data: JSON ответ от Overpass
            city: Название города (для логирования)
        
        Returns:
            Список остановок
        """
        stops = []
        
        for element in data.get('elements', []):
            stop = None
            
            if element['type'] == 'node':
                tags = element.get('tags', {})
                stop = OverpassStop(
                    osm_id=f"node_{element['id']}",
                    name=tags.get('name') or tags.get('ref') or f"Остановка {element['id']}",
                    lat=element['lat'],
                    lon=element['lon'],
                    type=tags.get('highway') or tags.get('public_transport', 'unknown'),
                    tags=tags
                )
            
            elif element['type'] == 'way' and 'center' in element:
                tags = element.get('tags', {})
                stop = OverpassStop(
                    osm_id=f"way_{element['id']}",
                    name=tags.get('name') or tags.get('ref') or f"Остановка {element['id']}",
                    lat=element['center']['lat'],
                    lon=element['center']['lon'],
                    type=tags.get('highway') or tags.get('public_transport', 'unknown'),
                    tags=tags
                )
            
            if stop:
                stops.append(stop)
        
        log.info("overpass_parsed", extra={"city": city, "parsed_count": len(stops)})
        return stops
