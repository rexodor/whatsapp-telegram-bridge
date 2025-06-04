import pytest
import json
import logging
from unittest.mock import MagicMock, patch
import sys
import os

# Añadir el directorio src al path para poder importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from telegram import TelegramClient

class TestTelegramClient:
    """Pruebas unitarias para el módulo TelegramClient."""
    
    @pytest.fixture
    def setup_client(self):
        """Configuración inicial para las pruebas."""
        # Configurar logger
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)
        
        # Crear instancia del cliente con valores de prueba
        client = TelegramClient(
            token="test_token",
            channel_id="test_channel_id",
            logger=logger
        )
        
        # Mockear la aplicación de Telegram
        client.application = MagicMock()
        
        return client
    
    def test_initialization(self, setup_client):
        """Prueba la inicialización correcta del cliente."""
        client = setup_client
        
        assert client.token == "test_token"
        assert client.channel_id == "test_channel_id"
        assert client.is_running is False
        assert client.message_callback is None
    
    @patch('telegram.ext.Application.builder')
    def test_start_polling(self, mock_builder, setup_client):
        """Prueba el inicio del polling."""
        client = setup_client
        
        # Configurar el mock
        mock_app = MagicMock()
        mock_builder.return_value.token.return_value.build.return_value = mock_app
        
        # Crear un callback de prueba
        callback = MagicMock()
        
        # Llamar al método a probar
        with patch.object(client, 'application', mock_app):
            client.start_polling(callback)
        
        # Verificar que se configuró correctamente
        assert client.message_callback == callback
        assert client.is_running is True
        mock_app.run_polling.assert_called_once()
    
    def test_extract_message_data_text(self, setup_client):
        """Prueba la extracción de datos de un mensaje de texto."""
        client = setup_client
        
        # Crear un mock de Update con un mensaje de texto
        update = MagicMock()
        update.effective_message.message_id = 12345
        update.effective_chat.id = 67890
        update.effective_user.id = 54321
        update.effective_user.username = "test_user"
        update.effective_message.date = "2025-06-04T10:00:00"
        update.effective_message.text = "Mensaje de prueba"
        update.effective_message.caption = None
        update.effective_message.photo = []
        update.effective_message.video = None
        update.effective_message.document = None
        update.effective_message.audio = None
        update.effective_message.voice = None
        update.effective_message.sticker = None
        
        # Extraer datos del mensaje
        message_data = client._extract_message_data(update)
        
        # Verificar los datos extraídos
        assert message_data["message_id"] == 12345
        assert message_data["chat_id"] == 67890
        assert message_data["user_id"] == 54321
        assert message_data["username"] == "test_user"
        assert message_data["date"] == "2025-06-04T10:00:00"
        assert message_data["text"] == "Mensaje de prueba"
        assert message_data["type"] == "text"
    
    def test_extract_message_data_photo(self, setup_client):
        """Prueba la extracción de datos de un mensaje con foto."""
        client = setup_client
        
        # Crear un mock de Update con un mensaje con foto
        update = MagicMock()
        update.effective_message.message_id = 12346
        update.effective_chat.id = 67890
        update.effective_user.id = 54321
        update.effective_user.username = "test_user"
        update.effective_message.date = "2025-06-04T10:05:00"
        update.effective_message.text = None
        update.effective_message.caption = "Una foto de prueba"
        
        # Configurar la foto
        photo1 = MagicMock()
        photo1.file_id = "small_photo_id"
        photo1.file_size = 1024
        
        photo2 = MagicMock()
        photo2.file_id = "large_photo_id"
        photo2.file_size = 2048
        
        update.effective_message.photo = [photo1, photo2]
        update.effective_message.video = None
        update.effective_message.document = None
        update.effective_message.audio = None
        update.effective_message.voice = None
        update.effective_message.sticker = None
        
        # Extraer datos del mensaje
        message_data = client._extract_message_data(update)
        
        # Verificar los datos extraídos
        assert message_data["message_id"] == 12346
        assert message_data["chat_id"] == 67890
        assert message_data["user_id"] == 54321
        assert message_data["username"] == "test_user"
        assert message_data["caption"] == "Una foto de prueba"
        assert message_data["type"] == "photo"
        assert message_data["media_file"] == "large_photo_id"  # Debe usar la foto más grande
        assert message_data["media_type"] == "image/jpeg"
        assert message_data["file_size"] == 2048
    
    def test_stop(self, setup_client):
        """Prueba la detención del cliente."""
        client = setup_client
        client.is_running = True
        
        # Detener el cliente
        client.stop()
        
        # Verificar que se detuvo correctamente
        assert client.is_running is False
        client.application.stop.assert_called_once()
