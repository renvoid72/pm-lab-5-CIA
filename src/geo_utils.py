"""Общие функции пространственных расчётов проекта.

Функции вынесены из ноутбуков, чтобы их можно было проверять автоматическими тестами
(tests/test_geo_utils.py) и использовать в нескольких ноутбуках одинаково.
В ноутбуке подключайте так:

    import sys; sys.path.append(str(BASE / "src"))   # в Colab BASE — папка на Диске с копией src/
    from geo_utils import to_metric, share_within
"""
from __future__ import annotations

import geopandas as gpd
import pandas as pd

ROAD_ID_COLUMNS = ["osm_type", "osm_id"]


def to_metric(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Возвращает слой в метрической проекции (зона UTM по центру слоя).

    Если слой уже в метрах, возвращает его без изменений.
    Если система координат не задана, выдаёт ошибку: угадывать её нельзя.
    """
    if gdf.crs is None:
        raise ValueError("У слоя не задана система координат (CRS)")
    if gdf.crs.is_projected:
        return gdf
    return gdf.to_crs(gdf.estimate_utm_crs())


def _require_metric(*layers: gpd.GeoDataFrame) -> None:
    for layer in layers:
        if layer.crs is None or not layer.crs.is_projected:
            raise ValueError("Расстояния считаются только в метрической проекции. Вызовите to_metric()")
    if len({layer.crs for layer in layers}) > 1:
        raise ValueError("Слои в разных системах координат. Приведите их к одной")


def nearest_distance(targets: gpd.GeoDataFrame, sources: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """Расстояние в метрах от каждого объекта targets до ближайшего объекта sources."""
    _require_metric(targets, sources)
    if sources.empty:
        raise ValueError("Слой sources пуст: расстояние до ближайшего объекта не определено")
    joined = gpd.sjoin_nearest(targets[["geometry"]], sources[["geometry"]], how="left", distance_col="dist")
    return joined.groupby(level=0)["dist"].min().reindex(targets.index)


def share_within(targets: gpd.GeoDataFrame, sources: gpd.GeoDataFrame, distance_m: float) -> float:
    """Доля объектов targets, у которых ближайший объект sources не дальше distance_m метров."""
    if distance_m <= 0:
        raise ValueError("Расстояние должно быть положительным")
    if targets.empty:
        return 0.0
    dist = nearest_distance(targets, sources)
    return float((dist <= distance_m).mean())


def summarize_road_accidents(
    city_accidents: gpd.GeoDataFrame,
    roads: gpd.GeoDataFrame,
    max_snap_distance_m: float,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Привязывает ДТП к ближайшим дорогам и возвращает совпадения и сводку по сегментам."""
    _require_metric(city_accidents, roads)
    if any(axis.unit_conversion_factor != 1 for axis in roads.crs.axis_info[:2]):
        raise ValueError("Система координат должна использовать метры")
    if max_snap_distance_m <= 0:
        raise ValueError("Расстояние должно быть положительным")
    trial_roads = roads.loc[
        roads.geometry.notna() & ~roads.geometry.is_empty,
        ROAD_ID_COLUMNS + ["name", "geometry"],
    ].copy()
    if trial_roads.empty or trial_roads[ROAD_ID_COLUMNS].isna().any().any():
        raise ValueError("Для расчёта нужны сегменты с геометрией и идентификаторами OSM")
    if trial_roads.duplicated(ROAD_ID_COLUMNS).any():
        raise ValueError("В слое дорог найдены повторяющиеся идентификаторы OSM")
    if city_accidents["kart_id"].isna().any() or city_accidents["kart_id"].duplicated().any():
        raise ValueError("Выгрузка ДТП должна содержать карточки с уникальными идентификаторами")

    nearest = gpd.sjoin_nearest(
        city_accidents[["kart_id", "injured", "killed", "geometry"]],
        trial_roads[ROAD_ID_COLUMNS + ["geometry"]],
        how="inner",
        max_distance=max_snap_distance_m,
        distance_col="distance_m",
    )
    matched = nearest.sort_values(["distance_m", *ROAD_ID_COLUMNS]).drop_duplicates("kart_id").copy()
    for column in ("injured", "killed"):
        values = pd.to_numeric(matched[column], errors="raise")
        if values.isna().any() or (values < 0).any() or (values % 1 != 0).any():
            raise ValueError(f"В поле {column} ожидаются целые неотрицательные значения")
        matched[column] = values.astype("int64")

    segment_counts = matched.groupby(ROAD_ID_COLUMNS, as_index=False).agg(
        accident_count=("kart_id", "size"),
        injured=("injured", "sum"),
        killed=("killed", "sum"),
    )
    trial_segments = trial_roads.merge(segment_counts, on=ROAD_ID_COLUMNS, validate="one_to_one")
    trial_segments = trial_segments.sort_values(
        ["accident_count", *ROAD_ID_COLUMNS],
        ascending=[False, True, True],
    )
    if trial_segments["accident_count"].sum() != len(matched):
        raise RuntimeError("Сумма ДТП по сегментам не совпадает с числом привязанных карточек")
    return matched, trial_segments
