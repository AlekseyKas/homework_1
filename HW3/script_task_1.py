purchases = {}

try:
    with open('purchase_log.txt', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:  # Проверяем, что строка не пустая
                # Ищем первый пробел для разделения ключа и значения
                space_index = line.find(' ')
                if space_index != -1:
                    key = line[:space_index]
                    value = line[space_index+1:]
                    purchases[key] = value
except FileNotFoundError:
    print("Файл purchase_log.txt не найден")
    exit()

# Вывод первых двух элементов
print("Первые два элемента словаря purchases:")
for i, (key, value) in enumerate(purchases.items()):
    if i < 2:
        print(f"{key} '{value}'")
    else:
        break