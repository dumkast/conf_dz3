import subprocess
import os

def run_converter(input_content, expected_output, input_filename="test_input.toml", output_filename="test_output.txt"):
    # Записываем входные данные в тестовый файл TOML
    with open(input_filename, "w") as file:
        file.write(input_content)

    # Запускаем процесс с помощью converter
    result = subprocess.run(
        ["python", "converter.py", input_filename, output_filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Проверяем, что не было ошибок
    assert result.returncode == 0, f"Ошибка выполнения: {result.stderr}"

    # Сравниваем результат
    with open(output_filename, "r") as file:
        output = file.read()
        assert output == expected_output, f"Ожидалось: {expected_output}, Получено: {output}"

    # Удаляем временные файлы
    os.remove(input_filename)
    os.remove(output_filename)

def test_single_line_comments():
    input_content = """
    # Это однострочный комментарий
    """
    expected_output = "-- Это однострочный комментарий\n"
    run_converter(input_content, expected_output)

def test_multi_line_comments():
    input_content = """
    # Это многострочный
    # комментарий
    """
    expected_output = "(comment\n Это многострочный\n комментарий\n)\n"
    run_converter(input_content, expected_output)

def test_arrays():
    input_content = """
    colors = ["red", "green", "blue"]
    """
    expected_output = "colors is << 'red', 'green', 'blue' >>\n"
    run_converter(input_content, expected_output)

def test_dictionaries():
    input_content = """
    [person]
    name = "John Doe"
    age = 30
    """
    expected_output = "person is table([\n name = 'John Doe',\n age = 30\n])\n"
    run_converter(input_content, expected_output)

def test_constants():
    input_content = """
    f = 5
    h = "#{f + 5}"
    """
    expected_output = "f is 5\nh is 10\n"
    run_converter(input_content, expected_output)

def test_calculations():
    input_content = """
    a = 3
    b = 4
    c = "#{a + b}"
    d = "#{b - 2}"
    e = "#{b * a}"
    f = "#{b / 2}"
    """
    expected_output = "a is 3\nb is 4\nc is 7\nd is 2\ne is 12\nf is 2.0\n"
    run_converter(input_content, expected_output)

def test_min_function():
    input_content = """
    x = 10
    y = 5
    z = "#{min(x, y)}"
    """
    expected_output = "x is 10\ny is 5\nz is 5\n"
    run_converter(input_content, expected_output)

# Запуск всех тестов
if __name__ == "__main__":
    test_single_line_comments()
    test_multi_line_comments()
    test_arrays()
    test_dictionaries()
    test_constants()
    test_calculations()
    test_min_function()
    print("\nВсе тесты пройдены успешно.")
