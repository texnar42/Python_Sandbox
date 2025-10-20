# from pymongo import MongoClient
# from pymongo.errors import PyMongoError
# from pymongo import MongoClient
# from prometheus_client import start_http_server, Gauge
# import time
# import configparser
# import os
#
# class MongoDBConfigExporter:
# def get_runtime_config(parameters,
#                        uri="mongodb://admin:password@localhost:27017/",
#                        auth_mechanism="SCRAM-SHA-256",
#                        auth_source="admin"):
#     """
#     Получает runtime-параметры из MongoDB
#
#     :param parameters: список параметров для получения (минимум 5)
#     :param uri: строка подключения MongoDB (по умолчанию локальный сервер)
#     :param auth_mechanism: механизм аутентификации
#     :param auth_source: источник аутентификации
#     :return: словарь с запрошенными параметрами или None при ошибке
#     """
#     # Проверяем минимальное количество параметров
#     if len(parameters) < 5:
#         raise ValueError("Function requires at least 5 parameters to fetch")
#
#     try:
#         # Формируем полный URI с параметрами аутентификации
#         full_uri = f"{uri}?authMechanism={auth_mechanism}&authSource={auth_source}"
#
#         # Создаем клиент с таймаутом подключения 3 секунды
#         with MongoClient(full_uri, serverSelectionTimeoutMS=3000) as client:
#             # Проверяем подключение
#             client.admin.command('ping')
#
#             # Формируем команду getParameter
#             command = {'getParameter': 1}
#             for param in parameters:
#                 command[param] = 1
#
#             # Выполняем команду
#             result = client.admin.command(command)
#
#             # Извлекаем только запрошенные параметры
#             return {param: result.get(param) for param in parameters}
#
#     except PyMongoError as e:
#         print(f"MongoDB connection error: {e}")
#         return None
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         return None
#
#
# # Пример использования
# if __name__ == "__main__":
#     exporter = MongoDBConfigExporter()
#     start_http_server(8000)
#     print("Exporter running on port 8000")
#     exporter.update_metrics()
#     # Список параметров для получения (минимум 5)
#     params_to_fetch = [
#         "wiredTigerFileHandleCloseMinimum",
#         "wiredTigerEngineRuntimeConfig",
#         "tcpFastOpenServer",
#         "logLevel",
#         "maxConns",
#         "oplogMinRetentionHours",  # Можно добавлять больше
#         "replWriterThreadCount"
#     ]
#
#     # Получаем параметры
#     config = get_runtime_config(params_to_fetch)
#
#     if config:
#         print("Runtime configuration parameters:")
#         for param, value in config.items():
#             print(f"{param}: {value}")
#     else:
#         print("Failed to retrieve configuration")