from pymongo import MongoClient
from prometheus_client import start_http_server, Gauge
import time
import configparser
import os


class MongoDBConfigExporter:
    def __init__(self):
        # Создаем метрику для параметров конфигурации
        self.config_parameters = Gauge(
            'mongodb_config_parameter',
            'MongoDB configuration parameters',
            ['section', 'key', 'source']
        )
        self.config_parameter1 = Gauge(
            'mongodb_config_parameter1',
            'MongoDB configuration parameters',
            ['section', 'key', 'source']
        )

    def get_runtime_config(self):
        """Получаем runtime-параметры из MongoDB"""
        try:
            client = MongoClient("mongodb://admin:password@localhost:27017/?authMechanism=SCRAM-SHA-256&authSource=admin")
            # Получаем параметр через getParameter
            result = client.admin.command(
                {
                    'getParameter': 1,
                    'notablescan': 1, # // Запрет table scan
                    'replWriterThreadCount': 1, #
                    'enableLocalhostAuthBypass': 1, #
                    'balancerStopped': 1,#
                    'journalCommitInterval': 1, #
                    'wiredTigerConcurrentReadTransactions': 1, #
                    'wiredTigerConcurrentWriteTransactions': 1, #
                    'cursorTimeoutMillis': 1, #
                    'transactionLifetimeLimitSeconds': 1 #
                # 'getParameter': 1,
                # 'wiredTigerFileHandleCloseMinimum': 1
            })
            return result.get('wiredTigerFileHandleCloseMinimum', None)

        except Exception as e:
            print(f"Runtime config error: {e}")
            return None
    # 'notablescan': 1, # // Запрет table scan
    # 'replWriterThreadCount': 1, #
    # 'enableLocalhostAuthBypass': 1, #
    # 'balancerStopped': 1,#
    # 'journalCommitInterval': 1, #
    # 'wiredTigerConcurrentReadTransactions': 1, #
    # 'wiredTigerConcurrentWriteTransactions': 1, #
    # 'cursorTimeoutMillis': 1, #
    # 'transactionLifetimeLimitSeconds': 1 #

    # def get_file_config(self, config_path="/etc/mongod.conf"):
    #     """Читаем параметр из конфиг-файла"""
    #     try:
    #         if not os.path.exists(config_path):
    #             return None
    #
    #         config = configparser.ConfigParser()
    #         config.read(config_path)
    #
    #         # Параметр находится в секции [wiredTiger]
    #         if 'wiredTiger' in config:
    #             return config['wiredTiger'].get('fileHandleCloseMinimum', None)
    #
    #         if 'wiredTiger' in config:
    #             return config['wiredTiger'].get('fileHandleCloseMinimum', None)
    #
    #         if 'wiredTiger' in config:
    #             return config['wiredTiger'].get('fileHandleCloseMinimum', None)
    #
    #         if 'wiredTiger' in config:
    #             return config['wiredTiger'].get('fileHandleCloseMinimum', None)
    #
    #         return None
    #     except Exception as e:
    #         print(f"File config error: {e}")
    #         return None

    def update_metrics(self):
        """Обновляем метрики"""
        while True:
            # Runtime значение (из работающего сервера)
            runtime_value = self.get_runtime_config()
            if runtime_value is not None:
                self.config_parameters1.labels(
                    section='notables',
                    key='scan',
                    source='runtime'
                ).set(runtime_value)
                self.config_parameter.labels(
                    section='wiredTiger',
                    key='fileHandleCloseMinimum',
                    source='runtime'
                ).set(runtime_value)

            # Значение из конфиг-файла
            # file_value = self.get_file_config()
            # if file_value is not None:
            #     # Преобразуем строку в число
            #     try:
            #         file_value = int(file_value)
            #         self.config_parameters.labels(
            #             section='wiredTiger',
            #             key='fileHandleCloseMinimum',
            #             source='configFile'
            #         ).set(file_value)
            #     except ValueError:
            #         print("Invalid config value")

            time.sleep(30)


if __name__ == '__main__':
    exporter = MongoDBConfigExporter()
    start_http_server(8000)
    print("Exporter running on port 8000")
    exporter.update_metrics()