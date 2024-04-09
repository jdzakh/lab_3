import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("127.0.0.1", 12345))
print("Соединение установлено с программой 1.")

while True:
    action = input("Введите команду ('построение бинарного дерева', 'запросить файл' или 'выход'): ")

    if action == 'построение бинарного дерева':
        server.send("send_numbers".encode()) #программа отправляет на сервер сообщение "send_numbers", предварительно закодированное в байты для передачи по сети
        numbers_input = input("Введите числа для построения бинарного дерева (разделите пробелом): ")
        server.send(numbers_input.encode()) #веденные числа отправляются на сервер

        response = server.recv(1024).decode() #ожидается ответ от сервера, ответ размером до 1024 байт декодируется его в строку
        print("Результат обхода бинарного дерева:", response)

    elif action == 'запросить файл':
        server.send("request_file".encode())
        launch_number = input("Введите номер запуска программы: ")
        tree_number = input("Введите номер дерева: ")

        server.send(launch_number.encode())
        server.send(tree_number.encode())

        file_data = server.recv(1024).decode()
        print("Содержимое запрошенного файла:")
        print(file_data)


    elif action == 'выход':
        break  #выходим из цикла

server.close()