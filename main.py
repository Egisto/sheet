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

@bot.event
async def on_ready():
    print(f'✅ {bot.user} se ha conectado a Discord!')
    print(f'📊 ID del bot: {bot.user.id}')
    print(f'🏠 Servidores conectados: {len(bot.guilds)}')
    
    # Listar servidores
    for guild in bot.guilds:
        print(f'   - {guild.name} (ID: {guild.id})')
        print(f'     Permisos: {guild.me.guild_permissions}')
    
    try:
        print('🔄 Sincronizando comandos...')
        synced = await bot.tree.sync()
        print(f'✅ Sincronizados {len(synced)} comandos exitosamente')
        
        # Listar comandos sincronizados
        for cmd in synced:
            print(f'   - /{cmd.name}: {cmd.description}')
            
    except Exception as e:
        print(f'❌ Error al sincronizar comandos: {e}')
        print('💡 Verifica que el bot tenga permisos de "applications.commands"')
        print('💡 Asegúrate de que el bot fue invitado con el scope "applications.commands"')

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

@bot.tree.command(name="periodo-de-prueba", description="Asigna un rol de período de prueba a un usuario")
@app_commands.describe(
    usuario="El usuario al que quieres asignar el rol",
    rol="El rol específico que quieres asignar (opcional)"
)
async def periodo_prueba(interaction: discord.Interaction, usuario: discord.Member, rol: discord.Role = None):
    # Verificar permisos
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "❌ No tienes permisos para gestionar roles",
            ephemeral=True
        )
        return
    
    # Verificar que el bot tenga permisos
    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "❌ No tengo permisos para gestionar roles en este servidor",
            ephemeral=True
        )
        return
    
    try:
        if rol:
            # Si se especifica un rol, asignarlo directamente
            if rol in usuario.roles:
                await interaction.response.send_message(
                    f"❌ **{usuario.display_name}** ya tiene el rol **{rol.name}**",
                    ephemeral=True
                )
                return
            
            await usuario.add_roles(rol)
            
            embed = discord.Embed(
                title="✅ Rol Asignado Exitosamente",
                description=f"Se ha asignado el rol **{rol.name}** a **{usuario.display_name}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Usuario", value=usuario.mention, inline=True)
            embed.add_field(name="Rol", value=rol.mention, inline=True)
            embed.add_field(name="Asignado por", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        else:
            # Si no se especifica rol, mostrar opciones
            # Obtener roles que el bot puede asignar (excluyendo @everyone y roles del bot)
            roles_disponibles = [
                r for r in interaction.guild.roles 
                if r.name != "@everyone" 
                and r.position < interaction.guild.me.top_role.position
                and not r.managed
            ]
            
            if not roles_disponibles:
                await interaction.response.send_message(
                    "❌ No hay roles disponibles para asignar",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🎯 Selecciona un Rol",
                description=f"Elige el rol que quieres asignar a **{usuario.display_name}**",
                color=discord.Color.blue()
            )
            embed.add_field(name="Usuario", value=usuario.mention, inline=True)
            embed.add_field(name="Roles disponibles", value=f"{len(roles_disponibles)} roles", inline=True)
            
            view = RolView(usuario, roles_disponibles)
            await interaction.response.send_message(embed=embed, view=view)
            
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ No tengo permisos para asignar roles",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="quitar-rol", description="Quita un rol a un usuario")
@app_commands.describe(
    usuario="El usuario al que quieres quitar el rol",
    rol="El rol que quieres quitar"
)
async def quitar_rol(interaction: discord.Interaction, usuario: discord.Member, rol: discord.Role):
    # Verificar permisos
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "❌ No tienes permisos para gestionar roles",
            ephemeral=True
        )
        return
    
    try:
        if rol not in usuario.roles:
            await interaction.response.send_message(
                f"❌ **{usuario.display_name}** no tiene el rol **{rol.name}**",
                ephemeral=True
            )
            return
        
        await usuario.remove_roles(rol)
        
        embed = discord.Embed(
            title="✅ Rol Removido Exitosamente",
            description=f"Se ha removido el rol **{rol.name}** de **{usuario.display_name}**",
            color=discord.Color.red()
        )
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Rol", value=rol.mention, inline=True)
        embed.add_field(name="Removido por", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ No tengo permisos para quitar roles",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="roles-usuario", description="Muestra todos los roles de un usuario")
@app_commands.describe(usuario="El usuario cuyos roles quieres ver")
async def roles_usuario(interaction: discord.Interaction, usuario: discord.Member):
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
    
    await interaction.response.send_message(embed=embed)

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