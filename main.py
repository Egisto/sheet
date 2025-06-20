import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import datetime

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
    print('   - !quitar-rol <usuario> <rol>')
    print('   - !roles-usuario <usuario>')
    print('   - !sync (solo administradores)')
    print('✅ Comandos slash disponibles:')
    print('   - /periodo-de-prueba <usuario>')
    print(f'   - Roles predefinidos: {", ".join(ROLES_PERIODO_PRUEBA)}')
    print('✅ Nuevo comando: /asignar-placa <usuario> <número_placa>')

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

@bot.tree.command(name="periodo-de-prueba", description="Asigna roles predefinidos de período de prueba a un usuario")
@app_commands.describe(usuario="Usuario al que asignar el período de prueba")
async def periodo_prueba(interaction: discord.Interaction, usuario: discord.Member):
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
        # Buscar los roles predefinidos en el servidor
        roles_a_asignar = []
        roles_no_encontrados = []
        
        for nombre_rol in ROLES_PERIODO_PRUEBA:
            rol = discord.utils.get(interaction.guild.roles, name=nombre_rol)
            if rol:
                # Verificar que el bot puede asignar este rol
                if rol.position < interaction.guild.me.top_role.position and not rol.managed:
                    roles_a_asignar.append(rol)
                else:
                    roles_no_encontrados.append(nombre_rol)
            else:
                roles_no_encontrados.append(nombre_rol)
        
        if not roles_a_asignar:
            await interaction.response.send_message(
                f"❌ No se encontraron roles válidos para asignar. Roles configurados: {', '.join(ROLES_PERIODO_PRUEBA)}",
                ephemeral=True
            )
            if roles_no_encontrados:
                await interaction.followup.send(
                    f"⚠️ Roles no encontrados o sin permisos: {', '.join(roles_no_encontrados)}",
                    ephemeral=True
                )
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
        
        # Enviar confirmación ephemeral al usuario que ejecutó el comando
        if roles_nuevos:
            roles_asignados_texto = ", ".join([rol.mention for rol in roles_nuevos])
            await interaction.response.send_message(
                f"✅ Se han asignado los roles: {roles_asignados_texto} a {usuario.mention}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"ℹ️ {usuario.mention} ya tenía todos los roles configurados",
                ephemeral=True
            )
        
        # Enviar mensaje al canal "boosts"
        await enviar_mensaje_periodo_prueba(interaction.guild, usuario, interaction.user)
        
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

async def enviar_mensaje_periodo_prueba(guild, usuario, autor_comando):
    """Envía el mensaje de período de prueba al canal 'boosts'"""
    try:
        # Buscar el canal "boosts"
        canal_boosts = discord.utils.get(guild.channels, name="boosts")
        
        if not canal_boosts:
            print("⚠️ Canal 'boosts' no encontrado")
            return
        
        # Calcular fechas
        fecha_inicio = datetime.datetime.now()
        fecha_caducidad = fecha_inicio + datetime.timedelta(days=7)
        
        # Crear timestamp para Discord
        timestamp_caducidad = int(fecha_caducidad.timestamp())
        
        # Crear embed del período de prueba
        embed_periodo = discord.Embed(
            title="🔄 Período de Pruebas",
            description=f"**Información acerca de este período de pruebas:**",
            color=discord.Color.yellow()
        )
        
        # Información del obrero en pruebas
        embed_periodo.add_field(
            name="👷 Obrero en pruebas:",
            value=f"{usuario.mention} (`{usuario.name}#{usuario.discriminator}` - ID: `{usuario.id}`)",
            inline=False
        )
        
        # Fechas
        embed_periodo.add_field(
            name="📅 Fechas:",
            value=f"⌛ **Fecha de inicio:** {fecha_inicio.strftime('%d/%m/%Y a las %H:%M')}\n"
                  f"⌛ **Fecha de caducidad:** <t:{timestamp_caducidad}:F> (<t:{timestamp_caducidad}:R>)",
            inline=False
        )
        
        # Objetivo
        embed_periodo.add_field(
            name="🎯 Objetivo:",
            value="Para finalizar este período de pruebas deberás de completar **3 formularios de actividad** y un **curso** para superar tu período de pruebas correctamente.",
            inline=False
        )
        
        # Footer con información adicional
        embed_periodo.set_footer(text=f"Período iniciado por {autor_comando.display_name}")
        embed_periodo.set_thumbnail(url=usuario.display_avatar.url)
        
        # Enviar mensaje al canal boosts
        await canal_boosts.send(content=f"{usuario.mention}", embed=embed_periodo)
        
        print(f"✅ Mensaje de período de prueba enviado al canal 'boosts' para {usuario.display_name}")
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje al canal boosts: {str(e)}")

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

@bot.command(name="periodo-de-prueba", description="Asigna roles predefinidos de período de prueba a un usuario")
async def periodo_prueba_prefix(ctx, usuario: discord.Member):
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
        
        # Enviar confirmación al canal donde se ejecutó el comando
        if roles_nuevos:
            roles_asignados_texto = ", ".join([rol.mention for rol in roles_nuevos])
            await ctx.send(f"✅ Se han asignado los roles: {roles_asignados_texto} a {usuario.mention}")
        else:
            await ctx.send(f"ℹ️ {usuario.mention} ya tenía todos los roles configurados")
        
        # Enviar mensaje al canal "boosts"
        await enviar_mensaje_periodo_prueba(ctx.guild, usuario, ctx.author)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para asignar roles")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="asignar-placa", description="Asigna un número de placa a un usuario y cambia su nickname")
@app_commands.describe(
    usuario="Usuario al que asignar la placa",
    numero_placa="Número de placa a asignar"
)
async def asignar_placa(interaction: discord.Interaction, usuario: discord.Member, numero_placa: int):
    # Verificar permisos
    if not interaction.user.guild_permissions.manage_nicknames:
        await interaction.response.send_message(
            "❌ No tienes permisos para gestionar nicknames",
            ephemeral=True
        )
        return
    
    # Verificar que el bot tenga permisos
    if not interaction.guild.me.guild_permissions.manage_nicknames:
        await interaction.response.send_message(
            "❌ No tengo permisos para gestionar nicknames en este servidor",
            ephemeral=True
        )
        return
    
    # Verificar que el número de placa sea válido
    if numero_placa <= 0 or numero_placa > 9999:
        await interaction.response.send_message(
            "❌ El número de placa debe estar entre 1 y 9999",
            ephemeral=True
        )
        return
    
    try:
        # Crear el nuevo nickname
        nuevo_nickname = f"NVI-{numero_placa:04d} | {usuario.name}"
        
        # Verificar si el nickname es muy largo (límite de Discord: 32 caracteres)
        if len(nuevo_nickname) > 32:
            # Truncar el nombre si es necesario
            nombre_truncado = usuario.name[:32 - len(f"NVI-{numero_placa:04d} | ")]
            nuevo_nickname = f"NVI-{numero_placa:04d} | {nombre_truncado}"
        
        # Cambiar el nickname del usuario
        await usuario.edit(nick=nuevo_nickname)
        
        # Enviar confirmación al usuario que ejecutó el comando
        await interaction.response.send_message(
            f"✅ Se ha asignado la placa **NVI-{numero_placa:04d}** a {usuario.mention}",
            ephemeral=True
        )
        
        # Enviar mensaje al canal "noticias-random"
        await enviar_mensaje_asignacion_placa(interaction.guild, usuario, numero_placa, interaction.user)
        
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ No tengo permisos para cambiar el nickname de este usuario",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )

async def enviar_mensaje_asignacion_placa(guild, usuario, numero_placa, autor_comando):
    """Envía el mensaje de asignación de placa al canal 'noticias-random'"""
    try:
        # Buscar el canal "noticias-random"
        canal_noticias = discord.utils.get(guild.channels, name="noticias-random")
        
        if not canal_noticias:
            print("⚠️ Canal 'noticias-random' no encontrado")
            return
        
        # Crear embed de asignación de placa
        embed_placa = discord.Embed(
            title="🛡️ Asignación de Placa",
            description=f"Enhorabuena {usuario.mention}, tu placa a partir de ahora será:",
            color=discord.Color.gold()
        )
        
        # Agregar el número de placa
        embed_placa.add_field(
            name="🆔 Número de Placa",
            value=f"**NVI-{numero_placa}**",
            inline=False
        )
        
        # Agregar instrucción
        embed_placa.add_field(
            name="📋 Instrucción",
            value="La deberás de utilizar en todo momento que estés en servicio.",
            inline=False
        )
        
        # Footer con información adicional
        embed_placa.set_footer(text=f"Placa asignada por {autor_comando.display_name}")
        embed_placa.set_thumbnail(url=usuario.display_avatar.url)
        
        # Enviar mensaje al canal noticias-random
        await canal_noticias.send(content=f"{usuario.mention}", embed=embed_placa)
        
        print(f"✅ Mensaje de asignación de placa enviado al canal 'noticias-random' para {usuario.display_name}")
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje al canal noticias-random: {str(e)}")

@bot.command(name="asignar-placa", description="Asigna un número de placa a un usuario y cambia su nickname")
async def asignar_placa_prefix(ctx, usuario: discord.Member, numero_placa: int):
    # Verificar permisos
    if not ctx.author.guild_permissions.manage_nicknames:
        await ctx.send("❌ No tienes permisos para gestionar nicknames")
        return
    
    # Verificar que el bot tenga permisos
    if not ctx.guild.me.guild_permissions.manage_nicknames:
        await ctx.send("❌ No tengo permisos para gestionar nicknames en este servidor")
        return
    
    # Verificar que el número de placa sea válido
    if numero_placa <= 0 or numero_placa > 9999:
        await ctx.send("❌ El número de placa debe estar entre 1 y 9999")
        return
    
    try:
        # Crear el nuevo nickname
        nuevo_nickname = f"NVI-{numero_placa:04d} | {usuario.name}"
        
        # Verificar si el nickname es muy largo (límite de Discord: 32 caracteres)
        if len(nuevo_nickname) > 32:
            # Truncar el nombre si es necesario
            nombre_truncado = usuario.name[:32 - len(f"NVI-{numero_placa:04d} | ")]
            nuevo_nickname = f"NVI-{numero_placa:04d} | {nombre_truncado}"
        
        # Cambiar el nickname del usuario
        await usuario.edit(nick=nuevo_nickname)
        
        # Enviar confirmación al canal donde se ejecutó el comando
        await ctx.send(f"✅ Se ha asignado la placa **NVI-{numero_placa:04d}** a {usuario.mention}")
        
        # Enviar mensaje al canal "noticias-random"
        await enviar_mensaje_asignacion_placa(ctx.guild, usuario, numero_placa, ctx.author)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para cambiar el nickname de este usuario")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# Ejecutar el bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Error: No se encontró el token de Discord en las variables de entorno")
        exit(1)
    
    print("🚀 Iniciando bot de Discord...")
    bot.run(token) 