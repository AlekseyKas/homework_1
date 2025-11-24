def sum_distance(from_num, to_num):
    # Если первое число больше второго, меняем их местами
    if from_num > to_num:
        from_num, to_num = to_num, from_num
    
    # Суммируем все числа в диапазоне
    total = 0
    for i in range(from_num, to_num + 1):
        total += i
    
    return total

# Альтернативное решение с использованием встроенной функции sum()
def sum_distance_alt(from_num, to_num):
    # Если первое число больше второго, меняем их местами
    if from_num > to_num:
        from_num, to_num = to_num, from_num
    
    # Используем функцию sum() для суммирования диапазона
    return sum(range(from_num, to_num + 1))

# Тестирование функций
if __name__ == "__main__":
    # Примеры использования
    print(sum_distance(1, 5))      # 1+2+3+4+5 = 15
    print(sum_distance(5, 1))      # тоже 15 (числа поменяются местами)
    print(sum_distance(-3, 2))     # -3 + -2 + -1 + 0 + 1 + 2 = -3
    print(sum_distance(10, 10))    # 10
    
    print("\nАльтернативная функция:")
    print(sum_distance_alt(1, 5))  # 15
    print(sum_distance_alt(5, 1))  # 15