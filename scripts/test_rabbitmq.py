#!/usr/bin/env python
"""Тест RabbitMQ подключения"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.movies.src.infrastructure.message_bus.event_bus import EventBus
import time
import logging

logging.basicConfig(level=logging.INFO)

def test_publish():
    """Тест публикации"""
    bus = EventBus()
    
    # Создаём exchange
    bus.declare_exchange('test.exchange', 'fanout')
    
    # Публикуем сообщение
    bus.publish(
        exchange_name='test.exchange',
        routing_key='',
        event={'message': 'Hello RabbitMQ!', 'count': 1}
    )
    
    print("✅ Message published")
    bus.close()

def test_consume():
    """Тест потребления"""
    bus = EventBus()
    
    # Создаём очередь
    queue = bus.declare_queue('test.queue')
    
    # Привязываем к exchange
    bus.bind_queue('test.queue', 'test.exchange', '')
    
    def callback(event_data):
        print(f"📨 Received: {event_data}")
    
    # Начинаем слушать (в отдельном потоке)
    import threading
    consumer_thread = threading.Thread(
        target=lambda: bus.consume('test.queue', callback)
    )
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Даём время на подключение
    time.sleep(1)
    
    # Публикуем ещё одно сообщение
    test_publish()
    
    # Ждём обработки
    time.sleep(2)
    bus.close()

if __name__ == '__main__':
    print="🔌 Testing RabbitMQ..."
    test_publish()
    test_consume()
