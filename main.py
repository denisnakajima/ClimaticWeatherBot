import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Token do Telegram
TELEGRAM_TOKEN = "7782730415:AAGMzwTvNP3ZnRJB25UGdhwr2jzR_uWmxW8"

# Função para buscar coordenadas da cidade (usando Open-Meteo)
def get_coordinates(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=pt&format=json"
    response = requests.get(url)
    
    if response.status_code == 200 and response.json().get("results"):
        data = response.json()["results"][0]
        return data["latitude"], data["longitude"]
    else:
        return None, None

# Função para buscar a previsão do tempo
def get_weather(city):
    lat, lon = get_coordinates(city)
    
    if lat is None or lon is None:
        return "❌ Cidade não encontrada! Tente novamente."
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=America/Sao_Paulo"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()["current_weather"]
        temp = data["temperature"]
        wind = data["windspeed"]
        condition = data["weathercode"]

        # Dicionário de condições climáticas básicas (simplificado)
        weather_conditions = {
            0: "☀️ Céu limpo",
            1: "🌤 Poucas nuvens",
            2: "⛅ Parcialmente nublado",
            3: "☁️ Nublado",
            45: "🌫 Névoa",
            48: "🌫 Névoa gelada",
            51: "🌦 Chuvisco",
            61: "🌧 Chuva leve",
            63: "🌧🌧 Chuva moderada",
            65: "🌧🌧🌧 Chuva forte",
            71: "❄️ Neve leve",
            73: "❄️❄️ Neve moderada",
            75: "❄️❄️❄️ Neve intensa",
            80: "🌦 Pancadas de chuva",
            81: "🌧🌧 Pancadas moderadas",
            82: "🌧🌧🌧 Pancadas fortes"
        }
        
        desc = weather_conditions.get(condition, "🌍 Clima desconhecido")
        
        return (
            f"🌤 *Previsão do tempo para {city.capitalize()}*\n"
            f"🌡 Temperatura: {temp}°C\n"
            f"💨 Vento: {wind} km/h\n"
            f"☁ Condição: {desc}"
        )
    else:
        return "❌ Erro ao obter previsão do tempo."

# Comando /start
async def start(update: Update, context):
    await update.message.reply_text("Olá! Envie o nome de uma cidade para saber a previsão do tempo. 🌎")

# Responde com a previsão do tempo
async def weather(update: Update, context):
    city = update.message.text
    forecast = get_weather(city)
    await update.message.reply_text(forecast, parse_mode="Markdown")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, weather))

    print("Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()