#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para interactuar con la API de WhatsApp Business.
Gestiona la conexión con WhatsApp y el envío de mensajes.
"""

import logging
import requests
import json
import os
import time
from typing import Dict, Any, Optional, Union, List
from pathlib import Path

class WhatsAppClient:
    """Cliente para interactuar con la API de WhatsApp Business."""
    
    def __init__(self, api_key: str, phone_number_id: str, recipient: str, 
                 logger: Optional[logging.Logger] = None):
        """
        Inicializa el cliente de WhatsApp.
        
        Args:
            api_key: Clave de API de WhatsApp Business.
            phone_number_id: ID del número de teléfono de WhatsApp.
            recipient: Número de teléfono o ID del destinatario.
            logger: Logger para registrar eventos.
        """
        self.api_key = api_key
        self.phone_number_id = phone_number_id
        self.recipient = recipient
        self.logger = logger or logging.getLogger(__name__)
        self.base_url = "https://graph.facebook.com/v17.0"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.temp_dir = Path("/tmp/whatsapp_media")
        self.temp_dir.mkdir(exist_ok=True)
        
    def send_text_message(self, text: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto a través de WhatsApp.
        
        Args:
            text: Contenido del mensaje.
            
        Returns:
            Respuesta de la API.
        """
        self.logger.info(f"Enviando mensaje de texto a {self.recipient}")
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.recipient,
            "type": "text",
            "text": {
                "body": text
            }
        }
        
        return self._make_api_request(url, payload)
        
    def send_media_message(self, media_type: str, media_url: str, 
                          caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Envía un mensaje con contenido multimedia a través de WhatsApp.
        
        Args:
            media_type: Tipo de medio (image, video, audio, document).
            media_url: URL del archivo multimedia.
            caption: Texto opcional para acompañar el medio.
            
        Returns:
            Respuesta de la API.
        """
        self.logger.info(f"Enviando mensaje multimedia ({media_type}) a {self.recipient}")
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.recipient,
            "type": media_type,
            media_type: {
                "link": media_url
            }
        }
        
        # Añadir caption si está presente
        if caption and media_type in ["image", "video", "document"]:
            payload[media_type]["caption"] = caption
            
        return self._make_api_request(url, payload)
        
    def upload_media(self, file_path: str) -> str:
        """
        Sube un archivo multimedia a los servidores de WhatsApp.
        
        Args:
            file_path: Ruta local del archivo a subir.
            
        Returns:
            URL del archivo subido.
        """
        self.logger.info(f"Subiendo archivo multimedia: {file_path}")
        
        # Esta es una implementación simulada
        # En un entorno real, se utilizaría la API de WhatsApp para subir el archivo
        
        # Simular una URL de archivo subido
        file_name = os.path.basename(file_path)
        mock_url = f"https://example.com/media/{file_name}"
        
        self.logger.debug(f"Archivo subido con éxito. URL: {mock_url}")
        return mock_url
        
    def _make_api_request(self, url: str, payload: Dict[str, Any], 
                         max_retries: int = 3) -> Dict[str, Any]:
        """
        Realiza una solicitud a la API de WhatsApp con reintentos.
        
        Args:
            url: URL de la API.
            payload: Datos a enviar.
            max_retries: Número máximo de reintentos.
            
        Returns:
            Respuesta de la API.
        """
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                self.logger.debug(f"Respuesta de la API: {result}")
                return result
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                self.logger.warning(
                    f"Error en solicitud a la API (intento {retry_count}/{max_retries}): {e}"
                )
                
                if retry_count >= max_retries:
                    self.logger.error("Se agotaron los reintentos para la solicitud a la API")
                    raise
                    
                # Esperar antes de reintentar (backoff exponencial)
                wait_time = 2 ** retry_count
                self.logger.info(f"Esperando {wait_time} segundos antes de reintentar...")
                time.sleep(wait_time)
                
    def send_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía un mensaje a WhatsApp basado en los datos proporcionados.
        
        Args:
            message_data: Datos del mensaje a enviar.
            
        Returns:
            Respuesta de la API.
        """
        message_type = message_data.get("type", "text")
        text = message_data.get("text", "")
        caption = message_data.get("caption", "")
        
        # Combinar texto y caption si ambos están presentes
        if text and caption:
            full_text = f"{text}\n\n{caption}"
        else:
            full_text = text or caption
            
        if message_type == "text":
            return self.send_text_message(full_text)
            
        elif message_type in ["photo", "video", "audio", "document", "voice", "sticker"]:
            # Mapear tipos de Telegram a tipos de WhatsApp
            whatsapp_type_map = {
                "photo": "image",
                "video": "video",
                "audio": "audio",
                "document": "document",
                "voice": "audio",
                "sticker": "image"
            }
            
            whatsapp_type = whatsapp_type_map.get(message_type, "document")
            
            # En un caso real, aquí se descargaría el archivo de Telegram
            # y se subiría a WhatsApp. Para este ejemplo, usamos una URL simulada.
            media_file = message_data.get("media_file")
            if not media_file:
                self.logger.warning(f"No se encontró archivo multimedia para mensaje tipo {message_type}")
                return self.send_text_message(full_text)
                
            # URL simulada para el ejemplo
            media_url = f"https://example.com/media/{media_file}"
            
            return self.send_media_message(whatsapp_type, media_url, full_text)
            
        else:
            self.logger.warning(f"Tipo de mensaje no soportado: {message_type}")
            return self.send_text_message(full_text)
