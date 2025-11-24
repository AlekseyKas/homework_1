def trim_and_repeat(string, offset=0, repetitions=1):
    # Обрезаем строку слева на offset символов
    trimmed_string = string[offset:]
    
    # Повторяем строку указанное количество раз
    result = trimmed_string * repetitions
    
    return result

# Альтернативная реализация с более компактным кодом
def trim_and_repeat_alt(string, offset=0, repetitions=1):
    return string[offset:] * repetitions

# Тестирование функции
if __name__ == "__main__":
    # Примеры использования
    print(trim_and_repeat("hello world", 2, 3))     # "llo worldllo worldllo world"
    print(trim_and_repeat("python", 0, 2))          # "pythonpython"
    print(trim_and_repeat("programming", 3))        # "gramming" (repetitions=1 по умолчанию)
    print(trim_and_repeat("test"))                  # "test" (offset=0, repetitions=1 по умолчанию)
    print(trim_and_repeat("example", 10, 2))        # "" (пустая строка, так как offset больше длины строки)
    
    # Тестирование альтернативной версии
    print("\nАльтернативная функция:")
    print(trim_and_repeat_alt("hello", 1, 2))       # "elloello"