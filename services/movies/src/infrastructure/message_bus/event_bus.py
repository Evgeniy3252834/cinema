"""Event Bus для работы с RabbitMQ"""
import json
import pika
import logging
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class EventBus:
    """Шина событий на RabbitMQ"""
    
    def __init__(self, host='localhost', port=5672, user='admin', password='admin'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Подключение к RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("✅ Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise
    
    def declare_exchange(self, exchange_name: str, exchange_type: str = 'topic'):
        """Объявить exchange"""
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True  # exchange сохраняется после перезапуска
        )
        logger.info(f"✅ Exchange declared: {exchange_name} ({exchange_type})")
    
    def declare_queue(self, queue_name: str, durable: bool = True):
        """Объявить очередь"""
        self.channel.queue_declare(queue=queue_name, durable=durable)
        logger.info(f"✅ Queue declared: {queue_name}")
        return queue_name
    
    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str):
        """Привязать очередь к exchange"""
        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        logger.info(f"✅ Queue {queue_name} bound to {exchange_name} with key {routing_key}")
    
    def publish(self, exchange_name: str, routing_key: str, event: Any):
        """Опубликовать событие"""
        try:
            # Конвертируем событие в JSON
            if hasattr(event, '__dict__'):
                event_data = event.__dict__
            else:
                event_data = event
            
            # Добавляем метаданные
            if isinstance(event_data, dict):
                event_data['_timestamp'] = datetime.now().isoformat()
                event_data['_event_type'] = event.__class__.__name__
            
            message = json.dumps(event_data, default=str)
            
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent message
                    content_type='application/json'
                )
            )
            logger.info(f"✅ Event published: {routing_key}")
        except Exception as e:
            logger.error(f"❌ Failed to publish event: {e}")
            raise
    
    def consume(self, queue_name: str, callback: Callable):
        """Начать потребление сообщений из очереди"""
        def wrapped_callback(ch, method, properties, body):
            try:
                # Парсим сообщение
                event_data = json.loads(body)
                logger.info(f"📨 Received event: {method.routing_key}")
                
                # Вызываем пользовательский callback
                callback(event_data)
                
                # Подтверждаем обработку
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.debug(f"✅ Message acknowledged")
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
                # Отклоняем и не переотправляем
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.channel.basic_qos(prefetch_count=1)  # Fair dispatch
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapped_callback
        )
        logger.info(f"👂 Started consuming from queue: {queue_name}")
    
    def start_consuming(self):
        """Запустить цикл потребления (блокирующий)"""
        logger.info("🔄 Starting consuming loop...")
        self.channel.start_consuming()
    
    def close(self):
        """Закрыть соединение"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("🔌 Connection to RabbitMQ closed")
