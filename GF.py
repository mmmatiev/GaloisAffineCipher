import itertools
import random

def is_prime(p):
    """Проверяет, является ли число p простым."""
    if p < 2:
        return False
    for i in range(2, int(p ** 0.5) + 1):
        if p % i == 0:
            return False
    return True

def poly_add(a, b, p):
    """
    Сложение двух многочленов a и b по модулю p.
    Многочлены представлены как списки коэффициентов от младшего к старшему.
    """
    max_len = max(len(a), len(b))
    result = []
    for i in range(max_len):
        coeff_a = a[i] if i < len(a) else 0
        coeff_b = b[i] if i < len(b) else 0
        result.append((coeff_a + coeff_b) % p)
    # Удаление ведущих нулей
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result

def poly_multiply(a, b, modulus, p):
    """
    Умножает два элемента поля Галуа, представленных как кортежи коэффициентов.
    Приведение выполняется по модулю заданного неприводимого многочлена (modulus).
    """
    a_list = list(a)
    b_list = list(b)
    product = [0] * (len(a_list) + len(b_list) - 1)

    for i, coeff_a in enumerate(a_list):
        for j, coeff_b in enumerate(b_list):
            product[i + j] = (product[i + j] + coeff_a * coeff_b) % p

    _, remainder = poly_divmod(product, list(modulus), p)

    while len(remainder) > 1 and remainder[-1] == 0:
        remainder.pop()

    n = len(modulus) - 1
    while len(remainder) < n:
        remainder.append(0)

    remainder = tuple(remainder[:n])
    return remainder

def poly_divmod(a, b, p):
    """
    Деление многочлена a на многочлен b по модулю p.
    Возвращает кортеж (частное, остаток).
    Многочлены представлены как списки коэффициентов от младшего к старшему.
    """
    a = a[:]  # Копия списка
    b = b[:]
    if len(b) == 0 or all(coeff == 0 for coeff in b):
        raise ZeroDivisionError("Деление на нулевой многочлен невозможно.")

    quotient = [0] * (len(a) - len(b) + 1) if len(a) >= len(b) else []
    while len(a) >= len(b):
        coeff = a[-1] * modinv(b[-1], p) % p
        if coeff == 0:
            # Если коэффициент равен нулю, удаляем ведущий коэффициент и продолжаем
            a.pop()
            continue
        degree_diff = len(a) - len(b)
        quotient[degree_diff] = coeff

        for i in range(len(b)):
            a[degree_diff + i] = (a[degree_diff + i] - coeff * b[i]) % p

        # Удаляем ведущие нули
        while len(a) > 0 and a[-1] == 0:
            a.pop()

    remainder = a if a else [0]
    return (quotient, remainder)

def modinv(a, p):
    """
    Находит мультипликативную обратную по модулю p.
    Использует расширенный алгоритм Евклида.
    """
    a = a % p
    if a == 0:
        raise ZeroDivisionError("Нет обратного элемента для 0.")

    lm, hm = 1, 0
    low, high = a, p
    while low > 1:
        ratio = high // low
        nm = hm - lm * ratio
        new = high - low * ratio
        hm, lm = lm, nm
        high, low = low, new
    return lm % p

def is_irreducible(poly, p):
    """
    Проверяет, является ли многочлен неприводимым над полем F_p.
    Многочлен представлен как список коэффициентов от младшего к старшему.
    """
    deg = len(poly) - 1
    if deg < 1:
        return False

    # Проверка наличия корней в F_p
    for a in range(p):
        val = 0
        power = 1
        for coeff in poly:
            val = (val + coeff * power) % p
            power = (power * a) % p
        if val == 0:
            return False

    # Проверка на делимость на все многочлены меньшей степени
    for d in range(2, (deg // 2) + 1):
        for divisor in itertools.product(range(p), repeat=d + 1):
            # Лидирующий коэффициент не должен быть нулем
            if divisor[-1] == 0:
                continue
            divisor = list(divisor)
            _, remainder = poly_divmod(poly, divisor, p)
            if all(c == 0 for c in remainder):
                return False

    return True

def find_random_irreducible_polynomial(p, n, max_attempts=1000):
    """
    Рандомно генерирует многочлен степени n над полем F_p и проверяет его на неприводимость.
    Если неприводимый многочлен найден, возвращает его.
    В противном случае, после max_attempts попыток, выбрасывает исключение.
    """
    tried = set()
    total_polynomials = p ** (n + 1) - p ** n  # Всего многочленов с ненулевым старшим коэффициентом
    attempts = 0

    while attempts < max_attempts and len(tried) < total_polynomials:
        # Генерация случайных коэффициентов от младшего к старшему
        coeffs = [random.randint(0, p - 1) for _ in range(n + 1)]
        if coeffs[-1] == 0:
            continue

        poly_tuple = tuple(coeffs)
        if poly_tuple in tried:
            continue  # уже проверенный многочлен
        tried.add(poly_tuple)
        attempts += 1

        if is_irreducible(coeffs, p):
            return coeffs

    raise ValueError(
        f"Не удалось найти неприводимый многочлен степени {n} над F_{p} после {max_attempts} попыток."
    )

def generate_field_elements(p, n):
    """
    Генерирует все элементы поля Галуа F_{p^n}.
    Каждый элемент представлен как кортеж коэффициентов многочлена.
    """
    return list(itertools.product(range(p), repeat=n))

def get_degree(poly):
    """
    Возвращает степень многочлена.
    Для нулевого многочлена возвращает -1.
    """
    for i in reversed(range(len(poly))):
        if poly[i] != 0:
            return i
    return -1

def polynomial_to_string(poly):
    """
    Преобразует многочлен из списка коэффициентов в строку.
    Пример: [1, 0, 2] -> "2x^2 + 1"
    """
    degree = get_degree(poly)
    if degree == -1:
        return "0"

    terms = []
    for i in range(degree, -1, -1):
        coeff = poly[i]
        if coeff == 0:
            continue
        term = ""
        if i == 0:
            term = f"{coeff}"
        elif i == 1:
            if coeff == 1:
                term = "x"
            elif coeff == -1:
                term = "-x"
            else:
                term = f"{coeff}x"
        else:
            if coeff == 1:
                term = f"x^{i}"
            elif coeff == -1:
                term = f"-x^{i}"
            else:
                term = f"{coeff}x^{i}"
        terms.append(term)

    # Объединение терминов с правильными знаками
    polynomial = terms[0]
    for term in terms[1:]:
        if term.startswith('-'):
            polynomial += f" - {term[1:]}"
        else:
            polynomial += f" + {term}"
    return polynomial

def find_generators(multiplicative_group, modulus, p, order):
    """
    Находит образующие элементы мультипликативной группы F_{p^n}^*.
    """
    generators = []
    # Находим простые множители порядка группы
    factors = set()
    temp = order
    for i in range(2, int(order ** 0.5) + 1):
        while temp % i == 0:
            factors.add(i)
            temp = temp // i
    if temp > 1:
        factors.add(temp)

    # Корректное определение identity
    n = len(modulus) - 1
    identity = tuple([1] + [0] * (n - 1))  # Для n=2: (1, 0)

    for elem in multiplicative_group:
        if elem == tuple([0] * len(elem)):
            continue  # Пропускаем ноль
        is_generator = True
        for factor in factors:
            exp = order // factor
            power = power_element(elem, exp, modulus, p)
            if power == identity:
                is_generator = False
                break
        if is_generator:
            generators.append(elem)
    return generators

def power_element(elem, exponent, modulus, p):
    """
    Возводит элемент поля Галуа в заданную степень.
    """
    result = tuple([1] + [0] * (len(modulus) - 1))  # Элемент 1
    base = elem
    while exponent > 0:
        if exponent % 2 == 1:
            result = poly_multiply(result, base, modulus, p)
        base = poly_multiply(base, base, modulus, p)
        exponent = exponent // 2
    return result

def element_order(elem, multiplicative_group, modulus, p):
    """
    Определяет порядок элемента в мультипликативной группе.
    """
    if elem == tuple([0] * len(elem)):
        return 0
    order = 1
    power = elem
    n = len(modulus) - 1
    identity = tuple([1] + [0] * (n - 1))  # Для n=2: (1, 0)

    while power != identity:
        power = poly_multiply(power, elem, modulus, p)
        order += 1
        if order > len(multiplicative_group):
            return order  # Защита от бесконечного цикла
    return order
