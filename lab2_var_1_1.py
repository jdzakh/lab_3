import os
import json
import socket
import struct

# Установка хоста и порта для соединения
host = '127.0.0.1'
port = 12345

# Создание сокета и привязка к хосту и порту
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1) #указывает на максимальное количество ожидающих соединений (В данном случае 1 указывает на то, что сервер будет принимать\
# только одно соединение за раз.)

# Принятие подключения
conn, addr = s.accept()

# Определение функции, которая возвращает информацию о файле или директории
def get_file_info(path):
    if os.path.isfile(path):  # Проверяем, является ли путь файлом
        file_info = {  # Создаем словарь с информацией о файле
            'name': os.path.basename(path),  # Получаем имя файла
            'size': os.path.getsize(path),  # Получаем размер файла
            'modified': os.path.getmtime(path)  # Получаем время последнего изменения
        }
        return file_info
    elif os.path.isdir(path):  # Если путь является директорией
        dir_info = {  # Создаем словарь с информацией о директории
            'name': os.path.basename(path),  # Получаем имя директории
            'type': 'directory',
            'contents': []  # Создаем пустой список для содержимого директории
        }
        for filename in os.listdir(path):  # Итерируем по содержимому директории
            file_path = os.path.join(path, filename)  # Получаем полный путь к файлу
            file_info = get_file_info(file_path)  # Рекурсивно вызываем функцию для файла внутри директории
            dir_info['contents'].append(file_info)  # Добавляем информацию о файле в содержимое директории
        return dir_info

# Функция для сохранения информации о файлах и папках в формате JSON
def save_to_json(file_info, output_dir):
    with open(os.path.join(output_dir, 'files_info.json'), 'w', encoding='utf-8') as file:
        json.dump(file_info, file, indent=4, ensure_ascii=False)

# Получение информации о текущей директории, сохранение в переменные
current_path = os.getcwd()
output_dir = current_path
files_info = get_file_info(current_path)
save_to_json(files_info, output_dir)

# Основной цикл программы для обработки команд от клиента
while True:
    try:
        command = conn.recv(2048).decode()  # Получаем команду от клиента
    except ConnectionResetError:
        print("Соединение с клиентом разорвано.")
        break

    if command == 'set_root_folder':
        # Установка новой корневой директории
        new_folder = conn.recv(2048).decode()
        if os.path.exists(new_folder): # Проверяем существование папки
            os.chdir(new_folder)  #Меняем рабочую директорию
            output_dir = new_folder
            files_info = get_file_info(new_folder)
            save_to_json(files_info, output_dir)
            conn.send(f"Корневая папка установлена на {new_folder}".encode()) # Отправляем ответ клиенту
        else:
            conn.send("Ошибка: Папка не существует.".encode()) # Отправляем ошибку клиенту

    # Отправка JSON-содержимого информации о файлах и папках клиенту
    # Получение JSON данных о файлах и директориях от клиента
    elif command == 'get_file_info':
        with open(os.path.join(output_dir, 'files_info.json'), 'r', encoding='utf-8') as file:
            files_info = json.load(file)
            json_data = json.dumps(files_info, ensure_ascii=False)
            json_data_bytes = json_data.encode()  # Преобразуем JSON данные в байты
            json_data_length = len(json_data_bytes)

            # Отправляем длину JSON данных клиенту
            conn.send(struct.pack('I', json_data_length))

            # Отправляем JSON данные клиенту фрагментами
            sent = 0
            while sent < json_data_length:
                remaining = json_data_length - sent
                send_size = min(4096, remaining)
                sent += conn.send(json_data_bytes[sent:sent + send_size])

    # Обработка команды 'q'
    elif command == 'q':
        break # Выходим из цикла

conn.close() # Закрываем соединение