# Версия для Jupyter Notebook/Google Colab
def find_middle_letters(word):
    """
    Функция для нахождения средней буквы/букв в переменной
    """
    length = len(word)
    
    if length == 0:
        return "Ошибка: переменная не может быть пустой"
    
    middle_index = length // 2
    
    if length % 2 == 0:  # Четное количество букв
        return word[middle_index - 1:middle_index + 1]
    else:  # Нечетное количество букв
        return word[middle_index]

try:
    user_word = input("Введите перменную из латинских букв: ").strip()
    
    if not user_word:
        print("Ошибка: вы не ввели перменную")
    elif not user_word.isalpha():
        print("Ошибка: переменная должна содержать только буквы")
    else:
        result = find_middle_letters(user_word)
        print(f"\nПеременная: '{user_word}'")
        print(f"Результат: {result}")
        
except KeyboardInterrupt:
    print("\nПрограмма прервана пользователем")