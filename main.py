import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import datetime
import time
import re

# Cargar variables de entorno
load_dotenv()

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuración de roles predefinidos para período de prueba
ROLES_PERIODO_PRUEBA = [
    "═══════Medallas═══════",  # Rol principal de período de prueba
    "═══════Personal═══════",  # Rol adicional
    "🔖〴Nuevo Ingreso〴", # Otro rol que se puede asignar
    "👷〴Personal MTMS〴",  # Rol principal de período de prueba
    "═══════Departamento de Obras═══════",  # Rol adicional
    "👷〴 Obrero en Pruebas",
    "═══════Sanciones═══════",  # Rol principal de período de prueba
    "═══════Otros═══════",  # Rol adicional
    "Curso Aprendiz"
]

# Diccionario de prefijos de placa según el rol
PREFIJOS_PLACA = {
    "🚐〴Secretario De Infraestructura General〴": "SEC",
    "🚐〴Sub. Secretario De Infraestructura General〴": "SBC",
    "⛏️〴Director General〴": "DIR",
    "🎩〴Sub. Director General〴": "SDR",
    "🔧〴Director General En Pruebas〴": "DGP",
    "🔎🧰〴Supervisor General〴": "SPG",
    "💼🔧〴Inspector〴": "INS",
    "💼🚧〴Sub Inspector〴": "SBI",
    "🧰〴Jefe De Area Técnica〴": "JAT",
    "🚗〴Jefe De Incautaciones〴": "JIC",
    "🦺〴Jefe De Carreteras〴": "JCT",
    "🛑〴Tecnico Superior〴": "TCS",
    "⛔〴Operador Vial〴": "OPV",
    "🚧〴Auxiliar Vial〴": "AXV",
    "🚦〴Mecanico Experimentado〴": "MEC",
    "🔖〴Nuevo Ingreso〴": "NVI"
}

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
    
    # Iniciar la tarea de mensaje diario
    enviar_mensaje_actividad_diaria.start()
    print('✅ Tarea de mensaje diario iniciada')

@tasks.loop(minutes=1)
async def enviar_mensaje_actividad_diaria():
    """Envía el mensaje de actividad diaria todos los días a las 15:10 GMT+2"""
    # Obtener hora actual en UTC
    ahora_utc = datetime.datetime.utcnow()
    
    # Convertir a GMT+2 (UTC+2)
    ahora_gmt2 = ahora_utc + datetime.timedelta(hours=2)
    
    # Verificar si es la hora correcta (15:10)
    if ahora_gmt2.hour == 15 and ahora_gmt2.minute == 10:
        await enviar_mensaje_actividad()
        print(f"✅ Verificando hora: {ahora_gmt2.strftime('%H:%M')} - Enviando mensaje de actividad")
    else:
        # Solo imprimir cada 10 minutos para no saturar los logs
        if ahora_gmt2.minute % 10 == 0:
            print(f"⏰ Hora actual GMT+2: {ahora_gmt2.strftime('%H:%M')} - Esperando a las 15:10")

async def enviar_mensaje_actividad():
    """Envía el mensaje de actividad diaria al canal correspondiente"""
    try:
        # Obtener la fecha actual en formato español (GMT+2)
        fecha_actual = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        fecha_formateada = fecha_actual.strftime('%d/%m/%Y')
        
        # Buscar el canal de actividad
        for guild in bot.guilds:
            canal_actividad = discord.utils.get(guild.channels, name="↪⏰》𝗔ctividad")
            
            if not canal_actividad:
                print(f"⚠️ Canal '↪⏰》𝗔ctividad' no encontrado en {guild.name}")
                continue
            
            # Buscar el rol de Personal MTMS
            rol_personal = discord.utils.get(guild.roles, name="👷〴Personal MTMS〴")
            
            if not rol_personal:
                print(f"⚠️ Rol '👷〴Personal MTMS〴' no encontrado en {guild.name}")
                continue
            
            # Crear el mensaje de actividad diaria
            mensaje_actividad = f"""**ACTIVIDAD DIARIA**

El {rol_personal.mention} debe reaccionar a este mensaje para saber su actividad en MTMS. Es forma obligatoria para todos los rangos y así saber la actividad del servidor. El no reaccionar podría llevar a cabo una llamada de atención, un strike o un despido.

**FECHA DEL DÍA DE HOY:** {fecha_formateada}"""
            
            # Enviar el mensaje
            mensaje_enviado = await canal_actividad.send(content=mensaje_actividad)
            
            # Agregar reacción automática para facilitar la respuesta
            await mensaje_enviado.add_reaction('✅')
            
            print(f"✅ Mensaje de actividad diaria enviado en {guild.name} - {fecha_formateada}")
            
    except Exception as e:
        print(f"❌ Error al enviar mensaje de actividad diaria: {str(e)}")

# Comando manual para enviar mensaje de actividad (para pruebas)
@bot.tree.command(name="enviar-actividad", description="Envía manualmente el mensaje de actividad diaria")
async def enviar_actividad_manual(interaction: discord.Interaction):
    # Verificar permisos
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Solo los administradores pueden usar este comando",
            ephemeral=True
        )
        return
    
    try:
        await enviar_mensaje_actividad()
        await interaction.response.send_message(
            "✅ Mensaje de actividad diaria enviado manualmente",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error al enviar mensaje: {str(e)}",
            ephemeral=True
        )

# Comando manual para enviar mensaje de actividad (prefijo)
@bot.command(name="enviar-actividad", description="Envía manualmente el mensaje de actividad diaria")
async def enviar_actividad_manual_prefix(ctx):
    # Verificar permisos
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo los administradores pueden usar este comando")
        return
    
    try:
        await enviar_mensaje_actividad()
        await ctx.send("✅ Mensaje de actividad diaria enviado manualmente")
    except Exception as e:
        await ctx.send(f"❌ Error al enviar mensaje: {str(e)}")

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
@app_commands.describe(
    usuario="Usuario al que asignar el período de prueba",
    usuario_roblox="Usuario de Roblox del nuevo ingreso"
)
async def periodo_prueba(interaction: discord.Interaction, usuario: discord.Member, usuario_roblox: str):
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
            mensaje_error = f"❌ No se encontraron roles válidos para asignar. Roles configurados: {', '.join(ROLES_PERIODO_PRUEBA)}"
            if roles_no_encontrados:
                mensaje_error += f"\n⚠️ Roles no encontrados o sin permisos: {', '.join(roles_no_encontrados)}"
            
            await interaction.response.send_message(mensaje_error, ephemeral=True)
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
        
        # Cambiar el nickname por el usuario de Roblox, manteniendo la placa si existe
        try:
            nickname_actual = usuario.nick or usuario.name
            match = re.match(r"^([A-Z]{3}-\d{1,2}) \| .+$", nickname_actual)
            if match:
                placa = match.group(1)
                nuevo_nick = f"{placa} | {usuario_roblox}"
            else:
                nuevo_nick = usuario_roblox

            if len(nuevo_nick) > 32:
                nuevo_nick = nuevo_nick[:32]

            await usuario.edit(nick=nuevo_nick)
        except Exception as e:
            print(f"❌ Error al cambiar el nickname: {str(e)}")

        # Preparar mensaje de confirmación
        if roles_nuevos:
            roles_asignados_texto = ", ".join([rol.mention for rol in roles_nuevos])
            mensaje_confirmacion = f"✅ Se han asignado los roles: {roles_asignados_texto} a {usuario.mention}"
        else:
            mensaje_confirmacion = f"ℹ️ {usuario.mention} ya tenía todos los roles configurados"
        
        # Enviar confirmación ephemeral al usuario que ejecutó el comando
        await interaction.response.send_message(mensaje_confirmacion, ephemeral=True)
        
        # Enviar mensaje al canal después de la respuesta
        try:
            await enviar_mensaje_periodo_prueba(interaction.guild, usuario, interaction.user, usuario_roblox)
        except Exception as e:
            print(f"❌ Error al enviar mensaje al canal: {str(e)}")
        
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

async def enviar_mensaje_periodo_prueba(guild, usuario, autor_comando, usuario_roblox):
    """Envía el mensaje de período de prueba al canal '↪📰》𝗣eriodo-de-𝗣rueba'"""
    try:
        # Buscar el canal "boosts"
        canal_boosts = discord.utils.get(guild.channels, name="↪📰》𝗣eriodo-de-𝗣rueba")
        
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
            color=discord.Color.gold()
        )
        
        # Información del obrero en pruebas
        embed_periodo.add_field(
            name="👷 Obrero en pruebas:",
            value=f"{usuario.mention} (`{usuario.name}#{usuario.discriminator}` - ID: `{usuario.id}`)\n**Usuario de Roblox:** `{usuario_roblox}`",
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
        await enviar_mensaje_periodo_prueba(ctx.guild, usuario, ctx.author, "N/A") # Assuming no Roblox user for prefix command
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para asignar roles")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="asignar-placa", description="Asigna un número de placa a un usuario y cambia su nickname")
@app_commands.describe(
    usuario="Usuario al que asignar la placa",
    numero_placa="Número de placa a asignar (1-99)"
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
    
    # Verificar que el número de placa sea válido (máximo 2 dígitos)
    if numero_placa <= 0 or numero_placa > 99:
        await interaction.response.send_message(
            "❌ El número de placa debe estar entre 1 y 99",
            ephemeral=True
        )
        return
    
    try:
        # Obtener el nickname actual o el nombre si no tiene nickname
        nombre_actual = usuario.nick if usuario.nick else usuario.name
        nuevo_nickname = f"NVI-{numero_placa} | {nombre_actual}"
        
        # Verificar si el nickname es muy largo (límite de Discord: 32 caracteres)
        if len(nuevo_nickname) > 32:
            # Truncar el nombre si es necesario
            nombre_truncado = nombre_actual[:32 - len(f"NVI-{numero_placa} | ")]
            nuevo_nickname = f"NVI-{numero_placa} | {nombre_truncado}"
        
        # Cambiar el nickname del usuario
        await usuario.edit(nick=nuevo_nickname)
        
        # Enviar confirmación solo al usuario que ejecutó el comando (ephemeral)
        await interaction.response.send_message(
            f"✅ Se ha asignado la placa **NVI-{numero_placa}** a {usuario.mention}",
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
    """Envía el mensaje de asignación de placa al canal '↪🆔》𝗣lacas-𝗔signadas'"""
    try:
        # Buscar el canal "↪🆔》𝗣lacas-𝗔signadas"
        canal_noticias = discord.utils.get(guild.channels, name="↪🆔》𝗣lacas-𝗔signadas")
        
        if not canal_noticias:
            print("⚠️ Canal '↪🆔》𝗣lacas-𝗔signadas' no encontrado")
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
        
        print(f"✅ Mensaje de asignación de placa enviado al canal '↪🆔》𝗣lacas-𝗔signadas' para {usuario.display_name}")
        
        # Enviar mensaje de bienvenida al canal de empleados
        await enviar_mensaje_bienvenida_empleados(guild, usuario)
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje al canal noticias-random: {str(e)}")

async def enviar_mensaje_bienvenida_empleados(guild, usuario):
    """Envía el mensaje de bienvenida al canal '↪🧥》𝗖hat-𝗘mpleados'"""
    try:
        # Buscar el canal "↪🧥》𝗖hat-𝗘mpleados"
        canal_empleados = discord.utils.get(guild.channels, name="↪🧥》𝗖hat-𝗘mpleados")
        
        if not canal_empleados:
            print("⚠️ Canal '↪🧥》𝗖hat-𝗘mpleados' no encontrado")
            return
        
        # Buscar los canales mencionados para crear enlaces
        canal_licencias = discord.utils.get(guild.channels, name="↪💳》𝗟icencias")
        canal_tutoriales = discord.utils.get(guild.channels, name="↪🥏》𝗧utoriales-𝗦ugerencias")
        canal_guia = discord.utils.get(guild.channels, name="↪📚》𝙂uía")
        
        # Crear enlaces a los canales (si existen)
        enlace_licencias = f"<#{canal_licencias.id}>" if canal_licencias else "#↪💳》𝗟icencias"
        enlace_tutoriales = f"<#{canal_tutoriales.id}>" if canal_tutoriales else "#↪🥏》𝗧utoriales-𝗦ugerencias"
        enlace_guia = f"<#{canal_guia.id}>" if canal_guia else "#↪📚》𝙂uía"
        
        # Crear el mensaje de bienvenida con enlaces
        mensaje_bienvenida = f"""{usuario.mention} :wave: ¡Bienvenida/o a MTMS! 

Antes de empezar, asegúrate de:

:credit_card:  Sacar tu Licencia B y subirla a {enlace_licencias}
:movie_camera: Ver los tutoriales y la guía  {enlace_tutoriales}   {enlace_guia}
:blue_book: Completar el curso obligatorio
:pencil: En tus primeros 7 días, debes enviar 3 formularios para pasar el periodo de prueba.

¡Buena suerte y cualquier duda no dudéis en preguntarme!"""
        
        # Enviar mensaje al canal de empleados
        await canal_empleados.send(content=mensaje_bienvenida)
        
        print(f"✅ Mensaje de bienvenida enviado al canal '↪🧥》𝗖hat-𝗘mpleados' para {usuario.display_name}")
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje de bienvenida al canal de empleados: {str(e)}")

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
    
    # Verificar que el número de placa sea válido (máximo 2 dígitos)
    if numero_placa <= 0 or numero_placa > 99:
        await ctx.send("❌ El número de placa debe estar entre 1 y 99")
        return
    
    try:
        # Crear el nuevo nickname
        nuevo_nickname = f"NVI-{numero_placa} | {usuario.name}"
        
        # Verificar si el nickname es muy largo (límite de Discord: 32 caracteres)
        if len(nuevo_nickname) > 32:
            # Truncar el nombre si es necesario
            nombre_truncado = usuario.name[:32 - len(f"NVI-{numero_placa} | ")]
            nuevo_nickname = f"NVI-{numero_placa} | {nombre_truncado}"
        
        # Cambiar el nickname del usuario
        await usuario.edit(nick=nuevo_nickname)
        
        # Enviar confirmación solo al usuario que ejecutó el comando (ephemeral para slash, público para prefijo)
        await ctx.send(f"✅ Se ha asignado la placa **NVI-{numero_placa}** a {usuario.mention}")
        
        # Enviar mensaje al canal "noticias-random"
        await enviar_mensaje_asignacion_placa(ctx.guild, usuario, numero_placa, ctx.author)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para cambiar el nickname de este usuario")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="ascenso", description="Asciende a un usuario a un nuevo rango")
@app_commands.describe(
    usuario="Usuario al que ascender",
    rango="Rol al que ascender al usuario",
    motivo="Motivo del ascenso"
)
async def ascenso(interaction: discord.Interaction, usuario: discord.Member, rango: discord.Role, motivo: str):
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
        # Verificar que el bot puede asignar este rol
        if rango.position >= interaction.guild.me.top_role.position or rango.managed:
            await interaction.response.send_message(
                f"❌ No tengo permisos para asignar el rol '{rango.name}'",
                ephemeral=True
            )
            return
        
        # Verificar si el usuario ya tiene el rol
        if rango in usuario.roles:
            await interaction.response.send_message(
                f"❌ {usuario.mention} ya tiene el rol '{rango.name}'",
                ephemeral=True
            )
            return
        
        # Asignar el rol
        await usuario.add_roles(rango)
        
        # Cambiar la placa si el rol está en el diccionario
        prefijo = PREFIJOS_PLACA.get(rango.name)
        if prefijo:
            # Intentar extraer el número de placa del nickname actual
            numero_placa = "00"
            if usuario.nick:
                match = re.match(r"^[A-Z]{3}-?(\d{1,2})\s*\|", usuario.nick)
                if match:
                    numero_placa = match.group(1)
            nuevo_nickname = f"{prefijo}-{numero_placa} | {usuario.name}"
            if len(nuevo_nickname) > 32:
                nombre_truncado = usuario.name[:32 - len(f"{prefijo}-{numero_placa} | ")]
                nuevo_nickname = f"{prefijo}-{numero_placa} | {nombre_truncado}"
            try:
                await usuario.edit(nick=nuevo_nickname)
            except Exception as e:
                print(f"❌ Error al cambiar la placa: {str(e)}")
        
        # Enviar confirmación al usuario que ejecutó el comando
        await interaction.response.send_message(
            f"✅ Se ha ascendido a {usuario.mention} al rango **{rango.name}**",
            ephemeral=True
        )
        
        # Enviar mensaje al canal de ascensos
        await enviar_mensaje_ascenso(interaction.guild, usuario, rango, motivo, interaction.user)
        
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

async def enviar_mensaje_ascenso(guild, usuario, rango, motivo, autor_comando):
    """Envía el mensaje de ascenso al canal '↪📣》𝗦ubir-𝗕ajar-𝗥ango'"""
    try:
        # Buscar el canal "↪📣》𝗦ubir-𝗕ajar-𝗥ango"
        canal_ascensos = discord.utils.get(guild.channels, name="↪📣》𝗦ubir-𝗕ajar-𝗥ango")
        
        if not canal_ascensos:
            print("⚠️ Canal '↪📣》𝗦ubir-𝗕ajar-𝗥ango' no encontrado")
            return
        
        # Crear embed de ascenso
        embed_ascenso = discord.Embed(
            title="🎉 ¡Enhorabuena por tu ascenso!",
            description=f"**Información acerca de este ascenso:**",
            color=discord.Color.gold()
        )
        
        # Información del obrero ascendido
        embed_ascenso.add_field(
            name="👷 Obrero ascendido:",
            value=f"{usuario.mention} (`{usuario.name}#{usuario.discriminator}` - ID: `{usuario.id}`)",
            inline=False
        )
        
        # Rango ascendido
        embed_ascenso.add_field(
            name="🥇 Rango ascendido:",
            value=f"{rango.mention}",
            inline=False
        )
        
        # Motivo
        embed_ascenso.add_field(
            name="💬 Motivo:",
            value=motivo,
            inline=False
        )
        
        # Footer con información adicional
        embed_ascenso.set_footer(text=f"Ejecuta: {autor_comando.display_name}")
        embed_ascenso.set_thumbnail(url=usuario.display_avatar.url)
        
        # Enviar mensaje al canal de ascensos
        await canal_ascensos.send(content=f"{usuario.mention}", embed=embed_ascenso)
        
        print(f"✅ Mensaje de ascenso enviado al canal '↪📣》𝗦ubir-𝗕ajar-𝗥ango' para {usuario.display_name}")
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje de ascenso: {str(e)}")

@bot.command(name="ascenso", description="Asciende a un usuario a un nuevo rango")
async def ascenso_prefix(ctx, usuario: discord.Member, rango: discord.Role, *, motivo: str):
    # Verificar permisos
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ No tienes permisos para gestionar roles")
        return
    
    # Verificar que el bot tenga permisos
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("❌ No tengo permisos para gestionar roles en este servidor")
        return
    
    try:
        # Verificar que el bot puede asignar este rol
        if rango.position >= ctx.guild.me.top_role.position or rango.managed:
            await ctx.send(f"❌ No tengo permisos para asignar el rol '{rango.name}'")
            return
        
        # Verificar si el usuario ya tiene el rol
        if rango in usuario.roles:
            await ctx.send(f"❌ {usuario.mention} ya tiene el rol '{rango.name}'")
            return
        
        # Asignar el rol
        await usuario.add_roles(rango)
        
        # Cambiar la placa si el rol está en el diccionario
        prefijo = PREFIJOS_PLACA.get(rango.name)
        if prefijo:
            # Intentar extraer el número de placa del nickname actual
            numero_placa = "00"
            if usuario.nick:
                match = re.match(r"^[A-Z]{3}-?(\d{1,2})\s*\|", usuario.nick)
                if match:
                    numero_placa = match.group(1)
            nuevo_nickname = f"{prefijo}-{numero_placa} | {usuario.name}"
            if len(nuevo_nickname) > 32:
                nombre_truncado = usuario.name[:32 - len(f"{prefijo}-{numero_placa} | ")]
                nuevo_nickname = f"{prefijo}-{numero_placa} | {nombre_truncado}"
            try:
                await usuario.edit(nick=nuevo_nickname)
            except Exception as e:
                print(f"❌ Error al cambiar la placa: {str(e)}")
        
        # Enviar confirmación al canal donde se ejecutó el comando
        await ctx.send(f"✅ Se ha ascendido a {usuario.mention} al rango **{rango.name}**")
        
        # Enviar mensaje al canal de ascensos
        await enviar_mensaje_ascenso(ctx.guild, usuario, rango, motivo, ctx.author)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para asignar roles")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="descenso", description="Desciende a un usuario a un rango inferior")
@app_commands.describe(
    usuario="Usuario al que descender",
    rango="Rol al que descender al usuario",
    motivo="Motivo del descenso"
)
async def descenso(interaction: discord.Interaction, usuario: discord.Member, rango: discord.Role, motivo: str):
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
        # Verificar que el bot puede asignar este rol
        if rango.position >= interaction.guild.me.top_role.position or rango.managed:
            await interaction.response.send_message(
                f"❌ No tengo permisos para asignar el rol '{rango.name}'",
                ephemeral=True
            )
            return
        
        # Verificar si el usuario ya tiene el rol
        if rango in usuario.roles:
            await interaction.response.send_message(
                f"❌ {usuario.mention} ya tiene el rol '{rango.name}'",
                ephemeral=True
            )
            return
        
        # Asignar el rol
        await usuario.add_roles(rango)
        
        # Enviar confirmación al usuario que ejecutó el comando
        await interaction.response.send_message(
            f"✅ Se ha descendido a {usuario.mention} al rango **{rango.name}**",
            ephemeral=True
        )
        
        # Enviar mensaje al canal de descensos
        await enviar_mensaje_descenso(interaction.guild, usuario, rango, motivo, interaction.user)
        
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

async def enviar_mensaje_descenso(guild, usuario, rango, motivo, autor_comando):
    """Envía el mensaje de descenso al canal '↪📣》𝗦ubir-𝗕ajar-𝗥ango'"""
    try:
        # Buscar el canal "↪📣》𝗦ubir-𝗕ajar-𝗥ango"
        canal_descensos = discord.utils.get(guild.channels, name="↪📣》𝗦ubir-𝗕ajar-𝗥ango")
        
        if not canal_descensos:
            print("⚠️ Canal '↪📣》𝗦ubir-𝗕ajar-𝗥ango' no encontrado")
            return
        
        # Crear embed de descenso
        embed_descenso = discord.Embed(
            title="🙁 Lo sentimos por tu descenso...",
            description=f"**Información acerca de este descenso:**",
            color=discord.Color.red()
        )
        
        # Información del obrero descendido
        embed_descenso.add_field(
            name="👷 Obrero descendido:",
            value=f"{usuario.mention} (`{usuario.name}#{usuario.discriminator}` - ID: `{usuario.id}`)",
            inline=False
        )
        
        # Rango descendido
        embed_descenso.add_field(
            name="📉 Rango descendido:",
            value=f"{rango.mention}",
            inline=False
        )
        
        # Motivo
        embed_descenso.add_field(
            name="💬 Motivo:",
            value=motivo,
            inline=False
        )
        
        # Footer con información adicional
        embed_descenso.set_footer(text=f"Ejecuta: {autor_comando.display_name}")
        embed_descenso.set_thumbnail(url=usuario.display_avatar.url)
        
        # Enviar mensaje al canal de descensos
        await canal_descensos.send(content=f"{usuario.mention}", embed=embed_descenso)
        
        print(f"✅ Mensaje de descenso enviado al canal '↪📣》𝗦ubir-𝗕ajar-𝗥ango' para {usuario.display_name}")
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje de descenso: {str(e)}")

@bot.command(name="descenso", description="Desciende a un usuario a un rango inferior")
async def descenso_prefix(ctx, usuario: discord.Member, rango: discord.Role, *, motivo: str):
    # Verificar permisos
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ No tienes permisos para gestionar roles")
        return
    
    # Verificar que el bot tenga permisos
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("❌ No tengo permisos para gestionar roles en este servidor")
        return
    
    try:
        # Verificar que el bot puede asignar este rol
        if rango.position >= ctx.guild.me.top_role.position or rango.managed:
            await ctx.send(f"❌ No tengo permisos para asignar el rol '{rango.name}'")
            return
        
        # Verificar si el usuario ya tiene el rol
        if rango in usuario.roles:
            await ctx.send(f"❌ {usuario.mention} ya tiene el rol '{rango.name}'")
            return
        
        # Asignar el rol
        await usuario.add_roles(rango)
        
        # Enviar confirmación al canal donde se ejecutó el comando
        await ctx.send(f"✅ Se ha descendido a {usuario.mention} al rango **{rango.name}**")
        
        # Enviar mensaje al canal de descensos
        await enviar_mensaje_descenso(ctx.guild, usuario, rango, motivo, ctx.author)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para asignar roles")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="despido", description="Despide a un usuario y le asigna roles de sanción")
@app_commands.describe(
    usuario="Usuario al que despedir",
    motivo="Motivo del despido"
)
async def despido(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
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
        # Buscar los roles de sanción
        roles_sancion = [
            "═══════Sanciones═══════",
            "❌| Despedido",
            "🎟️〴Civil〴"
        ]
        
        roles_a_asignar = []
        roles_no_encontrados = []
        
        for nombre_rol in roles_sancion:
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
                f"❌ No se encontraron roles de sanción válidos. Roles configurados: {', '.join(roles_sancion)}",
                ephemeral=True
            )
            if roles_no_encontrados:
                await interaction.followup.send(
                    f"⚠️ Roles no encontrados o sin permisos: {', '.join(roles_no_encontrados)}",
                    ephemeral=True
                )
            return
        
        # Quitar todos los roles del usuario (excepto @everyone)
        roles_a_quitar = [rol for rol in usuario.roles if rol.name != "@everyone"]
        if roles_a_quitar:
            await usuario.remove_roles(*roles_a_quitar)
        
        # Asignar roles de sanción
        await usuario.add_roles(*roles_a_asignar)
        
        # Enviar confirmación al usuario que ejecutó el comando
        await interaction.response.send_message(
            f"✅ Se ha despedido a {usuario.mention} y se le han asignado los roles de sanción",
            ephemeral=True
        )
        
        # Enviar mensaje al canal de despidos
        await enviar_mensaje_despido(interaction.guild, usuario, motivo, interaction.user)
        
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ No tengo permisos para gestionar roles",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )

async def enviar_mensaje_despido(guild, usuario, motivo, autor_comando):
    """Envía el mensaje de despido al canal '↪🚫》𝗗espidos'"""
    try:
        # Buscar el canal "↪🚫》𝗗espidos"
        canal_despidos = discord.utils.get(guild.channels, name="↪🚫》𝗗espidos")
        
        if not canal_despidos:
            print("⚠️ Canal '↪🚫》𝗗espidos' no encontrado")
            return
        
        # Crear embed de despido
        embed_despido = discord.Embed(
            title="💔 ¡Lamentamos tu despido!",
            description=f"**Información acerca de este despido:**",
            color=discord.Color.dark_red()
        )
        
        # Información del obrero despedido
        embed_despido.add_field(
            name="👷 Obrero despedido:",
            value=f"{usuario.mention} (`{usuario.name}#{usuario.discriminator}` - ID: `{usuario.id}`)",
            inline=False
        )
        
        # Motivo
        embed_despido.add_field(
            name="💬 Motivo:",
            value=motivo,
            inline=False
        )
        
        # Footer con información adicional
        embed_despido.set_footer(text=f"Ejecuta: {autor_comando.display_name}")
        embed_despido.set_thumbnail(url=usuario.display_avatar.url)
        
        # Enviar mensaje al canal de despidos
        await canal_despidos.send(content=f"{usuario.mention}", embed=embed_despido)
        
        print(f"✅ Mensaje de despido enviado al canal '↪🚫》𝗗espidos' para {usuario.display_name}")
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje de despido: {str(e)}")

@bot.command(name="despido", description="Despide a un usuario y le asigna roles de sanción")
async def despido_prefix(ctx, usuario: discord.Member, *, motivo: str):
    # Verificar permisos
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ No tienes permisos para gestionar roles")
        return
    
    # Verificar que el bot tenga permisos
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("❌ No tengo permisos para gestionar roles en este servidor")
        return
    
    try:
        # Buscar los roles de sanción
        roles_sancion = [
            "═══════Sanciones═══════",
            "❌| Despedido",
            "🎟️〴Civil〴"
        ]
        
        roles_a_asignar = []
        roles_no_encontrados = []
        
        for nombre_rol in roles_sancion:
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
            await ctx.send(f"❌ No se encontraron roles de sanción válidos. Roles configurados: {', '.join(roles_sancion)}")
            if roles_no_encontrados:
                await ctx.send(f"⚠️ Roles no encontrados o sin permisos: {', '.join(roles_no_encontrados)}")
            return
        
        # Quitar todos los roles del usuario (excepto @everyone)
        roles_a_quitar = [rol for rol in usuario.roles if rol.name != "@everyone"]
        if roles_a_quitar:
            await usuario.remove_roles(*roles_a_quitar)
        
        # Asignar roles de sanción
        await usuario.add_roles(*roles_a_asignar)
        
        # Enviar confirmación al canal donde se ejecutó el comando
        await ctx.send(f"✅ Se ha despedido a {usuario.mention} y se le han asignado los roles de sanción")
        
        # Enviar mensaje al canal de despidos
        await enviar_mensaje_despido(ctx.guild, usuario, motivo, ctx.author)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para gestionar roles")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="sancion", description="Aplica una sanción a un usuario")
@app_commands.describe(
    usuario="Usuario al que sancionar",
    rol="Rol de sanción a aplicar",
    strikes="Número de strikes acumulados",
    razon="Razón de la sanción",
    autorizado_por="Persona que autoriza la sanción"
)
async def sancion(interaction: discord.Interaction, usuario: discord.Member, rol: discord.Role, strikes: int, razon: str, autorizado_por: discord.Member):
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
        # Verificar que el bot puede asignar este rol
        if rol.position >= interaction.guild.me.top_role.position or rol.managed:
            await interaction.response.send_message(
                f"❌ No tengo permisos para asignar el rol '{rol.name}'",
                ephemeral=True
            )
            return
        
        # Verificar si el usuario ya tiene el rol
        if rol in usuario.roles:
            await interaction.response.send_message(
                f"❌ {usuario.mention} ya tiene el rol '{rol.name}'",
                ephemeral=True
            )
            return
        
        # Asignar el rol de sanción
        await usuario.add_roles(rol)
        
        # Enviar confirmación al usuario que ejecutó el comando
        await interaction.response.send_message(
            f"✅ Se ha sancionado a {usuario.mention} con el rol **{rol.name}**",
            ephemeral=True
        )
        
        # Enviar mensaje al canal de sanciones
        await enviar_mensaje_sancion(interaction.guild, usuario, rol, strikes, razon, autorizado_por, interaction.user)
        
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

async def enviar_mensaje_sancion(guild, usuario, rol, strikes, razon, autorizado_por, ejecuta):
    """Envía el mensaje de sanción al canal '↪📛》𝗦anciones'"""
    try:
        # Buscar el canal "↪📛》𝗦anciones"
        canal_sanciones = discord.utils.get(guild.channels, name="↪📛》𝗦anciones")
        
        if not canal_sanciones:
            print("⚠️ Canal '↪📛》𝗦anciones' no encontrado")
            return
        
        # Crear embed de sanción
        embed_sancion = discord.Embed(
            title="📛 Sanción Aplicada",
            description=f"**Sanción:** {rol.mention}",
            color=discord.Color.red()
        )
        
        # Empleado sancionado
        embed_sancion.add_field(
            name="👷 Empleado sancionado:",
            value=f"{usuario.mention} (`{usuario.name}#{usuario.discriminator}` - ID: `{usuario.id}`)",
            inline=False
        )
        
        # Acumulación de strikes
        embed_sancion.add_field(
            name="⚠️ Acumulación de strike:",
            value=f"**{strikes}** strikes",
            inline=False
        )
        
        # Razón
        embed_sancion.add_field(
            name="💬 Razón:",
            value=razon,
            inline=False
        )
        
        # Autorizado por
        embed_sancion.add_field(
            name="✅ Autorizado por:",
            value=f"{autorizado_por.mention}",
            inline=False
        )
        
        # Footer con información adicional
        embed_sancion.set_footer(text=f"Ejecuta: {ejecuta.display_name}")
        embed_sancion.set_thumbnail(url=usuario.display_avatar.url)
        
        # Enviar mensaje al canal de sanciones
        await canal_sanciones.send(content=f"{usuario.mention}", embed=embed_sancion)
        
        print(f"✅ Mensaje de sanción enviado al canal '↪📛》𝗦anciones' para {usuario.display_name}")
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje de sanción: {str(e)}")

@bot.command(name="sancion", description="Aplica una sanción a un usuario")
async def sancion_prefix(ctx, usuario: discord.Member, rol: discord.Role, strikes: int, autorizado_por: discord.Member, *, razon: str):
    # Verificar permisos
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ No tienes permisos para gestionar roles")
        return
    
    # Verificar que el bot tenga permisos
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("❌ No tengo permisos para gestionar roles en este servidor")
        return
    
    try:
        # Verificar que el bot puede asignar este rol
        if rol.position >= ctx.guild.me.top_role.position or rol.managed:
            await ctx.send(f"❌ No tengo permisos para asignar el rol '{rol.name}'")
            return
        
        # Verificar si el usuario ya tiene el rol
        if rol in usuario.roles:
            await ctx.send(f"❌ {usuario.mention} ya tiene el rol '{rol.name}'")
            return
        
        # Asignar el rol de sanción
        await usuario.add_roles(rol)
        
        # Enviar confirmación al canal donde se ejecutó el comando
        await ctx.send(f"✅ Se ha sancionado a {usuario.mention} con el rol **{rol.name}**")
        
        # Enviar mensaje al canal de sanciones
        await enviar_mensaje_sancion(ctx.guild, usuario, rol, strikes, razon, autorizado_por, ctx.author)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para asignar roles")
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