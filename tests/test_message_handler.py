import pytest
import json
import logging
from unittest.mock import MagicMock, patch
import sys
import os

# Añadir el directorio src al path para poder importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from message_handler import MessageHandler

class TestMessageHandler:
    """Pruebas unitarias para el módulo MessageHandler."""
    
    @pytest.fixture
    def setup_handler(self):
        """Configuración inicial para las pruebas."""
        # Crear mocks para los clientes
        telegram_client = MagicMock()
        whatsapp_client = MagicMock()
        
        # Configuración de filtros para pruebas
        filters = {
            "ignore_keywords": ["spam", "publicidad"],
            "ignore_users": ["user1", "bot123"],
            "only_include_keywords": [],
            "only_forward_media_types": ["text", "photo", "video", "document"]
        }
        
        # Configurar logger
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)
        
        # Crear instancia del manejador
        handler = MessageHandler(
            telegram_client=telegram_client,
            whatsapp_client=whatsapp_client,
            filters=filters,
            logger=logger
        )
        
        return handler, telegram_client, whatsapp_client
    
    def test_process_message_text(self, setup_handler):
        """Prueba el procesamiento de un mensaje de texto simple."""
        handler, _, whatsapp_client = setup_handler
        
        # Crear mensaje de prueba
        message = {
            "message_id": 12345,
            "chat_id": 67890,
            "user_id": 54321,
            "username": "test_user",
            "date": "2025-06-04T10:00:00",
            "text": "Hola, este es un mensaje de prueba",
            "caption": "",
            "type": "text",
            "media_file": None
        }
        
        # Configurar el mock para simular una respuesta exitosa
        whatsapp_client.send_message.return_value = {"success": True, "message_id": "wamid.123456"}
        
        # Procesar el mensaje
        result = handler.process_message(message)
        
        # Verificar que el mensaje fue procesado correctamente
        assert result is True
        whatsapp_client.send_message.assert_called_once_with(message)
    
    def test_filter_ignored_keywords(self, setup_handler):
        """Prueba que los mensajes con palabras clave ignoradas sean filtrados."""
        handler, _, whatsapp_client = setup_handler
        
        # Crear mensaje con palabra clave ignorada
        message = {
            "message_id": 12346,
            "chat_id": 67890,
            "user_id": 54321,
            "username": "test_user",
            "date": "2025-06-04T10:05:00",
            "text": "Este mensaje contiene spam y debería ser filtrado",
            "caption": "",
            "type": "text",
            "media_file": None
        }
        
        # Procesar el mensaje
        result = handler.process_message(message)
        
        # Verificar que el mensaje fue filtrado
        assert result is False
        whatsapp_client.send_message.assert_not_called()
    
    def test_filter_ignored_users(self, setup_handler):
        """Prueba que los mensajes de usuarios ignorados sean filtrados."""
        handler, _, whatsapp_client = setup_handler
        
        # Crear mensaje de usuario ignorado
        message = {
            "message_id": 12347,
            "chat_id": 67890,
            "user_id": 54321,
            "username": "user1",  # Usuario en la lista de ignorados
            "date": "2025-06-04T10:10:00",
            "text": "Este mensaje debería ser filtrado por el usuario",
            "caption": "",
            "type": "text",
            "media_file": None
        }
        
        # Procesar el mensaje
        result = handler.process_message(message)
        
        # Verificar que el mensaje fue filtrado
        assert result is False
        whatsapp_client.send_message.assert_not_called()
    
    def test_process_media_message(self, setup_handler):
        """Prueba el procesamiento de un mensaje con contenido multimedia."""
        handler, _, whatsapp_client = setup_handler
        
        # Crear mensaje multimedia de prueba
        message = {
            "message_id": 12348,
            "chat_id": 67890,
            "user_id": 54321,
            "username": "test_user",
            "date": "2025-06-04T10:15:00",
            "text": "",
            "caption": "Una imagen de prueba",
            "type": "photo",
            "media_file": "file_id_123",
            "media_type": "image/jpeg",
            "file_name": None,
            "file_size": 1024
        }
        
        # Configurar el mock para simular una respuesta exitosa
        whatsapp_client.send_message.return_value = {"success": True, "message_id": "wamid.123457"}
        
        # Procesar el mensaje
        result = handler.process_message(message)
        
        # Verificar que el mensaje fue procesado correctamente
        assert result is True
        whatsapp_client.send_message.assert_called_once_with(message)
    
    def test_duplicate_message_handling(self, setup_handler):
        """Prueba que los mensajes duplicados sean ignorados."""
        handler, _, whatsapp_client = setup_handler
        
        # Crear mensaje de prueba
        message = {
            "message_id": 12349,
            "chat_id": 67890,
            "user_id": 54321,
            "username": "test_user",
            "date": "2025-06-04T10:20:00",
            "text": "Este mensaje se enviará una sola vez",
            "caption": "",
            "type": "text",
            "media_file": None
        }
        
        # Configurar el mock para simular una respuesta exitosa
        whatsapp_client.send_message.return_value = {"success": True, "message_id": "wamid.123458"}
        
        # Procesar el mensaje por primera vez
        result1 = handler.process_message(message)
        
        # Procesar el mismo mensaje por segunda vez
        result2 = handler.process_message(message)
        
        # Verificar que el mensaje fue procesado correctamente la primera vez
        assert result1 is True
        
        # Verificar que el mensaje fue ignorado la segunda vez
        assert result2 is False
        
        # Verificar que send_message fue llamado solo una vez
        assert whatsapp_client.send_message.call_count == 1
