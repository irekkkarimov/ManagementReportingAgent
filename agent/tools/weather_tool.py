from langchain_core.tools import tool


@tool("get_weather", description="Возвращает погоду для указанного города city")
def get_weather(city: str) -> str:
    """
    Возвращает погоду в указанном городе
    :param city: город, погода в котором запрашивается, тип str
    :return: Заключение о погоде в указанном городе
    """
    # Replace with a real API call if needed
    return f"The weather in {city} is sunny with a high of 25°C."
