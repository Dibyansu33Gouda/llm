def get_weather(city: str) -> str:
    fake_data = {
        "Berhampur": "31°C, rain likely",
        "Hyderabad": "27°C, clear skies",
    }
    return fake_data.get(city, "No data for that city")

def celsius_to_fahrenheit(celcius:float)->str:
    return f"{celcius * 9/5 +32:.1f} *F"


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

convert_decl = {
    "name": "celsius_to_fahrenheit",
    "description": "Convert a temperature from Celsius to Fahrenheit. Use this whenever the user wants a temperature in Fahrenheit.",
    "parameters": {
        "type": "object",
        "properties": {
            "celsius": {"type": "number", "description": "Temperature in Celsius, e.g. 31"}
        },
        "required": ["celsius"],
    },
}

TOOLS = {
    "get_weather": get_weather,
    "celsius_to_fahrenheit":celsius_to_fahrenheit,
    }

DECLS = [get_weather_decl, convert_decl]