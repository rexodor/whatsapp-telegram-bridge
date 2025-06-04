#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para interactuar con la API de Telegram.
Gestiona la conexión con Telegram, la escucha de mensajes
y el procesamiento de eventos del bot.
"""

import logging
from typing import Callable, Dict, Any, Optional, List
import time

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

class TelegramClient:
    """Cliente para interactuar con la API de Telegram."""
    
    def __init__(self, token: str, channel_id: str, logger: Optional[logging.Logger] = None):
        """
        Inicializa el cliente de Telegram.
        
        Args:
            token: Token del bot de Telegram.
            channel_id: ID del canal a monitorear.
            logger: Logger para registrar eventos.
        """
        self.token = token
        self.channel_id = channel_id
        self.logger = logger or logging.getLogger(__name__)
        self.application = None
        self.is_running = False
        self.message_callback = None
        
    def start_polling(self, message_callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Inicia el monitoreo de mensajes en el canal especificado.
        
        Args:
            message_callback: Función a llamar cuando se recibe un mensaje.
        """
        self.message_callback = message_callback
        self.logger.info(f"Iniciando monitoreo del canal {self.channel_id}")
        
        # Configurar la aplicación
        self.application = Application.builder().token(self.token).build()
        
        # Registrar manejadores
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("stop", self._stop_command))
        self.application.add_handler(CommandHandler("status", self._status_command))
        self.application.add_handler(MessageHandler(filters.CHAT & ~filters.COMMAND, self._message_handler))
        
        # Iniciar el polling
        self.is_running = True
        self.application.run_polling()
        
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja el comando /start."""
        self.logger.info("Comando /start recibido")
        self.is_running = True
        await update.message.reply_text("Bridge iniciado. Los mensajes serán reenviados a WhatsApp.")
        
    async def _stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja el comando /stop."""
        self.logger.info("Comando /stop recibido")
        self.is_running = False
        await update.message.reply_text("Bridge detenido. Los mensajes no serán reenviados.")
        
    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja el comando /status."""
        status = "activo" if self.is_running else "inactivo"
        self.logger.info(f"Comando /status recibido. Estado actual: {status}")
        await update.message.reply_text(f"Estado del bridge: {status}")
        
    async def _message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Procesa los mensajes recibidos."""
        if not self.is_running:
            self.logger.debug("Mensaje recibido pero el bridge está inactivo")
            return
            
        if str(update.effective_chat.id) != self.channel_id:
            self.logger.debug(f"Mensaje recibido de un chat no monitoreado: {update.effective_chat.id}")
            return
            
        try:
            # Extraer información del mensaje
            message_data = self._extract_message_data(update)
            
            # Llamar al callback con los datos del mensaje
            if self.message_callback:
                self.message_callback(message_data)
                
        except Exception as e:
            self.logger.error(f"Error al procesar mensaje de Telegram: {e}", exc_info=True)
            
    def _extract_message_data(self, update: Update) -> Dict[str, Any]:
        """
        Extrae los datos relevantes de un mensaje de Telegram.
        
        Args:
            update: Objeto Update de Telegram.
            
        Returns:
            Diccionario con los datos del mensaje.
        """
        message = update.effective_message
        
        # Datos básicos del mensaje
        message_data = {
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "user_id": update.effective_user.id if update.effective_user else None,
            "username": update.effective_user.username if update.effective_user else None,
            "date": message.date,
            "text": message.text or "",
            "caption": message.caption or "",
            "type": "text",
            "media_file": None,
            "media_type": None,
            "file_name": None,
            "file_size": None,
        }
        
        # Determinar el tipo de mensaje y extraer datos adicionales
        if message.photo:
            message_data["type"] = "photo"
            message_data["media_file"] = message.photo[-1].file_id
            message_data["media_type"] = "image/jpeg"
            message_data["file_size"] = message.photo[-1].file_size
            
        elif message.video:
            message_data["type"] = "video"
            message_data["media_file"] = message.video.file_id
            message_data["media_type"] = "video/mp4"
            message_data["file_name"] = message.video.file_name
            message_data["file_size"] = message.video.file_size
            
        elif message.document:
            message_data["type"] = "document"
            message_data["media_file"] = message.document.file_id
            message_data["media_type"] = message.document.mime_type
            message_data["file_name"] = message.document.file_name
            message_data["file_size"] = message.document.file_size
            
        elif message.audio:
            message_data["type"] = "audio"
            message_data["media_file"] = message.audio.file_id
            message_data["media_type"] = message.audio.mime_type
            message_data["file_name"] = message.audio.file_name
            message_data["file_size"] = message.audio.file_size
            
        elif message.voice:
            message_data["type"] = "voice"
            message_data["media_file"] = message.voice.file_id
            message_data["media_type"] = "audio/ogg"
            message_data["file_size"] = message.voice.file_size
            
        elif message.sticker:
            message_data["type"] = "sticker"
            message_data["media_file"] = message.sticker.file_id
            message_data["media_type"] = "image/webp"
            message_data["file_size"] = message.sticker.file_size
            
        self.logger.debug(f"Mensaje procesado: tipo={message_data['type']}, usuario={message_data['username']}")
        return message_data
        
    async def download_file(self, file_id: str) -> str:
        """
        Descarga un archivo de Telegram.
        
        Args:
            file_id: ID del archivo a descargar.
            
        Returns:
            Ruta local del archivo descargado.
        """
        try:
            self.logger.debug(f"Descargando archivo con ID: {file_id}")
            # Implementar lógica de descarga usando la API de Telegram
            # Este es un placeholder, la implementación real dependerá de la biblioteca
            return f"/tmp/telegram_file_{file_id}"
        except Exception as e:
            self.logger.error(f"Error al descargar archivo de Telegram: {e}", exc_info=True)
            raise
            
    def stop(self) -> None:
        """Detiene el cliente de Telegram."""
        self.logger.info("Deteniendo cliente de Telegram")
        self.is_running = False
        if self.application:
            self.application.stop()
