"""Тесты привязки ДТП к дорожным сегментам."""

import geopandas as gpd
from shapely.geometry import LineString, Point

from geo_utils import summarize_road_accidents

UTM_UFA = "EPSG:32640"


def roads(rows):
    return gpd.GeoDataFrame(
        {"osm_type": ["way"] * len(rows), "osm_id": [row[0] for row in rows], "name": [None] * len(rows)},
        geometry=[LineString([(0, y), (100, y)]) for _, y in rows],
        crs=UTM_UFA,
    )


def accidents(rows):
    return gpd.GeoDataFrame(
        {
            "kart_id": range(1, len(rows) + 1),
            "injured": [row[1] for row in rows],
            "killed": [row[2] for row in rows],
        },
        geometry=[Point(50, y) for y, _, _ in rows],
        crs=UTM_UFA,
    )


def test_counts_accidents_at_distance_limit_and_sums_severity():
    events = accidents([(0, 2, 0), (50, 3, 1), (51, 4, 2)])
    matched, segments = summarize_road_accidents(events, roads([(10, 0)]), 50)

    assert matched["kart_id"].tolist() == [1, 2]
    assert matched["distance_m"].tolist() == [0, 50]
    assert segments[["accident_count", "injured", "killed"]].iloc[0].tolist() == [2, 5, 1]


def test_equal_distance_uses_smallest_osm_id_and_counts_accident_once():
    events = accidents([(10, 1, 0)])
    matched, segments = summarize_road_accidents(events, roads([(20, 0), (10, 20)]), 50)

    assert matched["osm_id"].tolist() == [10]
    assert segments["osm_id"].tolist() == [10]
    assert segments["accident_count"].tolist() == [1]


def test_no_nearby_roads_returns_empty_matches_and_segments():
    events = accidents([(100, 1, 0)])
    matched, segments = summarize_road_accidents(events, roads([(10, 0)]), 50)

    assert matched.empty
    assert segments.empty
    assert segments.crs == events.crs
