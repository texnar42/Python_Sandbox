import paramiko

# Настройки подключения

# list
#
# host = "localhost"
# hosts = [
#     'host1.example.com',
#     'host2.example.com',
#     '192.168.1.100'
# ]
# port = 2222
# username = "root"
# password = "password"  # Или используйте ключи SSH
# directory = "/etc/hosts"
#
# # Команда или скрипт для выполнения
# command = "df -h " + directory + "| awk 'NR==2 {print ""$5""}'"
#
# # Создаём SSH-клиент
# client = paramiko.SSHClient()
# client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#
# try:
#     # Подключаемся
#     client.connect(host, port, username, password)
#
#     # Выполняем команду
#     stdin, stdout, stderr = client.exec_command(command)
#
#     # Читаем вывод
#     print("STDOUT:", stdout.read().decode())
#     print("STDERR:", stderr.read().decode())
#
#
#     output_str = stdout.read().decode("utf-8") # .strip() убирает лишние пробелы/переносы
#
#
# finally:
#     client.close()




# hosts = [
#     'localhost'
# ]
# port = [
#     2222
# ]
host = "localhost"
port = 2222
username = "root"
password = "password"  # Или используйте ключи SSH
directory = "/etc/hosts"

def check_disk_space(host, port, username, password, command="df -h " + directory + "| awk 'NR==2 {print ""$5""}'"):
    try:
        # Создаем SSH-клиент
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Подключаемся к хосту
        client.connect(hostname=host, port=port, username=username, password=password)

        # Выполняем команду
        stdin, stdout, stderr = client.exec_command(command)

        # Читаем вывод
        output = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            print(f"Ошибка на хосте {host}: {error}")
        else:
            print(f"Результат для хоста {host}:\n{output}")

    except Exception as e:
        print(f"Не удалось подключиться к {host}: {str(e)}")
    finally:
        client.close()


# Проверяем каждый хост
for host in host:
    check_disk_space(host, port, username, password)

# else: print("Не Соответсвует")