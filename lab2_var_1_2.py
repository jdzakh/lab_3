import socket
import json
import struct

# Устанавливаем хост и порт для соединения
host = '127.0.0.1'
port = 12345

# Создаем сокет и устанавливаем соединение с сервером
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

# Основной цикл программы для взаимодействия с сервером
while True:
    command = input("Введите команду (set_root_folder, get_file_info or q): ")
    s.send(command.encode())

    # Обработка команды 'set_root_folder' и 'q'
    if command == 'set_root_folder':
        new_folder = input("Введите новую корневую папку: ")
        s.send(new_folder.encode())
        print(s.recv(2048).decode())

    elif command == 'get_file_info':
        response_length_data = s.recv(4)  # Получаем длину JSON данных от сервера
        response_length = struct.unpack('I', response_length_data)[0]  # Распаковываем данные длины

        response = b""
        while len(response) < response_length:
            data = s.recv(min(4096, response_length - len(response)))
            response += data

        files_info = json.loads(response.decode())
        for file_path, file_info in files_info.items():
            print(file_path, file_info)

    elif command == 'q':
        break

s.close()