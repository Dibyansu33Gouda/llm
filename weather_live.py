import requests 

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

LEVEL_NAMES = ["normal", "watch", "high", "severe"]

def _locate(city: str):
    r = requests.get(GEOCODE_URL, params={"name": city, "count": 1}, timeout=10)
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        raise ValueError(f"Could not find a place called {city}")
    
    top = results[0]
    label = ", ".join(x for x in [top["name"], top.get("admin1"), top.get("country")] if x)
    return top["latitude"], top["longitude"], label


def get_forecast(city: str, days: int = 7) -> dict:
    days = max(1, min(int(days), 16))
    lat, lon, label = _locate(city)
    r = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_gusts_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_gusts_10m_max",
            "forecast_days": days,
            "timezone": "auto",
        },
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    d = data["daily"]
    return {
        "place": label,
        "now": data["current"],
        "daily": [
            {
                "date": d["time"][i],
                "temp_max_c": d["temperature_2m_max"][i],
                "temp_min_c": d["temperature_2m_min"][i],
                "rain_mm": d["precipitation_sum"][i] or 0,
                "gust_kmh": d["wind_gusts_10m_max"][i] or 0,
            }
            for i in range(len(d["time"]))
        ],
    }


def _level(rain_mm: float, gust_kmh: float) -> int:
    rain = 3 if rain_mm >= 115 else 2 if rain_mm >= 64.5 else 1 if rain_mm >= 30 else 0
    wind = 3 if gust_kmh >= 90 else 2 if gust_kmh >= 60 else 1 if gust_kmh >= 40 else 0
    return max(rain, wind)


def assess_risk(city: str, days: int = 7) -> dict:
    fc = get_forecast(city, days)
    rows = fc["daily"]
    levels = [_level(row["rain_mm"], row["gust_kmh"]) for row in rows]
    peak = max(levels)
    risky = [i for i, lv in enumerate(levels) if lv > 0]

    if not risky:
        back_to_normal, note = None, "No risky days in this forecast window."
    elif risky[-1] == len(rows) - 1:
        back_to_normal = None
        note = "Still risky on the last forecast day, so the end date is unknown."
    else:
        back_to_normal = rows[risky[-1] + 1]["date"]
        note = "Conditions return to normal after the last risky day."

    return {
        "place": fc["place"],
        "peak_risk": LEVEL_NAMES[peak],
        "peak_date": rows[levels.index(peak)]["date"] if peak else None,
        "back_to_normal_date": back_to_normal,
        "note": note,
        "days": [
            {**row, "risk": LEVEL_NAMES[lv]} for row, lv in zip(rows, levels)
        ],
    }


get_forecast_decl = {
    "name": "get_forecast",
    "description": "Get current conditions and a daily forecast (temperature, rain in mm, max wind gust in km/h) for a city, up to 16 days ahead.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. Berhampur"},
            "days": {"type": "integer", "description": "Forecast days, 1 to 16. Default 7."},
        },
        "required": ["city"],
    },
}

assess_risk_decl = {
    "name": "assess_risk",
    "description": "Rate each forecast day for a city as normal, watch, high or severe based on rain and wind gusts, and report the peak day and the first calm day afterwards. Use this before giving any safety or preparation advice.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. Berhampur"},
            "days": {"type": "integer", "description": "Forecast days, 1 to 16. Default 7."},
        },
        "required": ["city"],
    },
}

TOOLS = {"get_forecast": get_forecast, "assess_risk": assess_risk}
DECLS = [get_forecast_decl, assess_risk_decl]