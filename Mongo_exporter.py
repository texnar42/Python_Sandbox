#!/usr/bin/env python3
"""
MongoDB Live Config Exporter - получает текущую конфигурацию MongoDB через административные команды
"""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import Gauge, generate_latest, REGISTRY
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


class MongoDBConfigMetrics:
    def __init__(self, host, port, username, password, auth_db='admin'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth_db = auth_db
        self.metrics = {}
        self.connection_status = Gauge('mongodb_config_connection_status', 'MongoDB connection status')
        self.config_version = Gauge('mongodb_config_version', 'MongoDB version')
        #self.
        self.config_parameters = Gauge(
            'mongodb_config_parameter',
            'MongoDB configuration parameter',
            ['section', 'key', 'source']
        )

    def connect(self):
        """Устанавливает соединение с MongoDB"""
        try:
            #conn_str = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.auth_db}"
            conn_str = f"mongodb://admin:password@localhost:27017/?authMechanism=SCRAM-SHA-256&authSource=admin"
            self.client = MongoClient(conn_str, serverSelectionTimeoutMS=5000)
            self.client.server_info()  # Проверка соединения
            self.connection_status.set(1)
            return True
        except (ConnectionFailure, OperationFailure) as e:
            print(f"Connection failed: {e}")
            self.connection_status.set(0)
            return False

    def get_config(self):
        """Получает конфигурацию MongoDB"""
        if not hasattr(self, 'client') or not self.connect():
            return None

        try:
            admin_db = self.client['admin']

            # Получаем версию сервера
            build_info = admin_db.command('buildInfo')
            self.config_version.set(float(build_info['version'].split('.')[0]))

            # Получаем текущую конфигурацию
            config = {
                'settings': admin_db.command({
                'getParameter': 1,
                'wiredTigerFileHandleCloseMinimum': 1
            }),
                'status': admin_db.command('serverStatus'),
                #'sharding': admin_db.command('getShardingConfig')
            }

            return config
        except OperationFailure as e:
            print(f"Error retrieving config: {e}")
            return None

    def collect_metrics(self):
        """Собирает метрики из текущей конфигурации MongoDB"""
        config = self.get_config()
        if not config:
            return

        # Обрабатываем основные настройки
        self.process_settings(config.get('settings', {}))

        # Обрабатываем статус сервера
        self.process_status(config.get('status', {}))

        # Обрабатываем шардинг
        self.process_sharding(config.get('sharding', {}))

    def process_settings(self, settings):
        """Обрабатывает параметры настроек"""
        for key, value in settings.items():
            if isinstance(value, (int, float, bool)):
                numeric_value = 1 if value is True else 0 if value is False else value
                self.config_parameters.labels(
                    section='settings',
                    key=key,
                    source='runtime'
                ).set(numeric_value)



    def process_status(self, status):
        """Обрабатывает статус сервера"""
        # Сборка информации
        build_info = status.get('buildInfo', {})
        self.config_parameters.labels(
            section='build',
            key='version',
            source='runtime'
        ).set(float(build_info.get('version', '0.0').split('.')[0]))

        # Настройки хранилища
        storage = status.get('storageEngine', {})
        self.config_parameters.labels(
            section='storage',
            key='engine',
            source='runtime'
        ).set(1 if storage.get('name') else 0)

        # Настройки репликации
        repl = status.get('repl', {})
        self.config_parameters.labels(
            section='replication',
            key='enabled',
            source='runtime'
        ).set(1 if repl else 0)

        wiredTiger = status.get('wiredTigerFileHandleCloseMinimum', {})
        print(wiredTiger)
        self.config_parameters.labels(
            section='wiredTiger',
            key='fileHandleCloseMinimum',
            source='runtime'

        ).set(wiredTiger)



    def process_sharding(self, sharding):
        """Обрабатывает конфигурацию шардинга"""
        self.config_parameters.labels(
            section='sharding',
            key='enabled',
            source='runtime'
        ).set(1 if sharding.get('configsvrConnectionString') else 0)

        # Параметры кластера
        cluster_id = sharding.get('clusterId', {})
        self.config_parameters.labels(
            section='sharding',
            key='cluster_id',
            source='runtime'
        ).set(1 if cluster_id else 0)


class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, metrics_collector, *args, **kwargs):
        self.metrics_collector = metrics_collector
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/metrics':
            try:
                self.metrics_collector.collect_metrics()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(generate_latest(REGISTRY))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        elif self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")


def main():
    parser = argparse.ArgumentParser(
        description='MongoDB Live Config Exporter for Prometheus'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='MongoDB host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=27017,
        help='MongoDB port (default: 27017)'
    )
    parser.add_argument(
        '--username',
        help='MongoDB username'
    )
    parser.add_argument(
        '--password',
        type=str,
        default="password",
        help='MongoDB password'
    )
    parser.add_argument(
        '--auth-db',
        default='admin',
        help='Authentication database (default: admin)'
    )
    parser.add_argument(
        '--web-port',
        type=int,
        default=8000,
        help='Exporter port (default: 8000)'
    )

    args = parser.parse_args()

    print(f"Starting MongoDB Live Config Exporter on port {args.web_port}")
    print(f"Connecting to MongoDB: {args.host}:{args.port}")

    # Инициализируем сборщик метрик
    metrics_collector = MongoDBConfigMetrics(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        auth_db=args.auth_db
    )

    # Проверяем подключение
    if metrics_collector.connect():
        print("Successfully connected to MongoDB")
    else:
        print("Warning: Initial connection failed. Metrics may be unavailable")

    # Создаем кастомный обработчик
    handler = lambda *args: MetricsHandler(metrics_collector, *args)

    # Запускаем сервер
    server = HTTPServer(('', args.web_port), handler)
    print(f"Exporter running at http://localhost:{args.web_port}/metrics")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down exporter")
        server.server_close()


if __name__ == '__main__':
    main()