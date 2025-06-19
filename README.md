# Bot de Discord para Gestión de Roles

Un bot de Discord desarrollado en Python que permite asignar y gestionar roles de manera fácil y eficiente.

## 🚀 Características

- **Comando `/periodo-de-prueba`**: Asigna roles a usuarios específicos
- **Interfaz interactiva**: Selección de roles mediante botones
- **Gestión completa**: Asignar, quitar y ver roles de usuarios
- **Despliegue en Railway**: Configuración lista para Railway.app
- **Permisos seguros**: Verificación de permisos antes de ejecutar acciones

## 📋 Comandos Disponibles

### `/periodo-de-prueba`
Asigna un rol a un usuario específico.
- **Parámetros**:
  - `usuario`: El usuario al que asignar el rol
  - `rol` (opcional): El rol específico a asignar

### `/quitar-rol`
Quita un rol específico de un usuario.
- **Parámetros**:
  - `usuario`: El usuario del que quitar el rol
  - `rol`: El rol a quitar

### `/roles-usuario`
Muestra todos los roles de un usuario específico.
- **Parámetros**:
  - `usuario`: El usuario cuyos roles quieres ver

## 🛠️ Configuración Local

1. **Clona el repositorio**:
   ```bash
   git clone <tu-repositorio>
   cd sheets
   ```

2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura las variables de entorno**:
   Crea un archivo `.env` con:
   ```
   DISCORD_TOKEN=tu_token_del_bot
   ```

4. **Ejecuta el bot**:
   ```bash
   python main.py
   ```

## 🚀 Despliegue en Railway.app

### Paso 1: Crear el Bot en Discord
1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Crea una nueva aplicación
3. Ve a la sección "Bot" y crea un bot
4. Copia el token del bot
5. En "OAuth2 > URL Generator", selecciona:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Manage Roles`, `Send Messages`, `Use Slash Commands`

### Paso 2: Desplegar en Railway
1. Conecta tu repositorio de GitHub a Railway.app
2. En Railway, agrega la variable de entorno:
   - `DISCORD_TOKEN`: Tu token del bot de Discord
3. Railway detectará automáticamente que es un proyecto Python
4. El bot se desplegará automáticamente

### Paso 3: Invitar el Bot al Servidor
Usa el enlace generado en el paso 1 para invitar el bot a tu servidor.

## 🔧 Permisos Requeridos

El bot necesita los siguientes permisos en el servidor:
- **Gestionar Roles**: Para asignar y quitar roles
- **Enviar Mensajes**: Para responder a comandos
- **Usar Comandos de Barra**: Para los comandos slash

## 📝 Notas Importantes

- El bot solo puede asignar roles que estén por debajo de su propio rol en la jerarquía
- Los usuarios que usen los comandos deben tener permisos de "Gestionar Roles"
- El bot respeta la jerarquía de roles del servidor

## 🐛 Solución de Problemas

### El bot no responde a comandos
- Verifica que el bot tenga los permisos correctos
- Asegúrate de que el token sea válido
- Revisa los logs en Railway

### Error de permisos
- Verifica que el bot tenga el rol "Gestionar Roles"
- Asegúrate de que el rol del bot esté por encima de los roles que intenta asignar

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. 