#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo principal para el Telegram-WhatsApp Bridge.
Este es el punto de entrada del programa que inicia el monitoreo
de mensajes de Telegram y su reenvío a WhatsApp.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

# Importaciones locales
from telegram import TelegramClient
from whatsapp import WhatsAppClient
from message_handler import MessageHandler

# Configuración de logging
def setup_logging(config):
    """Configura el sistema de logging según las especificaciones del archivo de configuración."""
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_file = log_config.get("file", "logs/bridge.log")
    max_size = log_config.get("max_size_mb", 10) * 1024 * 1024
    backup_count = log_config.get("backup_count", 5)
    
    # Asegurarse de que el directorio de logs exista
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configurado correctamente")
    return logger

def load_config():
    """Carga la configuración desde el archivo config.json."""
    config_path = Path(__file__).parent.parent / "config" / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Archivo de configuración no encontrado en {config_path}")
        print("Por favor, copia config.example.json a config.json y configúralo con tus credenciales.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: El archivo de configuración {config_path} no es un JSON válido.")
        sys.exit(1)

def main():
    """Función principal que inicia el bridge entre Telegram y WhatsApp."""
    # Cargar configuración
    config = load_config()
    
    # Configurar logging
    logger = setup_logging(config)
    logger.info("Iniciando Telegram-WhatsApp Bridge")
    
    try:
        # Inicializar clientes
        telegram_client = TelegramClient(
            token=config["telegram"]["token"],
            channel_id=config["telegram"]["channel_id"],
            logger=logger
        )
        
        whatsapp_client = WhatsAppClient(
            api_key=config["whatsapp"]["api_key"],
            phone_number_id=config["whatsapp"]["phone_number_id"],
            recipient=config["whatsapp"]["recipient"],
            logger=logger
        )
        
        # Inicializar manejador de mensajes
        message_handler = MessageHandler(
            telegram_client=telegram_client,
            whatsapp_client=whatsapp_client,
            filters=config.get("filters", {}),
            logger=logger
        )
        
        # Iniciar el monitoreo
        logger.info("Iniciando monitoreo de mensajes")
        telegram_client.start_polling(message_handler.process_message)
        
        # Mantener el programa en ejecución
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Programa detenido por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        # Implementar lógica de reconexión según configuración
        reconnection_config = config.get("reconnection", {})
        max_retries = reconnection_config.get("max_retries", 5)
        retry_delay = reconnection_config.get("retry_delay_seconds", 30)
        
        for attempt in range(max_retries):
            logger.info(f"Intentando reconexión ({attempt+1}/{max_retries}) en {retry_delay} segundos...")
            time.sleep(retry_delay)
            try:
                # Reintentar conexión
                main()
                break
            except Exception as e:
                logger.error(f"Reintento fallido: {e}", exc_info=True)
        
        logger.critical("Se agotaron los intentos de reconexión. Saliendo...")
    finally:
        # Limpieza
        logger.info("Cerrando conexiones...")
        if 'telegram_client' in locals():
            telegram_client.stop()
        logger.info("Programa finalizado")

if __name__ == "__main__":
    main()
