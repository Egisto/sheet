import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def diagnosticar_bot():
    print("🔍 Iniciando diagnóstico del bot...")
    
    # Verificar token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Error: No se encontró DISCORD_TOKEN en las variables de entorno")
        return False
    
    print("✅ Token encontrado en variables de entorno")
    
    # Verificar formato del token
    if not token.startswith('MTA') or len(token) < 50:
        print("❌ Error: El token no parece tener el formato correcto")
        print("   El token debe empezar con 'MTA' y tener al menos 50 caracteres")
        return False
    
    print("✅ Formato del token parece correcto")
    
    # Intentar conectar
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"✅ Bot conectado exitosamente como: {bot.user}")
        print(f"✅ ID del bot: {bot.user.id}")
        print(f"✅ Servidores conectados: {len(bot.guilds)}")
        
        for guild in bot.guilds:
            print(f"   - {guild.name} (ID: {guild.id})")
            print(f"     Permisos del bot: {guild.me.guild_permissions}")
        
        await bot.close()
    
    @bot.event
    async def on_error(event, *args, **kwargs):
        print(f"❌ Error en evento {event}: {args}")
    
    try:
        print("🔄 Intentando conectar a Discord...")
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Error: Token inválido o bot deshabilitado")
        return False
    except discord.HTTPException as e:
        print(f"❌ Error HTTP: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import asyncio
    asyncio.run(diagnosticar_bot()) 