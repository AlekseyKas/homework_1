def match_couples(boys, girls):
    # Проверяем, что количество юношей и девушек одинаковое
    if len(boys) != len(girls):
        return "Внимание, кто-то может остаться без пары!"
    
    # Сортируем оба списка по алфавиту
    boys_sorted = sorted(boys)
    girls_sorted = sorted(girls)
    
    # Формируем идеальные пары
    result = "Идеальные пары:\n"
    pairs = []
    
    for i in range(len(boys_sorted)):
        pair = f"{boys_sorted[i]} и {girls_sorted[i]}"
        pairs.append(pair)
    
    result += "\n".join(pairs)
    return result

# Примеры использования
boys1 = ['Peter', 'Alex', 'John', 'Arthur', 'Richard']
girls1 = ['Kate', 'Liza', 'Kira', 'Emma', 'Trisha']

boys2 = ['Peter', 'Alex', 'John', 'Arthur', 'Richard', 'Michael']
girls2 = ['Kate', 'Liza', 'Kira', 'Emma', 'Trisha']

# Тестируем первый пример
print("Пример 1:")
print(match_couples(boys1, girls1))
print("\nПример 2:")
print(match_couples(boys2, girls2))