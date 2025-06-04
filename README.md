# Telegram-WhatsApp Bridge

Un proyecto que permite conectar WhatsApp y Telegram, reenviando automáticamente mensajes de un canal de Telegram a un canal de WhatsApp.

## Descripción

Este proyecto proporciona una solución para sincronizar mensajes entre plataformas de mensajería, específicamente de Telegram a WhatsApp. Monitorea un canal de Telegram en tiempo real y reenvía automáticamente los mensajes detectados a un canal de WhatsApp especificado.

## Características

- Monitoreo en tiempo real de canales de Telegram
- Reenvío automático de mensajes a WhatsApp
- Soporte para mensajes de texto y multimedia (imágenes, videos, documentos, etc.)
- Filtrado de mensajes configurable
- Sistema de logging para seguimiento de actividades
- Manejo de errores y reconexión automática

## Requisitos previos

- Python 3.8 o superior
- Token de Bot de Telegram (obtenido a través de [BotFather](https://t.me/botfather))
- Cuenta de WhatsApp Business API
- Acceso a Internet

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/yourusername/telegram-whatsapp-bridge.git
   cd telegram-whatsapp-bridge
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Copia el archivo de configuración de ejemplo y edítalo con tus credenciales:
   ```
   cp config/config.example.json config/config.json
   ```

## Configuración

Edita el archivo `config/config.json` con la siguiente información:

- `telegram_token`: Tu token de bot de Telegram
- `telegram_channel_id`: ID del canal de Telegram a monitorear
- `whatsapp_api_key`: Tu clave de API de WhatsApp Business
- `whatsapp_phone_number_id`: ID del número de teléfono de WhatsApp
- `whatsapp_recipient`: Número de teléfono o ID del canal de WhatsApp donde se enviarán los mensajes
- `filters`: Configuración de filtros para los mensajes (palabras clave a ignorar o incluir)

## Uso

Para iniciar el bridge:

```
python src/main.py
```

El programa comenzará a monitorear el canal de Telegram especificado y reenviará automáticamente los mensajes al canal de WhatsApp configurado.

### Comandos disponibles (en el bot de Telegram)

- `/start`: Inicia el reenvío de mensajes
- `/stop`: Detiene el reenvío de mensajes
- `/status`: Muestra el estado actual del bridge

## Despliegue

Para mantener el bridge funcionando continuamente, puedes desplegarlo en un servidor:

### Usando systemd (Linux)

1. Crea un archivo de servicio:
   ```
   sudo nano /etc/systemd/system/telegram-whatsapp-bridge.service
   ```

2. Añade el siguiente contenido (ajusta las rutas según tu configuración):
   ```
   [Unit]
   Description=Telegram WhatsApp Bridge
   After=network.target

   [Service]
   User=yourusername
   WorkingDirectory=/path/to/telegram-whatsapp-bridge
   ExecStart=/usr/bin/python3 /path/to/telegram-whatsapp-bridge/src/main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Habilita e inicia el servicio:
   ```
   sudo systemctl enable telegram-whatsapp-bridge
   sudo systemctl start telegram-whatsapp-bridge
   ```

### Usando Docker

Un Dockerfile está incluido en el repositorio. Para construir y ejecutar:

```
docker build -t telegram-whatsapp-bridge .
docker run -d --name telegram-whatsapp-bridge telegram-whatsapp-bridge
```

## Estructura del proyecto

```
/telegram-whatsapp-bridge
├── /src                # Código fuente
│   ├── telegram.py     # Lógica para interactuar con Telegram
│   ├── whatsapp.py     # Lógica para interactuar con WhatsApp
│   ├── message_handler.py  # Lógica para procesar y reenviar mensajes
│   └── main.py         # Punto de entrada del programa
├── /config             # Archivos de configuración
│   ├── config.json
│   └── config.example.json
├── /logs               # Carpeta para almacenar logs
├── /tests              # Pruebas unitarias
├── requirements.txt    # Dependencias del proyecto
├── README.md           # Documentación del proyecto
├── CONTRIBUTING.md     # Guía de contribución
└── LICENSE             # Licencia del proyecto (MIT)
```

## Contribuir

Las contribuciones son bienvenidas. Por favor, lee [CONTRIBUTING.md](CONTRIBUTING.md) para obtener detalles sobre nuestro código de conducta y el proceso para enviarnos pull requests.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Limitaciones conocidas

- La API de WhatsApp Business tiene límites de tasa que pueden afectar el reenvío de mensajes en volúmenes altos.
- Algunos tipos de contenido multimedia pueden no ser compatibles entre plataformas.
- El bot de Telegram debe ser administrador del canal para monitorear todos los mensajes.

## Solución de problemas

Consulta los archivos de registro en la carpeta `/logs` para obtener información detallada sobre cualquier error.

Problemas comunes:
- **Error de autenticación**: Verifica que tus tokens y credenciales sean correctos.
- **Mensajes no enviados**: Comprueba los límites de tasa de la API de WhatsApp.
- **Bot no responde**: Asegúrate de que el bot tenga los permisos adecuados en el canal de Telegram.

## Contacto

Si tienes preguntas o sugerencias, por favor abre un issue en este repositorio.

