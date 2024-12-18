import argparse
import toml

class SyntaxError(Exception):
    pass

global_context = {}

# Чтение и запись TOML файлов с комментариями
def read_write_toml(file_path, mode='r', lines=None):
    try:
        with open(file_path, mode) as file:
            if mode == 'r':
                return file.readlines()
            file.writelines(lines)
    except Exception as e:
        raise SyntaxError(f"Ошибка при {mode} файла: {e}")

# Оценка выражений
def evaluate_expression(expression, context):
    try:
        context_with_min = {**context, "min": min}
        return eval(expression, {"__builtins__": None}, context_with_min)
    except Exception as e:
        raise SyntaxError(f"Ошибка при вычислении выражения '{expression}': {e}")

# Добавление данных в глобальный контекст
def add_to_context(data, context):
    for key, value in data.items():
        if isinstance(value, dict):
            add_to_context(value, context)
        else:
            context[key] = value

# Преобразование значений в конфигурационный формат
def convert_value(value, context=None):
    if isinstance(value, str):
        return f"'{value}'" if not value.startswith("#{") else str(evaluate_expression(value[2:-1].strip(), context))
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "<< " + ", ".join([convert_value(v, context) for v in value]) + " >>"
    if isinstance(value, dict):
        return "table([\n" + ",\n".join([f" {k} = {convert_value(v, context)}" for k, v in value.items()]) + "\n])"
    raise SyntaxError(f"Неподдерживаемое значение: {value}")

# Преобразование TOML в формат учебного конфигурационного языка
def convert_toml_to_custom_syntax(data, context):
    return [f"{key} is {convert_value(value, context)}" for key, value in data.items() if
            isinstance(value, (dict, list, str, int, float))]

# Основная функция обработки файлов
def process_files(input_file, output_file):
    lines = read_write_toml(input_file)
    try:
        data = toml.loads("".join(line for line in lines if not line.strip().startswith("#")))
    except toml.TomlDecodeError as e:
        raise SyntaxError(f"Ошибка при разборе TOML: {e}")

    add_to_context(data, global_context)
    converted_data = convert_toml_to_custom_syntax(data, global_context)

    output_lines, comment_block, data_index = [], [], 0
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith("#"):
            comment_block.append(stripped_line[1:].strip())  # Сохраняем комментарий без '#'
            if i + 1 == len(lines) or not lines[i + 1].strip().startswith("#"):
                # Если комментариев больше одного, выводим многострочный комментарий
                if len(comment_block) == 1:
                    output_lines.append(f"-- {comment_block[0]}\n")  # Одиночный комментарий
                else:
                    output_lines.append(f"(comment\n{''.join(f' {line}\n' for line in comment_block)})\n")  # Многострочный комментарий
                comment_block = []
        elif stripped_line.startswith("[") and "]" in stripped_line or stripped_line:
            # Перед добавлением проверяем, не вышли ли за пределы списка converted_data
            if data_index < len(converted_data):
                output_lines.append(f"{converted_data[data_index]}\n")
                data_index += 1
    read_write_toml(output_file, 'w', output_lines)

def main():
    parser = argparse.ArgumentParser(description="Конвертация TOML файла в учебный конфигурационный язык")
    parser.add_argument("input_file", help="Путь к входному TOML файлу")
    parser.add_argument("output_file", help="Путь к выходному файлу")
    args = parser.parse_args()

    try:
        process_files(args.input_file, args.output_file)
        print("Конвертация завершена успешно.")
    except SyntaxError as e:
        print(f"Ошибка синтаксиса: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()