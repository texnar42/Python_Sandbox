import paramiko

# Настройки подключения
host = "host.docker.internal"
port = 22
username = "root"
password = "password"  # Или используйте ключи SSH

# Команда или скрипт для выполнения
command = "ls -l"

# Создаём SSH-клиент
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Подключаемся
    client.connect(host, port, username, password)

    # Выполняем команду
    stdin, stdout, stderr = client.exec_command(command)

    # Читаем вывод
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())

finally:
    client.close()