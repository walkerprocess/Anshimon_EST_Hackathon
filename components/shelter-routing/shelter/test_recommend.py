import asyncio
import contextlib
import importlib.util
import io
import json
import os
import py_compile
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("recommend.py")


def load_recommend_module():
    spec = importlib.util.spec_from_file_location("recommend_under_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load recommend.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


recommend = load_recommend_module()


class FakeResponse:
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def json(self, content_type=None):
        return self.body


class FakeSession:
    def __init__(self, get_body=None, post_body=None, post_status=200, error=None):
        self.get_body = get_body
        self.post_body = post_body
        self.post_status = post_status
        self.error = error

    def get(self, *args, **kwargs):
        if self.error:
            raise self.error
        return FakeResponse(self.get_body)

    def post(self, *args, **kwargs):
        if self.error:
            raise self.error
        return FakeResponse(self.post_body, self.post_status)


class FakeClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class DemoCoordinateRegressionTest(unittest.TestCase):
    def test_recommend_module_compiles(self) -> None:
        py_compile.compile(str(SCRIPT), doraise=True)

    def test_demo_coordinate_contains_latitude_and_longitude(self) -> None:
        self.assertEqual((37.5301, 127.1236), recommend.DEMO_LATLON)

    def test_offline_demo_runs(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            recommend.demo()
        self.assertTrue(output.getvalue().strip())

    def test_cli_demo_path_exits_cleanly(self) -> None:
        output = io.StringIO()
        with mock.patch.object(sys, "argv", [str(SCRIPT), "--demo"]):
            with contextlib.redirect_stdout(output):
                with self.assertRaises(SystemExit):
                    runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertTrue(output.getvalue().strip())


class ParsingTest(unittest.TestCase):
    def setUp(self) -> None:
        recommend._WARNED.clear()

    def test_pick_and_coordinate_detection(self) -> None:
        row = {"R_AREA_NM": "Shelter", "LOT": "126.9785", "LAT": "37.5670"}
        self.assertEqual("Shelter", recommend.pick(row, recommend.NAME_KEYS))
        self.assertEqual((37.567, 126.9785), recommend.latlon(row))
        self.assertIsNone(recommend.latlon({"LAT": "48.85", "LOT": "2.35"}))

    def test_to_shelter_normalizes_a_valid_row(self) -> None:
        row = {
            "시설명": "Community Center",
            "도로명주소": "1 Test Road",
            "경도": "127.12",
            "위도": "37.53",
        }
        self.assertEqual(
            {
                "name": "Community Center",
                "address": "1 Test Road",
                "lat": 37.53,
                "lon": 127.12,
            },
            recommend.to_shelter(row),
        )
        self.assertIsNone(recommend.to_shelter({"시설명": "No coordinates"}))

    def test_from_file_reads_csv_and_supported_json_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "shelters.csv"
            csv_path.write_text("name,lat,lon\nA,37.5,127.1\n", encoding="utf-8-sig")
            self.assertEqual("A", recommend.from_file(str(csv_path))[0]["name"])

            list_path = root / "list.json"
            list_path.write_text(json.dumps([{"name": "B"}]), encoding="utf-8")
            self.assertEqual([{"name": "B"}], recommend.from_file(str(list_path)))

            nested_path = root / "nested.json"
            nested_path.write_text(json.dumps({"service": {"row": [{"name": "C"}]}}), encoding="utf-8")
            self.assertEqual([{"name": "C"}], recommend.from_file(str(nested_path)))

            invalid_path = root / "invalid.json"
            invalid_path.write_text(json.dumps({"service": {}}), encoding="utf-8")
            with self.assertRaises(SystemExit):
                recommend.from_file(str(invalid_path))


class ProviderClientTest(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_shelters_returns_a_successful_page(self) -> None:
        body = {
            recommend.SERVICE: {
                "RESULT": {"CODE": "INFO-000"},
                "list_total_count": 1,
                "row": [{"name": "A"}],
            }
        }
        with mock.patch.dict(os.environ, {"SHELTER_API_BASE_URL": "test-key"}):
            rows = await recommend.fetch_shelters(FakeSession(get_body=body))
        self.assertEqual([{"name": "A"}], rows)

    async def test_fetch_shelters_requires_a_key(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"SHELTER_API_BASE_URL": "", "SHELTER_API_KEY": ""},
            clear=False,
        ):
            with self.assertRaises(SystemExit):
                await recommend.fetch_shelters(FakeSession())

    async def test_fetch_shelters_surfaces_provider_and_network_errors(self) -> None:
        provider_error = {
            recommend.SERVICE: {"RESULT": {"CODE": "ERROR-001", "MESSAGE": "bad"}}
        }
        empty = {recommend.SERVICE: {"RESULT": {"CODE": "INFO-000"}, "row": []}}
        with mock.patch.dict(os.environ, {"SHELTER_API_BASE_URL": "test-key"}):
            with self.assertRaises(SystemExit):
                await recommend.fetch_shelters(FakeSession(get_body=provider_error))
            with self.assertRaises(SystemExit):
                await recommend.fetch_shelters(FakeSession(get_body=empty))
            with self.assertRaises(SystemExit):
                await recommend.fetch_shelters(FakeSession(error=RuntimeError("offline")))

    async def test_walk_time_returns_route_metrics(self) -> None:
        response = {
            "features": [
                {"properties": {"totalDistance": 162.9, "totalTime": 181}}
            ]
        }
        destination = {"name": "Shelter", "lat": 37.53, "lon": 127.12}
        result = await recommend.walk_time(
            FakeSession(post_body=response), 37.50, 127.10, destination
        )
        self.assertEqual(162, result["walk_meters"])
        self.assertEqual(3, result["walk_minutes"])

    async def test_walk_time_returns_none_for_failed_routes(self) -> None:
        destination = {"name": "Shelter", "lat": 37.53, "lon": 127.12}
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertIsNone(
                await recommend.walk_time(
                    FakeSession(post_body={}, post_status=401), 37.50, 127.10, destination
                )
            )
            self.assertIsNone(
                await recommend.walk_time(
                    FakeSession(error=RuntimeError("offline")), 37.50, 127.10, destination
                )
            )


class RecommendationFlowTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        recommend._WARNED.clear()
        self.rows = [
            {"R_AREA_NM": "Near", "LAT": "37.531", "LOT": "127.121"},
            {"R_AREA_NM": "Fast", "LAT": "37.540", "LOT": "127.130"},
        ]

    async def test_recommendation_prefers_shorter_walk_and_flags_long_routes(self) -> None:
        async def fake_walk_time(session, lat, lon, destination):
            minutes = 25 if destination["name"] == "Near" else 5
            return destination | {"walk_minutes": minutes, "walk_meters": minutes * 80}

        with mock.patch.object(recommend.aiohttp, "ClientSession", return_value=FakeClientSession()):
            with mock.patch.object(recommend, "fetch_shelters", new=mock.AsyncMock(return_value=self.rows)):
                with mock.patch.object(recommend, "walk_time", new=fake_walk_time):
                    with contextlib.redirect_stderr(io.StringIO()):
                        result = await recommend.recommend(37.5301, 127.1236)

        self.assertEqual("Fast", result["name"])
        self.assertEqual(2, result["candidates"])
        self.assertFalse(result["needs_review"])

    async def test_recommendation_requires_review_when_all_routes_fail(self) -> None:
        async def failed_walk_time(session, lat, lon, destination):
            return None

        with mock.patch.object(recommend.aiohttp, "ClientSession", return_value=FakeClientSession()):
            with mock.patch.object(recommend, "fetch_shelters", new=mock.AsyncMock(return_value=self.rows)):
                with mock.patch.object(recommend, "walk_time", new=failed_walk_time):
                    with contextlib.redirect_stderr(io.StringIO()):
                        result = await recommend.recommend(37.5301, 127.1236)

        self.assertTrue(result["needs_review"])
        self.assertEqual("Near", result["nearest_by_line"])

    async def test_recommendation_rejects_rows_without_coordinates(self) -> None:
        with mock.patch.object(recommend.aiohttp, "ClientSession", return_value=FakeClientSession()):
            with mock.patch.object(
                recommend,
                "fetch_shelters",
                new=mock.AsyncMock(return_value=[{"R_AREA_NM": "Invalid"}]),
            ):
                with self.assertRaises(SystemExit):
                    await recommend.recommend(37.5301, 127.1236)


if __name__ == "__main__":
    unittest.main()
