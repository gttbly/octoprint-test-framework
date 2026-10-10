from config.config import Config

print("URL:", Config.BASE_URL)
print("API Key:", Config.API_KEY[:5] + "..." if Config.API_KEY else "未读取到")
