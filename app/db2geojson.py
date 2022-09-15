import json
import pathlib
from datetime import datetime, timedelta, timezone
from typing import Any
import matplotlib.pyplot as plt

<<<<<<< main
from .wbgt_util import wbgt_status
from .models import point_name
import cartopy.crs as ccrs

=======
>>>>>>> contour option
# from .models import point_name


class wbgt_point:
    def __init__(
        self,
        ido: float,
        keido: float,
        month: int,
        day: int,
        hour: int,
        severity: int,
        type: str = "Feature",
    ) -> None:
        self.type: str = type
        self.geometry: dict[str, Any] = {"type": "Point", "coordinates": (keido, ido)}
        self.properties: dict[str, Any] = {"Month": month, "Day": day, "Hour": hour, "severity": severity}


class com_geojson:
    def __init__(self, type: str = "FeatureCollection"):
        self.type = type
        self.features: list[dict[str, Any]] = []


# jp = json.dumps(p.__dict__)
# print(jp)


def data2geojson(file_name: str = "info.geojson", force: bool = False):
    target = pathlib.Path(__file__).parent / "static" / file_name

    date: int = datetime.now(timezone(timedelta(hours=9), "JST")).day

    if force or not target.exists():
        print("Generate GeoJson")

        g = com_geojson()

        for point in point_name.objects.all():
            try:
                for time, wbgt in zip(point.wbgt_time_json["time"], point.wbgt_time_json["wbgt"]):
                    month, day, hour = time.split("/")

                    for v in wbgt_status.values():
                        if v.min <= wbgt < v.max:
                            severity = v.level
                            break
                    else:
                        severity = 0

                    g.features.append(
                        wbgt_point(
                            ido=point.ido,
                            keido=point.keido,
                            month=int(month),
                            day=int(day),
                            hour=int(hour.split(":")[0]) + 24 * (date != int(day)),
                            severity=severity,
                        ).__dict__
                    )
            except TypeError:
                pass

        with open(target, mode="w+") as f:
            json.dump(g.__dict__, f)


def sample_data(shape=(73, 145)):
    """Return ``lons``, ``lats`` and ``data`` of some fake data."""
    nlats, nlons = shape
    lats = np.linspace(-np.pi / 2, np.pi / 2, nlats)
    lons = np.linspace(0, 2 * np.pi, nlons)
    lons, lats = np.meshgrid(lons, lats)
    wave = 0.75 * (np.sin(2 * lats) ** 8) * np.cos(4 * lons)
    mean = 0.5 * np.cos(2 * lats) * ((np.sin(2 * lats)) ** 2 + 2)

    lats = np.rad2deg(lats)
    lons = np.rad2deg(lons)
    data = wave + mean

    print(data)

    return lons, lats, data


def contourf(file_name: str = "info.geojson", hour=1):
    json_data = json.load(open(pathlib.Path(__file__).parent / "static" / file_name, mode="r"))

    idos = []
    keidos = []
    seviraritys = []

    for point_info in json_data["features"]:
        geo, prop = point_info["geometry"], point_info["properties"]

        if prop["Hour"] == hour:
            idos.append(geo["coordinates"][1])
            keidos.append(geo["coordinates"][0])
            seviraritys.append(prop["sevirarity"])

    import folium
    from folium import plugins
    import random

    center = [32, 131]
    m = folium.Map(location=center, zoom_start=5)

    folium.plugins.HeatMap(
        data=[(ido, keido, random.randint(0, 100)) for ido, keido, data in zip(idos, keidos, seviraritys)],  # ２次元を渡す
        radius=15,
    ).add_to(m)
    m.save("pcr_positive.html")


if __name__ == "__main__":
    contourf()
