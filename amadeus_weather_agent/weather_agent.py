import os
import re
import uuid
from datetime import datetime, timedelta
from aiohttp import web, ClientSession
from dotenv import load_dotenv

load_dotenv()

PORT = 10106
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def parse_weather_query(text: str):
    q = text.lower()

    # destination after "to"
    city = None
    m = re.search(r"\bto\s+([a-z\s]+?)(?:,|$)", q)
    if m:
        city = m.group(1).strip()

    # dates: Jan 21-25, 2026
    date_match = re.search(
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})-(\d{1,2}),\s*(\d{4})",
        q
    )

    month_map = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }

    start_date = None
    end_date = None

    if date_match:
        mon, d1, d2, year = date_match.groups()
        mm = month_map[mon]
        start_date = f"{year}-{mm}-{d1.zfill(2)}"
        end_date = f"{year}-{mm}-{d2.zfill(2)}"

    return city, start_date, end_date


def within_openweather_range(start_date: str, max_days: int = 5) -> bool:
    """
    OpenWeather free forecast: about 5 days ahead.
    """
    d = datetime.strptime(start_date, "%Y-%m-%d").date()
    today = datetime.now().date()
    return d <= (today + timedelta(days=max_days))


async def openweather_geocode(city: str):
    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city, "limit": 1, "appid": OPENWEATHER_API_KEY}

    async with ClientSession() as session:
        async with session.get(url, params=params, timeout=30) as resp:
            data = await resp.json()

    if not data:
        return None
    return data[0]["lat"], data[0]["lon"]


async def openweather_forecast(lat: float, lon: float):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    async with ClientSession() as session:
        async with session.get(url, params=params, timeout=30) as resp:
            return await resp.json()


def normalize_daily_from_3hour(forecast_json, start_date: str, end_date: str):
    """
    Convert 3-hour forecast -> daily min/max + total precipitation.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    daily = {}

    for item in forecast_json.get("list", []):
        dt_txt = item.get("dt_txt")  # "YYYY-MM-DD HH:MM:SS"
        if not dt_txt:
            continue

        day_str = dt_txt.split(" ")[0]
        day_date = datetime.strptime(day_str, "%Y-%m-%d").date()

        if day_date < start or day_date > end:
            continue

        temp_min = item.get("main", {}).get("temp_min")
        temp_max = item.get("main", {}).get("temp_max")
        rain_3h = float(item.get("rain", {}).get("3h", 0.0))
        condition = item.get("weather", [{}])[0].get("main")

        if day_str not in daily:
            daily[day_str] = {
                "min_temp_c": temp_min,
                "max_temp_c": temp_max,
                "precipitation_mm": rain_3h,
                "condition": condition
            }
        else:
            if temp_min is not None:
                daily[day_str]["min_temp_c"] = min(daily[day_str]["min_temp_c"], temp_min)
            if temp_max is not None:
                daily[day_str]["max_temp_c"] = max(daily[day_str]["max_temp_c"], temp_max)
            daily[day_str]["precipitation_mm"] += rain_3h

    result = []
    for day in sorted(daily.keys()):
        result.append({
            "date": day,
            "min_temp_c": round(daily[day]["min_temp_c"], 1) if daily[day]["min_temp_c"] is not None else None,
            "max_temp_c": round(daily[day]["max_temp_c"], 1) if daily[day]["max_temp_c"] is not None else None,
            "precipitation_mm": round(daily[day]["precipitation_mm"], 2),
            "condition": daily[day]["condition"],
            "source": "openweather-3hour-daily-summary"
        })

    return result


async def handle(request: web.Request):
    payload = await request.json()
    text = payload["params"]["message"]["parts"][0]["text"]

    req_id = payload.get("id", "1")
    task_id = str(uuid.uuid4())

    city, start_date, end_date = parse_weather_query(text)

    print("QUERY:", text)
    print("PARSED:", city, start_date, end_date)

    if not OPENWEATHER_API_KEY:
        data = [{"error": "Missing OPENWEATHER_API_KEY in .env"}]
        return web.json_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "kind": "artifact-update",
                "artifact": {"parts": [{"data": data}]},
                "taskId": task_id
            }
        })

    if not city or not start_date or not end_date:
        # Return fallback with parsed data
        if city:
            data = [{
                "city": city.title(),
                "month": "January",
                "note": "Unable to parse complete date range. Showing seasonal forecast.",
                "source": "fallback"
            }]
        else:
            data = []
        return web.json_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "kind": "artifact-update",
                "artifact": {"parts": [{"data": data}]},
                "taskId": task_id
            }
        })

    # OpenWeather limitation (5 days)
    if not within_openweather_range(start_date, max_days=5):
        data = [{
            "city": city.title(),
            "note": "OpenWeather free plan supports only ~5 days forecast. For future trips, show climate/seasonal summary.",
            "source": "fallback"
        }]
        return web.json_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "kind": "artifact-update",
                "artifact": {"parts": [{"data": data}]},
                "taskId": task_id
            }
        })

    try:
        coords = await openweather_geocode(city)
        if not coords:
            weather = [{
                "city": city.title(),
                "month": start_date.split("-")[1] if start_date else "Unknown",
                "note": f"Weather data not available for {city}. Please check city name.",
                "source": "fallback"
            }]
        else:
            lat, lon = coords
            forecast_json = await openweather_forecast(lat, lon)
            weather = normalize_daily_from_3hour(forecast_json, start_date, end_date)
            if not weather:
                # If no data for date range, return fallback
                weather = [{
                    "city": city.title(),
                    "month": start_date.split("-")[1] if start_date else "Unknown",
                    "note": "Weather data for selected dates will be available closer to travel date.",
                    "source": "fallback"
                }]

    except Exception as e:
        print(f"Weather API Error: {str(e)}")
        weather = [{
            "city": city.title() if city else "Unknown",
            "month": start_date.split("-")[1] if start_date else "Unknown",
            "note": f"Weather service error: {str(e)}. Please try again.",
            "source": "fallback"
        }]

    return web.json_response({
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "kind": "artifact-update",
            "artifact": {"parts": [{"data": weather}]},
            "taskId": task_id
        }
    })


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, port=PORT)
