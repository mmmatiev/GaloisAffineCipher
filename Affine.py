from GF import (
    poly_add, poly_multiply, polynomial_to_string
)

# Глобальные переменные:
alpha_affine = None
beta_affine = None
alpha_inv_affine = None

char_to_field_affine = {}
field_to_char_affine = {}

# Функция для создания отображений между символами алфавита и элементами поля
def create_mappings_affine(alphabet, field_elements):
    """
    Преобразует каждый элемент field_elements в tuple длины n и сопоставляет символам алфавита.
    """
    global char_to_field_affine, field_to_char_affine
    char_to_field_affine = {}
    field_to_char_affine = {}
    # Предположим, что len(field_elements) == len(alphabet) == p^n
    # и что каждый field_elements[i] уже имеет длину n.
    for idx, char in enumerate(alphabet):
        elem = tuple(field_elements[idx])
        char_to_field_affine[char] = elem
        field_to_char_affine[elem] = char

def pad_or_trim_to_n(poly_tuple, n):
    """
    Приводит кортеж poly_tuple к длине n:
    - если len(poly_tuple) > n, обрезает справа,
    - если len(poly_tuple) < n, добавляет 0.
    """
    poly_list = list(poly_tuple)
    if len(poly_list) > n:
        poly_list = poly_list[:n]
    while len(poly_list) < n:
        poly_list.append(0)
    return tuple(poly_list)

def compute_inverse_affine(elem, multiplicative_group, modulus, p, n):
    """
    Вычисляет мультипликативную обратную для элемента в аффинном шифре.
    """
    print(f"Вычисление обратного элемента для: {polynomial_to_string(elem)}")
    for candidate in multiplicative_group:
        product = poly_multiply(elem, candidate, modulus, p)
        identity = tuple([1] + [0] * (n - 1))  # Представление единицы в поле
        if product == identity:
            print(f"Найден обратный элемент: {polynomial_to_string(candidate)}")
            return candidate
    raise ValueError("Обратный элемент не найден.")

def encrypt_text(plaintext, p, n, modulus):
    ciphertext = ''
    for char in plaintext:
        if char not in char_to_field_affine:
            print(f"Символ '{char}' отсутствует в алфавите. Заменяем на '?'.")
            ciphertext += '?'
            continue

        x = char_to_field_affine[char]
        print(f"Шифруем '{char}' -> {polynomial_to_string(x)}")

        alpha_x = poly_multiply(alpha_affine, x, modulus, p)
        print(f"α * x = {polynomial_to_string(alpha_x)}")

        y = poly_add(alpha_x, beta_affine, p)
        y = tuple(y)
        print(f"α * x + β = {polynomial_to_string(y)}")

        # ДОПОЛНЯЕМ/ОБРЕЗАЕМ ДО n
        y = pad_or_trim_to_n(y, n)

        if y in field_to_char_affine:
            encrypted_char = field_to_char_affine[y]
            print(f"Соответствующий символ: '{encrypted_char}'")
            ciphertext += encrypted_char
        else:
            print(f"Элемент {polynomial_to_string(y)} не найден в отображении. Заменяем на '?'.")
            ciphertext += '?'

    return ciphertext

def decrypt_text(ciphertext, p, n, modulus):
    plaintext = ''
    for char in ciphertext:
        if char not in field_to_char_affine.values():
            print(f"Символ '{char}' не является зашифрованным символом. Заменяем на '?'.")
            plaintext += '?'
            continue

        y = None
        for key_elem, value_char in field_to_char_affine.items():
            if value_char == char:
                y = key_elem
                break

        if y is None:
            print(f"Элемент для символа '{char}' не найден. Заменяем на '?'.")
            plaintext += '?'
            continue

        print(f"Дешифруем '{char}' -> {polynomial_to_string(y)}")
        # Аддитивная инверсия в поле (y -> -y)
        negate_beta = tuple((-c) % p for c in beta_affine)
        y_minus_beta = poly_add(y, negate_beta, p)
        print(f"y - β = {polynomial_to_string(y_minus_beta)}")

        alpha_inv_y = poly_multiply(alpha_inv_affine, y_minus_beta, modulus, p)
        alpha_inv_y = tuple(alpha_inv_y)
        print(f"α⁻¹ * (y - β) = {polynomial_to_string(alpha_inv_y)}")

        # Дополняем/обрезаем до n
        alpha_inv_y = pad_or_trim_to_n(alpha_inv_y, n)

        if alpha_inv_y in field_to_char_affine:
            decrypted_char = field_to_char_affine[alpha_inv_y]
            print(f"Соответствующий символ: '{decrypted_char}'")
            plaintext += decrypted_char
        else:
            print(f"Элемент {polynomial_to_string(alpha_inv_y)} не найден в отображении. Заменяем на '?'.")
            plaintext += '?'

    return plaintext
