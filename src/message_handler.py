#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para procesar y reenviar mensajes entre Telegram y WhatsApp.
Gestiona el filtrado de mensajes y la lógica de reenvío.
"""

import logging
import re
import time
from typing import Dict, Any, List, Optional, Callable, Set

class MessageHandler:
    """Manejador para procesar y reenviar mensajes entre plataformas."""
    
    def __init__(self, telegram_client, whatsapp_client, filters: Dict[str, Any] = None, 
                 logger: Optional[logging.Logger] = None):
        """
        Inicializa el manejador de mensajes.
        
        Args:
            telegram_client: Cliente de Telegram.
            whatsapp_client: Cliente de WhatsApp.
            filters: Configuración de filtros para los mensajes.
            logger: Logger para registrar eventos.
        """
        self.telegram_client = telegram_client
        self.whatsapp_client = whatsapp_client
        self.filters = filters or {}
        self.logger = logger or logging.getLogger(__name__)
        self.processed_messages = set()  # Para evitar duplicados
        
    def process_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Procesa un mensaje recibido de Telegram y lo reenvía a WhatsApp si pasa los filtros.
        
        Args:
            message_data: Datos del mensaje a procesar.
            
        Returns:
            True si el mensaje fue procesado y reenviado, False en caso contrario.
        """
        message_id = message_data.get("message_id")
        
        # Evitar procesar mensajes duplicados
        if message_id in self.processed_messages:
            self.logger.debug(f"Mensaje {message_id} ya procesado, ignorando")
            return False
            
        self.processed_messages.add(message_id)
        
        # Limitar el tamaño del conjunto para evitar consumo excesivo de memoria
        if len(self.processed_messages) > 1000:
            self.processed_messages = set(list(self.processed_messages)[-1000:])
            
        # Aplicar filtros
        if not self._apply_filters(message_data):
            self.logger.info(f"Mensaje {message_id} filtrado, no se reenviará")
            return False
            
        try:
            # Reenviar mensaje a WhatsApp
            self.logger.info(f"Reenviando mensaje {message_id} a WhatsApp")
            response = self.whatsapp_client.send_message(message_data)
            
            self.logger.debug(f"Mensaje reenviado con éxito: {response}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al reenviar mensaje {message_id}: {e}", exc_info=True)
            return False
            
    def _apply_filters(self, message_data: Dict[str, Any]) -> bool:
        """
        Aplica filtros configurados al mensaje.
        
        Args:
            message_data: Datos del mensaje a filtrar.
            
        Returns:
            True si el mensaje pasa todos los filtros, False en caso contrario.
        """
        # Si no hay filtros configurados, permitir todos los mensajes
        if not self.filters:
            return True
            
        # Filtrar por tipo de mensaje
        allowed_types = self.filters.get("only_forward_media_types", [])
        if allowed_types and message_data.get("type") not in allowed_types:
            self.logger.debug(f"Mensaje filtrado por tipo: {message_data.get('type')}")
            return False
            
        # Filtrar por usuario
        ignored_users = self.filters.get("ignore_users", [])
        username = message_data.get("username", "")
        user_id = message_data.get("user_id", "")
        
        if username and username in ignored_users:
            self.logger.debug(f"Mensaje filtrado por usuario ignorado: {username}")
            return False
            
        if str(user_id) in ignored_users:
            self.logger.debug(f"Mensaje filtrado por ID de usuario ignorado: {user_id}")
            return False
            
        # Filtrar por palabras clave a ignorar
        ignore_keywords = self.filters.get("ignore_keywords", [])
        text = (message_data.get("text", "") + " " + message_data.get("caption", "")).lower()
        
        for keyword in ignore_keywords:
            if keyword.lower() in text:
                self.logger.debug(f"Mensaje filtrado por palabra clave ignorada: {keyword}")
                return False
                
        # Filtrar por palabras clave a incluir (si la lista no está vacía)
        include_keywords = self.filters.get("only_include_keywords", [])
        if include_keywords:
            for keyword in include_keywords:
                if keyword.lower() in text:
                    return True
                    
            self.logger.debug("Mensaje filtrado por no contener palabras clave requeridas")
            return False
            
        # Si pasa todos los filtros
        return True
        
    def format_message(self, message_data: Dict[str, Any]) -> str:
        """
        Formatea un mensaje para su reenvío.
        
        Args:
            message_data: Datos del mensaje a formatear.
            
        Returns:
            Mensaje formateado.
        """
        message_type = message_data.get("type", "text")
        text = message_data.get("text", "")
        caption = message_data.get("caption", "")
        username = message_data.get("username", "")
        
        # Formatear el mensaje según el tipo
        if message_type == "text":
            if username:
                return f"*{username}*: {text}"
            return text
            
        else:
            # Para mensajes multimedia
            if text and caption:
                content = f"{text}\n\n{caption}"
            else:
                content = text or caption or f"[{message_type}]"
                
            if username:
                return f"*{username}*: {content}"
            return content
