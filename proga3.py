from datetime import datetime
import os
import json
import socket


# класс для представления узлов бинарного дерева
class Node:
    def __init__(self, key):
        self.key = key  # значение, хранимое в данном узле.
        self.left = None  # ссылка на левого потомка узла
        self.right = None  # ссылка на правого потомка узла


def insert_node(root, key):  # функция для вставки узла в бинарное дерево
    if root is None:
        return Node(
            key)  # если корень пуст, создается новый узел со значением key, и этот узел становится корнем поддерева
    if key < root.key:
        root.left = insert_node(root.left, key)  # рекурсивно вставляем новый узел в левую ветвь дерева
    else:
        root.right = insert_node(root.right, key)
    return root  # корень поддерева


def inorder_traversal(root, result):  # обход дерева по порядку
    if root:  # если узел существует
        inorder_traversal(root.left, result)  # обходим все узлы левого поддерева перед текущим узлом
        result.append(root.key)  # добавление значения текущего узла в итоговый список
        inorder_traversal(root.right, result)


def create_binary_tree(numbers):  # функция для создания бинарного дерева из списка чисел
    root = None  # пустой корень в начале
    for num in numbers:
        root = insert_node(root, num)  # вставка числа в бинарное дерево
    result = []
    inorder_traversal(root, result)  # построение дерева по списку чисел
    return result


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #создается объект сокета server
server.bind(("127.0.0.1", 12345)) #код связывает сокет с определенным адресом и портом
server.listen(1) #начинает прослушивание входящих подключений
conn, addr = server.accept() #метод ожидает входящее подключение от клиента
print(f"Подключение установлено от {addr}")


while True:
    data = conn.recv(1024).decode() #получение данных

    if data == "send_numbers":
        numbers_string = conn.recv(1024).decode()
        numbers = [int(num) for num in numbers_string.split()]

        current_time = datetime.now()  # получаем текущую дату и время
        folder_name = current_time.strftime("%d-%m-%Y_%H-%M-%S")  # форматируем название папки

        os.makedirs(folder_name)  # создаем новую папку с текущим временем

        root = None  # для начала нового бинарного дерева
        for i, num in enumerate(numbers, 1):
            root = insert_node(root, num)  # на каждой итерации вставляем новый узел с ключом num в текущее бинарное дерево, начиная с корня root
            result = []
            inorder_traversal(root, result)  # построение дерева по списку чисел

            file_name = f"{i}.json"
            with open(os.path.join(folder_name, file_name), "w") as file:
                json.dump(result, file)  # сохраняем файл в формате json

        response = json.dumps(result) #преобразует результат в формат json
        conn.send(response.encode()) #используется для отправки этих байтов через сетевое соединение


    elif data == "request_file":
        launch_number = conn.recv(1024).decode()
        tree_number = conn.recv(1024).decode()

        file_name = f"{tree_number}.json" #создает имя файла, используя значение tree_number и расширение файла .json
        file_path = os.path.join(folder_name, file_name) #создает полный путь к файлу

        with open(file_path, "r") as file: #открывает файл по указанному пути для чтения
            data = file.read()
            conn.send(data.encode()) #отправляет содержимое файла обратно клиенту


conn.close() #закрывает сокет, представляющий установленное сетевое соединение
server.close() #закрывает сокет сервера
