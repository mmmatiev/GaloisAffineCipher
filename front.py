import Affine

from GF import (
    poly_add, poly_multiply, polynomial_to_string,
    find_random_irreducible_polynomial, is_irreducible,
    generate_field_elements, get_degree, find_generators,
    element_order, is_prime
)

RUSSIAN_ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'  # 32 символа
ENGLISH_ALPHABET = 'abcdefghijklmnopqrstuvwxyzA'  # 27 символов


# --- Функция для отображения главного меню ---
def display_menu():
    """Отображает главное меню программы."""
    print("\nМеню:")
    print("1. Построить поле Галуа F_{p^n}")
    print("2. Выполнить арифметическую операцию над элементами поля")
    print("3. Исследовать мультипликативную группу F_{p^n}^*")
    print("4. Работа с аффинным шифром")
    print("5. Выход")


def input_polynomial_element(elements, p, n):
    """
    Позволяет пользователю выбрать элемент поля Галуа по номеру.
    """
    while True:
        try:
            poly_num = int(input("Введите номер многочлена:\n").strip())
            if not (1 <= poly_num <= len(elements)):
                print(f"Неверный номер. Введите число от 1 до {len(elements)}.")
                continue
            return list(elements[poly_num - 1])
        except ValueError:
            print("Неверный ввод. Введите целое число.")


# Функция для нахождения p и n для заданного размера алфавита
def find_p_n(size):
    """Найдите наименьшее простое число p и целое число n, такое, что p^n >= size."""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
              43, 47, 53, 59, 61, 67]
    for p in primes:
        n = 1
        while p ** n < size:
            n += 1
        if p ** n >= size:
            return p, n
    raise ValueError("Не удалось найти подходящие p и n для заданного размера алфавита.")


# Функция установки ключа
def set_affine_key(alphabet, elements, p, n, modulus, multiplicative_group):
    """
    Устанавливает ключ (α, β) в глобальных переменных модуля
    Affine.
    """
    # 1. Сформировать список ненулевых (F_{p^n}^*)
    nonzero_elements = [elem for elem in elements if any(c != 0 for c in elem)]
    print("\nВыберите α (ненулевой элемент из F_{p^n}^*) из списка:")
    for idx, e in enumerate(nonzero_elements, 1):
        print(f"{idx}. {polynomial_to_string(e)}")

    while True:
        try:
            alpha_choice = int(input("Введите номер элемента для α: ").strip())
            if not (1 <= alpha_choice <= len(nonzero_elements)):
                print("Неверный номер. Повторите ввод.")
                continue
            chosen_alpha = nonzero_elements[alpha_choice - 1]
            print(f"Выбрано α:\n{polynomial_to_string(chosen_alpha)}")
            break
        except ValueError:
            print("Ошибка ввода. Нужно ввести целое число.")

    # 2. Ищем обратный (α⁻¹)
    try:
        alpha_inv = Affine.compute_inverse_affine(
            tuple(chosen_alpha),
            multiplicative_group,  # список ненулевых
            modulus, p, n
        )
        print(f"Найден α⁻¹: {polynomial_to_string(alpha_inv)}")
    except ValueError as e:
        print(f"Ошибка: {e}")
        return

    # 3. Выбираем β из всех элементов
    print("\nВыберите β (любой элемент из F_{p^n}):")
    for idx, e in enumerate(elements, 1):
        print(f"{idx}. {polynomial_to_string(e)}")

    while True:
        try:
            beta_choice = int(input("Введите номер элемента для β: ").strip())
            if not (1 <= beta_choice <= len(elements)):
                print("Неверный номер. Повторите ввод.")
                continue
            chosen_beta = elements[beta_choice - 1]
            print(f"Выбрано β:\n{polynomial_to_string(chosen_beta)}")
            break
        except ValueError:
            print("Ошибка ввода. Нужно ввести целое число.")

    # 4. Сохраняем всё в модуле Affine
    Affine.alpha_affine = tuple(chosen_alpha)
    Affine.alpha_inv_affine = tuple(alpha_inv)
    Affine.beta_affine = tuple(chosen_beta)
    print("\nКлюч успешно установлен:")
    print(f" α = {polynomial_to_string(Affine.alpha_affine)}")
    print(f" β = {polynomial_to_string(Affine.beta_affine)}")
    print(f" α⁻¹ =\n{polynomial_to_string(Affine.alpha_inv_affine)}")


# Основная функция работы с аффинным шифром
def affine_cipher_menu():
    """Отображает подменю аффинного шифра и обрабатывает выбор пользователя."""

    print("\n--- Работа с аффинным шифром ---")

    # Построение поля Галуа для аффинного шифра
    print("\n--- Построение поля Галуа F_{p^n} для аффинного шифра ---")

    # Выбор алфавита
    print("\nВыберите алфавит для аффинного шифра:")
    print("1. Русский")
    print("2. Английский")
    print("3. Произвольный")

    while True:
        alphabet_choice = input("Введите номер опции (1-3): ").strip()
        if alphabet_choice not in ['1', '2', '3']:
            print("Неверный выбор. Пожалуйста, выберите 1, 2 или\n3.\n")
            continue
        break

    if alphabet_choice == '1':
        # Русский
        alphabet = RUSSIAN_ALPHABET
        p = 2
        n = 5
        print("\nВыбрано: Русский алфавит")
        print(f"Алфавит: {alphabet}")
        print(f"Используется поле F_{p}^{n}")

    elif alphabet_choice == '2':
        # Английский
        alphabet = ENGLISH_ALPHABET
        p = 3
        n = 3
        print("\nВыбрано: Английский алфавит")
        print(f"Алфавит: {alphabet}")
        print(f"Используется поле F_{p}^{n}")

    else:
        # Произвольный
        print("\n--- Ввод произвольного алфавита ---")
        while True:
            custom_alphabet = input("Введите алфавит\n(последовательность уникальных символов): ").strip()
            if len(custom_alphabet) == 0:
                print("Алфавит не может быть пустым. Попробуйте\nснова.\n")
                continue
            if len(set(custom_alphabet)) != len(custom_alphabet):
                print("Алфавит должен содержать уникальные символы. Попробуйте\nснова.\n")
                continue
            break
        alphabet = custom_alphabet
        print(f"Используемый алфавит: {alphabet}")

        # Определение p и n
        size = len(alphabet)
        try:
            p, n = find_p_n(size)
            print(f"\nОпределены параметры поля: p={p}, n={n} (F_{p}^{n})")
        except ValueError as ve:
            print(f"Ошибка: {ve}")
            return  # Возврат в подменю

        # Корректировка алфавита
        if p ** n > size:
            # Расширение алфавита
            needed = p ** n - size
            filler = [chr(i) for i in range(32, 127) if chr(i) not in custom_alphabet]
            if len(filler) < needed:
                print("Недостаточно символов для расширения\nалфавита.")
                return
            alphabet = custom_alphabet + ''.join(filler[:needed])
            print(f"Алфавит расширен до {p ** n} символов.")
        elif p ** n < size:
            # Усечение алфавита
            alphabet = custom_alphabet[:p ** n]
            print(f"Алфавит усечён до {p ** n} символов.")
        # Если p**n == size, ничего не делаем

        # Ввод или генерация неприводимого многочлена
        choice_poly = input("\nХотите ввести свой неприводимый многочлен для аффинного шифра? (y/n): ").lower()
        if choice_poly == 'y':
            print(f"\nВведите коэффициенты неприводимого многочлена степени {n} над F_{p}.")
            print("Коэффициенты вводятся от старшего к младшему (например, для x^2 + x + 1 введите: 1 1 1)")
            while True:
                coeffs_str = input("Коэффициенты через пробел:\n").strip().split()
                if len(coeffs_str) != n + 1:
                    print(f"Неверное количество коэффициентов.\nОжидалось {n + 1}, получено {len(coeffs_str)}.")
                    continue
                try:
                    coeffs = [int(c) % p for c in coeffs_str]
                    coeffs = coeffs[::-1]  # От старшего к младшему -> от младшего к старшему
                    if not is_irreducible(coeffs, p):
                        print("Введённый многочлен неприводимым не является. Попробуйте снова.")
                        continue
                    modulus = tuple(coeffs)
                    break
                except ValueError:
                    print("Неверный ввод. Введите целые числа.")
        else:
            print("\nГенерируется неприводимый многочлен для аффинного шифра...")
            try:
                modulus_coeffs = find_random_irreducible_polynomial(p, n)
                modulus = tuple(modulus_coeffs)
                print(f"Сгенерированный неприводимый многочлен для аффинного шифра: {polynomial_to_string(modulus)}")
            except ValueError as e:
                print(str(e))
                return  # Возврат в подменю

    # Генерация элементов поля для аффинного шифра
    elements = generate_field_elements(p, n)

    # Сортировка элементов: сначала по степени, затем по коэффициенту
    # при старшей степени, затем лексикографически
    def sort_key_affine(x):
        deg = get_degree(x)
        if deg == -1:
            return (-1, 0, x)
        else:
            return (deg, x[deg], x)

    elements_sorted = sorted(elements, key=sort_key_affine)
    elements = elements_sorted

    # Создание отображений между символами и элементами поля после сортировки
    Affine.create_mappings_affine(alphabet, elements)
    print(f"\nЭлементы поля F_{p}^{n} для аффинного шифра:")
    for idx, elem in enumerate(elements, 1):
        elem_tuple = tuple(elem)
        print(f"{idx}. {polynomial_to_string(elem_tuple)}")

    # Формируем мультипликативную группу для вычисления обратных элементов
    multiplicative_group = [elem for elem in elements if any(c != 0 for c in elem)]

    # Подменю аффинного шифра
    while True:
        print("\n--- Аффинный Шифр ---")
        print("1. Установить ключ")
        print("2. Зашифровать текст")
        print("3. Расшифровать текст")
        print("4. Вернуться в главное меню")
        choice = input("Выберите опцию (1-4): ").strip()

        if choice == '1':
            # Передаём multiplicative_group как шестой аргумент
            modulus_coeffs = find_random_irreducible_polynomial(p, n)
            modulus = tuple(modulus_coeffs)
            set_affine_key(alphabet, elements, p, n, modulus, multiplicative_group)

        elif choice == '2':
            # Проверяем, установлены ли ключи (alpha_affine и beta_affine)
            if Affine.alpha_affine is None or Affine.beta_affine is None:
                print("Ключи не установлены. Сначала установите ключ (опция 1).")
                continue
            plaintext = input("Введите открытый текст:\n").strip()
            ciphertext = Affine.encrypt_text(plaintext, p, n, modulus)
            print(f"Зашифрованный текст: {ciphertext}")

        elif choice == '3':
            # Проверяем, установлены ли ключи и обратный элемент (alpha_inv_affine)
            if Affine.alpha_inv_affine is None or Affine.beta_affine is None:
                print("Ключи не установлены или α⁻¹ не найден. Сначала установите ключ (опция 1).")
                continue
            ciphertext = input("Введите шифртекст: ").strip()
            plaintext = Affine.decrypt_text(ciphertext, p, n, modulus)
            print(f"Расшифрованный текст: {plaintext}")

        elif choice == '4':
            print("Возврат в главное меню.")
            break

        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")


# Функция для построения основного поля Галуа (используется в опциях 1-3)
def build_main_galois_field():
    """
    Функция для построения основного поля Галуа F_{p^n},
    используемая в опциях 1-3.
    """
    print("\n--- Построение основного поля Галуа F_{p^n} ---")

    # Ввод p
    while True:
        try:
            p = int(input("Введите простое число p: "))
            if not is_prime(p):
                print("Введённое число не является простым. Попробуйте снова.")
                continue
            break
        except ValueError:
            print("Неверный ввод. Введите целое число.")

    # Ввод n
    while True:
        try:
            n = int(input("Введите степень расширения n: "))
            if n < 1:
                print("Степень расширения должна быть положительным целым числом.")
                continue
            break
        except ValueError:
            print("Неверный ввод. Введите целое число.")

    # Ввод или генерация неприводимого многочлена
    choice_poly = input("\nХотите ввести свой неприводимый многочлен? (y/n): ").lower()
    if choice_poly == 'y':
        print(f"\nВведите коэффициенты неприводимого многочлена степени {n} над F_{p}.")
        print("Коэффициенты вводятся от старшего к младшему (например, для 2x^2 -2x +1 введите: 2 -2 1)")
        while True:
            coeffs_str = input("Коэффициенты через пробел:\n").strip().split()
            if len(coeffs_str) != n + 1:
                print(f"Неверное количество коэффициентов.\nОжидалось {n + 1}, получено {len(coeffs_str)}.")
                continue
            try:
                # Переворачиваем список для внутреннего представления
                coeffs = [int(c) % p for c in coeffs_str]
                coeffs = coeffs[::-1]  # От старшего к младшему -> от младшего к старшему
                if not is_irreducible(coeffs, p):
                    print("Введённый многочлен неприводимым не является. Попробуйте снова.")
                    continue
                modulus = tuple(coeffs)
                break
            except ValueError:
                print("Неверный ввод. Введите целые числа.")
    else:
        print("\nГенерируется неприводимый многочлен...")
        try:
            modulus_coeffs = find_random_irreducible_polynomial(p, n)
            modulus = tuple(modulus_coeffs)
            print(f"Сгенерированный неприводимый многочлен:\n{polynomial_to_string(modulus)}")
        except ValueError as e:
            print(str(e))
            return None, None, None, None  # Возврат в главное меню

    # Генерация элементов поля
    elements = generate_field_elements(p, n)

    # Сортировка элементов: сначала по степени, затем по коэффициенту
    # при старшей степени, затем лексикографически
    def sort_key(x):
        deg = get_degree(x)
        if deg == -1:
            return (-1, 0, x)
        else:
            return (deg, x[deg], x)

    elements_sorted = sorted(elements, key=sort_key)
    elements = elements_sorted

    print(f"\nЭлементы поля F_{p}^{n}:")
    for idx, elem in enumerate(elements, 1):
        elem_tuple = tuple(elem)
        print(f"{idx}. {polynomial_to_string(elem_tuple)}")

    return p, n, modulus, elements


# Основной блок программы
if __name__ == "__main__":
    print("Инструмент для построения и исследования полей Галуа F_{p^n}\n")

    # Переменные для основного поля Галуа
    main_field_built = False
    p_main = 0
    n_main = 0
    modulus_main = []
    elements_main = []
    multiplicative_group_main = []
    order_main = 0
    generators_main = []

    while True:
        display_menu()
        choice = input("\nВыберите опцию (1-5): ").strip()

        if choice == '1':
            # Построение основного поля Галуа
            p_main, n_main, modulus_main, elements_main = build_main_galois_field()
            if p_main is not None:
                main_field_built = True

        elif choice == '2':
            # Арифметические операции над основным полем
            if not main_field_built:
                print("\nОсновное поле Галуа не построено. Сначала выберите опцию 1.")
                continue
            print("\n--- Арифметические операции над элементами основного поля ---")
            print("Введите два многочлена из списка ниже для выполнения операции:")
            for idx, elem in enumerate(elements_main, 1):
                print(f"{idx}. {polynomial_to_string(elem)}")

            # Ввод первого многочлена
            poly1 = input_polynomial_element(elements_main, p_main, n_main)
            # Ввод второго многочлена
            poly2 = input_polynomial_element(elements_main, p_main, n_main)

            # Выбор операции
            while True:
                operation = input("Выберите операцию (сложение - '+', умножение - '*'): ").strip()
                if operation not in ['+', '*']:
                    print("Неверная операция. Введите '+' для сложения или '*' для умножения.")
                    continue
                break

            # Выполнение операции
            if operation == '+':
                result = poly_add(poly1, poly2, p_main)
                print(f"\nРезультат сложения:\n{polynomial_to_string(result)}")
            else:
                # Для умножения используется функция poly_multiply, которая выполняет редукцию
                result = poly_multiply(tuple(poly1), tuple(poly2), modulus_main, p_main)
                print(f"\nРезультат умножения:\n{polynomial_to_string(result)}")

        elif choice == '3':
            # Исследование мультипликативной группы основного поля
            if not main_field_built:
                print("\nОсновное поле Галуа не построено. Сначала выберите опцию 1.")
                continue
            print("\n--- Исследование мультипликативной группы основного поля F_{p^n}^* ---")

            # Формирование мультипликативной группы (исключаем ноль)
            multiplicative_group_main = [
                tuple(elem) for elem in elements_main if any(c != 0 for c in elem)
            ]
            order_main = p_main ** n_main - 1
            print(f"\nМультипликативная группа F_{p_main}^{n_main}^* имеет порядок {order_main}.")

            # Нахождение образующих
            generators_main = find_generators(multiplicative_group_main, modulus_main, p_main, order_main)
            if generators_main:
                print("\nОбразующие элементы мультипликативной группы:")
                for idx, gen in enumerate(generators_main, 1):
                    print(f"{idx}. {polynomial_to_string(gen)}")
            else:
                print("Образующих элементов мультипликативной группы не найдено.")
                continue

            # Определение порядков элементов
            print("\nПорядки элементов мультипликативной группы:")
            identity = tuple([1] + [0] * (len(modulus_main) - 1))
            for elem in multiplicative_group_main:
                ord_elem = element_order(elem, multiplicative_group_main, modulus_main, p_main)
                print(f" {polynomial_to_string(elem)} : {ord_elem}")

            # Выбор образующего для разложения
            while True:
                choice_gen = input(
                    "\nВыберите образующий по номеру для разложения элементов по степеням (или 'exit' для выхода): "
                )
                if choice_gen.lower() == 'exit':
                    print("Возврат в главное меню.")
                    break
                try:
                    choice_gen = int(choice_gen)
                    if not (1 <= choice_gen <= len(generators_main)):
                        print("Неверный номер образующего. Попробуйте снова.")
                        continue
                    selected_gen = generators_main[choice_gen - 1]
                    break
                except ValueError:
                    print("Неверный ввод. Введите номер образующего или 'exit'.")

            # Разложение элементов по выбранному образующему
            if 'selected_gen' in locals():
                print(
                    f"\nРазложение элементов по степеням выбранного образующего "
                    f"{polynomial_to_string(selected_gen)}:"
                )
                decomposition = {}
                current = tuple([1] + [0] * (n_main - 1))  # Элемент 1
                for exponent in range(order_main):
                    decomposition[current] = exponent
                    current = poly_multiply(current, selected_gen, modulus_main, p_main)

                for elem in multiplicative_group_main:
                    exponent = decomposition.get(elem, None)
                    if exponent is not None:
                        print(
                            f" {polynomial_to_string(elem)} = "
                            f"({polynomial_to_string(selected_gen)})^{exponent}"
                        )
                    else:
                        print(
                            f" {polynomial_to_string(elem)} "
                            f"не представляется в виде {polynomial_to_string(selected_gen)}^k"
                        )

        elif choice == '4':
            # Работа с аффинным шифром
            affine_cipher_menu()

        elif choice == '5':
            # Выход
            print("\nЗавершение работы. До свидания!")
            break

        else:
            print("\nНеверная опция. Пожалуйста, выберите из меню (1-5).")
