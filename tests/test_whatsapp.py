import pytest
import json
import logging
from unittest.mock import MagicMock, patch
import sys
import os

# Añadir el directorio src al path para poder importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from whatsapp import WhatsAppClient

class TestWhatsAppClient:
    """Pruebas unitarias para el módulo WhatsAppClient."""
    
    @pytest.fixture
    def setup_client(self):
        """Configuración inicial para las pruebas."""
        # Configurar logger
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)
        
        # Crear instancia del cliente con valores de prueba
        client = WhatsAppClient(
            api_key="test_api_key",
            phone_number_id="test_phone_id",
            recipient="test_recipient",
            logger=logger
        )
        
        return client
    
    def test_initialization(self, setup_client):
        """Prueba la inicialización correcta del cliente."""
        client = setup_client
        
        assert client.api_key == "test_api_key"
        assert client.phone_number_id == "test_phone_id"
        assert client.recipient == "test_recipient"
        assert client.base_url == "https://graph.facebook.com/v17.0"
        assert client.headers["Authorization"] == "Bearer test_api_key"
        assert client.headers["Content-Type"] == "application/json"
        assert client.temp_dir.exists()
    
    @patch('requests.post')
    def test_send_text_message(self, mock_post, setup_client):
        """Prueba el envío de un mensaje de texto."""
        client = setup_client
        
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "messaging_product": "whatsapp",
            "contacts": [{"wa_id": "test_recipient"}],
            "messages": [{"id": "wamid.123456"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Llamar al método a probar
        result = client.send_text_message("Mensaje de prueba")
        
        # Verificar la llamada a la API
        expected_url = f"{client.base_url}/{client.phone_number_id}/messages"
        expected_payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": client.recipient,
            "type": "text",
            "text": {
                "body": "Mensaje de prueba"
            }
        }
        
        mock_post.assert_called_once_with(
            expected_url, 
            headers=client.headers, 
            json=expected_payload
        )
        
        # Verificar el resultado
        assert result == mock_response.json.return_value
    
    @patch('requests.post')
    def test_send_media_message(self, mock_post, setup_client):
        """Prueba el envío de un mensaje con contenido multimedia."""
        client = setup_client
        
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "messaging_product": "whatsapp",
            "contacts": [{"wa_id": "test_recipient"}],
            "messages": [{"id": "wamid.123457"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Llamar al método a probar
        result = client.send_media_message(
            media_type="image",
            media_url="https://example.com/image.jpg",
            caption="Una imagen de prueba"
        )
        
        # Verificar la llamada a la API
        expected_url = f"{client.base_url}/{client.phone_number_id}/messages"
        expected_payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": client.recipient,
            "type": "image",
            "image": {
                "link": "https://example.com/image.jpg",
                "caption": "Una imagen de prueba"
            }
        }
        
        mock_post.assert_called_once_with(
            expected_url, 
            headers=client.headers, 
            json=expected_payload
        )
        
        # Verificar el resultado
        assert result == mock_response.json.return_value
    
    @patch('requests.post')
    def test_send_message_text(self, mock_post, setup_client):
        """Prueba el envío de un mensaje de texto usando el método genérico."""
        client = setup_client
        
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "messaging_product": "whatsapp",
            "contacts": [{"wa_id": "test_recipient"}],
            "messages": [{"id": "wamid.123458"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Crear datos de mensaje de prueba
        message_data = {
            "message_id": 12345,
            "chat_id": 67890,
            "user_id": 54321,
            "username": "test_user",
            "date": "2025-06-04T10:00:00",
            "text": "Mensaje de prueba",
            "caption": "",
            "type": "text",
            "media_file": None
        }
        
        # Llamar al método a probar
        result = client.send_message(message_data)
        
        # Verificar que se llamó al método correcto
        expected_url = f"{client.base_url}/{client.phone_number_id}/messages"
        expected_payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": client.recipient,
            "type": "text",
            "text": {
                "body": "Mensaje de prueba"
            }
        }
        
        mock_post.assert_called_once_with(
            expected_url, 
            headers=client.headers, 
            json=expected_payload
        )
        
        # Verificar el resultado
        assert result == mock_response.json.return_value
    
    @patch('requests.post')
    def test_send_message_photo(self, mock_post, setup_client):
        """Prueba el envío de un mensaje con foto usando el método genérico."""
        client = setup_client
        
        # Configurar el mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "messaging_product": "whatsapp",
            "contacts": [{"wa_id": "test_recipient"}],
            "messages": [{"id": "wamid.123459"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Crear datos de mensaje de prueba
        message_data = {
            "message_id": 12346,
            "chat_id": 67890,
            "user_id": 54321,
            "username": "test_user",
            "date": "2025-06-04T10:05:00",
            "text": "",
            "caption": "Una foto de prueba",
            "type": "photo",
            "media_file": "file_id_123",
            "media_type": "image/jpeg",
            "file_name": None,
            "file_size": 1024
        }
        
        # Llamar al método a probar
        result = client.send_message(message_data)
        
        # Verificar que se llamó al método correcto
        # En este caso, debería usar una URL simulada para el ejemplo
        assert mock_post.called
        
        # Verificar el resultado
        assert result == mock_response.json.return_value
    
    @patch('requests.post')
    def test_api_request_retry(self, mock_post, setup_client):
        """Prueba el mecanismo de reintento en caso de error en la API."""
        client = setup_client
        
        # Configurar el mock para fallar en el primer intento y tener éxito en el segundo
        mock_post.side_effect = [
            requests.exceptions.RequestException("Error de conexión"),
            MagicMock(
                json=lambda: {"success": True},
                raise_for_status=lambda: None
            )
        ]
        
        # Reducir el tiempo de espera para la prueba
        with patch('time.sleep'):
            # Llamar al método a probar
            result = client._make_api_request(
                url="https://example.com/api",
                payload={"test": "data"},
                max_retries=3
            )
        
        # Verificar que se realizaron dos intentos
        assert mock_post.call_count == 2
        
        # Verificar el resultado
        assert result == {"success": True}
