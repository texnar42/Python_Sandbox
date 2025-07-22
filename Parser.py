import re
from collections import defaultdict
from datetime import datetime
import csv


#import log_data

# Регулярное выражение для разбора строки лога
# LOG_PATTERN = r'(\d+\.\d+\.\d+\.\d+).*?\[(.*?)\] "(GET|POST|PUT|DELETE|HEAD) (.*?) HTTP'
LOG_PATTERN = r'.*?\[(.*?)\] "(GET|POST|PUT|DELETE|HEAD) (.*?) HTTP'
                 #192.168.1.1 - - [15/Jul/2025:10:15:33 +0300] "POST /submit-form HTTP/1.1" 403 98

with open('input.csv', 'r') as log_file:
    logs = log_file.readlines()

parsed_data = []
for log in logs:
    match = re.search(LOG_PATTERN, log)
    if match:
        datetime_str = match.group(1)  # 15/Jul/2025:10:15:30 +0300
        method = match.group(2)  # GET/POST
        url = match.group(3)  # /index.html

        # Разделяем дату и время
        # date, time = datetime_str.split(':')[:2]
        # full_date = f"{date} {time}"  # 15/Jul/2025 10:15:30

        parsed_data.append([datetime_str, method, url])

# Записываем в новый CSV-файл
with open('parsed_logs.csv', 'w', newline='') as output_file:
    writer = csv.writer(output_file)
    writer.writerow(['Date', 'Method', 'URL'])  # Заголовки
    writer.writerows(parsed_data)

print("Парсинг завершен. Результат сохранен в parsed_logs.csv")