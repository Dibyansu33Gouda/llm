def get_weather(city: str) -> str:
    fake_data = {
        "Berhampur": "31°C, rain likely",
        "Hyderabad": "27°C, clear skies",
    }
    return fake_data.get(city, "No data for that city")


get_weather_decl = {
    "name": "get_weather",
    "description": "Get the current weather for a city. Use this when the user asks about temperature, rain, or what to wear outside.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. Berhampur"}
        },
        "required": ["city"],
    },
}

TOOLS = {"get_weather": get_weather}