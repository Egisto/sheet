import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuración de roles predefinidos para período de prueba
ROLES_PERIODO_PRUEBA = [
    "Informador de canales",  # Rol principal de período de prueba
    "Rol Dorado",  # Rol adicional
    "Suscriptor oro", # Otro rol que se puede asignar
    "Suscriptor plata",  # Rol principal de período de prueba
    "Suscriptor bronce",  # Rol adicional
    "Suscriptor"
]

@bot.event
async def on_ready():
    print(f'✅ {bot.user} se ha conectado a Discord!')
    print(f'📊 ID del bot: {bot.user.id}')
    print(f'🏠 Servidores conectados: {len(bot.guilds)}')
    
    # Listar servidores
    for guild in bot.guilds:
        print(f'   - {guild.name} (ID: {guild.id})')
        print(f'     Permisos: {guild.me.guild_permissions}')
    
    print('✅ Bot listo para usar comandos de prefijo:')
    print('   - !periodo-de-prueba <usuario>')
    print('   - !quitar-rol <usuario> <rol>')
    print('   - !roles-usuario <usuario>')
    print('   - !sync (solo administradores)')
    print(f'   - Roles predefinidos: {", ".join(ROLES_PERIODO_PRUEBA)}')

class RolView(discord.ui.View):
    def __init__(self, usuario, roles_disponibles):
        super().__init__(timeout=60)
        self.usuario = usuario
        self.roles_disponibles = roles_disponibles
        
        # Crear botones para cada rol disponible
        for rol in roles_disponibles:
            self.add_item(RolButton(rol))

class RolButton(discord.ui.Button):
    def __init__(self, rol):
        super().__init__(
            label=f"📋 {rol.name}",
            style=discord.ButtonStyle.primary,
            custom_id=f"rol_{rol.id}"
        )
        self.rol = rol

    async def callback(self, interaction: discord.Interaction):
        try:
            # Obtener el usuario del view
            usuario = self.view.usuario
            
            # Verificar si el usuario ya tiene el rol
            if self.rol in usuario.roles:
                await interaction.response.send_message(
                    f"❌ **{usuario.display_name}** ya tiene el rol **{self.rol.name}**",
                    ephemeral=True
                )
                return
            
            # Asignar el rol
            await usuario.add_roles(self.rol)
            
            embed = discord.Embed(
                title="✅ Rol Asignado Exitosamente",
                description=f"Se ha asignado el rol **{self.rol.name}** a **{usuario.display_name}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Usuario", value=usuario.mention, inline=True)
            embed.add_field(name="Rol", value=self.rol.mention, inline=True)
            embed.add_field(name="Asignado por", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=False)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para asignar este rol",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al asignar el rol: {str(e)}",
                ephemeral=True
            )

@bot.command(name="periodo-de-prueba", description="Asigna roles predefinidos de período de prueba a un usuario")
async def periodo_prueba(ctx, usuario: discord.Member):
    # Verificar permisos
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ No tienes permisos para gestionar roles")
        return
    
    # Verificar que el bot tenga permisos
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("❌ No tengo permisos para gestionar roles en este servidor")
        return
    
    try:
        # Buscar los roles predefinidos en el servidor
        roles_a_asignar = []
        roles_no_encontrados = []
        
        for nombre_rol in ROLES_PERIODO_PRUEBA:
            rol = discord.utils.get(ctx.guild.roles, name=nombre_rol)
            if rol:
                # Verificar que el bot puede asignar este rol
                if rol.position < ctx.guild.me.top_role.position and not rol.managed:
                    roles_a_asignar.append(rol)
                else:
                    roles_no_encontrados.append(nombre_rol)
            else:
                roles_no_encontrados.append(nombre_rol)
        
        if not roles_a_asignar:
            await ctx.send(f"❌ No se encontraron roles válidos para asignar. Roles configurados: {', '.join(ROLES_PERIODO_PRUEBA)}")
            if roles_no_encontrados:
                await ctx.send(f"⚠️ Roles no encontrados o sin permisos: {', '.join(roles_no_encontrados)}")
            return
        
        # Verificar roles que ya tiene el usuario
        roles_ya_asignados = []
        roles_nuevos = []
        
        for rol in roles_a_asignar:
            if rol in usuario.roles:
                roles_ya_asignados.append(rol)
            else:
                roles_nuevos.append(rol)
        
        # Asignar roles nuevos
        if roles_nuevos:
            await usuario.add_roles(*roles_nuevos)
        
        # Crear embed de respuesta
        embed = discord.Embed(
            title="✅ Período de Prueba Configurado",
            description=f"Se han configurado los roles de período de prueba para **{usuario.display_name}**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Asignado por", value=ctx.author.mention, inline=True)
        
        if roles_nuevos:
            embed.add_field(
                name="✅ Roles Asignados", 
                value=", ".join([rol.mention for rol in roles_nuevos]), 
                inline=False
            )
        
        if roles_ya_asignados:
            embed.add_field(
                name="ℹ️ Roles Ya Tenía", 
                value=", ".join([rol.mention for rol in roles_ya_asignados]), 
                inline=False
            )
        
        if roles_no_encontrados:
            embed.add_field(
                name="⚠️ Roles No Encontrados", 
                value=", ".join(roles_no_encontrados), 
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para asignar roles")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="quitar-rol", description="Quita un rol a un usuario")
async def quitar_rol(ctx, usuario: discord.Member, rol: discord.Role):
    # Verificar permisos
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ No tienes permisos para gestionar roles")
        return
    
    try:
        if rol not in usuario.roles:
            await ctx.send(f"❌ **{usuario.display_name}** no tiene el rol **{rol.name}**")
            return
        
        await usuario.remove_roles(rol)
        
        embed = discord.Embed(
            title="✅ Rol Removido Exitosamente",
            description=f"Se ha removido el rol **{rol.name}** de **{usuario.display_name}**",
            color=discord.Color.red()
        )
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Rol", value=rol.mention, inline=True)
        embed.add_field(name="Removido por", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para quitar roles")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="roles-usuario", description="Muestra todos los roles de un usuario")
async def roles_usuario(ctx, usuario: discord.Member):
    roles = [rol.mention for rol in usuario.roles if rol.name != "@everyone"]
    
    if not roles:
        embed = discord.Embed(
            title="👤 Roles del Usuario",
            description=f"**{usuario.display_name}** no tiene roles asignados",
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title="👤 Roles del Usuario",
            description=f"**{usuario.display_name}** tiene los siguientes roles:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Roles", value=" ".join(roles), inline=False)
    
    embed.add_field(name="Usuario", value=usuario.mention, inline=True)
    embed.add_field(name="Total de roles", value=str(len(roles)), inline=True)
    
    await ctx.send(embed=embed)

# Comando manual para sincronizar comandos
@bot.command(name='sync')
async def sync_commands(ctx):
    """Sincroniza los comandos slash manualmente"""
    if ctx.author.guild_permissions.administrator:
        try:
            print(f'🔄 Sincronización manual solicitada por {ctx.author}')
            synced = await bot.tree.sync()
            await ctx.send(f'✅ Sincronizados {len(synced)} comandos exitosamente!')
            print(f'✅ Sincronización manual completada: {len(synced)} comandos')
        except Exception as e:
            await ctx.send(f'❌ Error al sincronizar: {e}')
            print(f'❌ Error en sincronización manual: {e}')
    else:
        await ctx.send('❌ Solo los administradores pueden usar este comando')

# Manejo de errores
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permisos para usar este comando")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Faltan argumentos requeridos para este comando")
    else:
        await ctx.send(f"❌ Error: {str(error)}")

# Ejecutar el bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Error: No se encontró el token de Discord en las variables de entorno")
        exit(1)
    
    print("🚀 Iniciando bot de Discord...")
    bot.run(token) 