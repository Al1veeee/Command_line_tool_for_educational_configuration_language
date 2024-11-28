import re
from xml.etree.ElementTree import Element, SubElement, tostring


class ConfigParser:
    def __init__(self, config_text):
        self.config_text = config_text
        self.constants = {}

    def parse(self):
        lines = self.config_text.splitlines()
        for line in lines:
            self.parse_constant(line.strip())

    def parse_constant(self, line):
        match = re.match(r"const (\w+) = (.+);", line)
        if match:
            name = match.group(1)
            value = match.group(2)
            self.constants[name] = self.evaluate(value)
        else:
            raise SyntaxError(f"Invalid constant declaration: {line}")

    def evaluate(self, expr):
        expr = expr.strip()

        # Check for undefined constants (e.g., $undefined$)
        if expr.startswith("$") and expr.endswith("$"):
            raise ValueError(f"Undefined constant: {expr}")

        if expr.startswith("list(") and expr.endswith(")"):
            return self.parse_list(expr)
        elif expr.isdigit():  # Check if the expression is an integer
            return int(expr)
        elif expr.replace('.', '', 1).isdigit():  # Check for float numbers
            return float(expr)
        elif expr.isidentifier():  # Check if the expression is an identifier (variable name)
            return expr
        elif expr.startswith('"') and expr.endswith('"'):  # Check if the expression is a string in double quotes
            return expr[1:-1]
        elif expr.startswith("'") and expr.endswith("'"):  # Check if the expression is a string in single quotes
            return expr[1:-1]
        else:
            raise SyntaxError(f"Invalid expression: {expr}")

    def parse_list(self, expr):
        if not expr.startswith("list(") or not expr.endswith(")"):
            raise SyntaxError(f"Invalid list syntax: {expr}")

        inner = expr[5:-1].strip()  # Убираем 'list(' и ')'
        items = []
        buffer = ""
        stack = 0

        for char in inner:
            if char == "," and stack == 0:  # Новая часть, если не внутри вложенного списка
                items.append(self.evaluate(buffer.strip()))
                buffer = ""
            else:
                buffer += char
                if char == "(":
                    stack += 1
                elif char == ")":
                    stack -= 1

        if buffer.strip():  # Добавляем последний элемент
            items.append(self.evaluate(buffer.strip()))

        return items

    def to_xml(self):
        """
        Преобразует разобранные данные конфигурации в XML-строку.
        """
        root = Element("configuration")
        for name, value in self.constants.items():
            constant = SubElement(root, "constant", name=name)

            if isinstance(value, list):  # Если значение - список
                list_element = SubElement(constant, "list")
                for item in value:
                    item_element = SubElement(list_element, "value")
                    item_element.text = str(item)
            else:  # Простое значение
                constant.text = str(value)

        # Преобразуем дерево XML в строку
        return tostring(root, encoding="unicode")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert configuration to XML.")
    parser.add_argument("--input", required=True, help="Path to input configuration file.")
    parser.add_argument("--output", required=True, help="Path to output XML file.")
    args = parser.parse_args()

    try:
        # Считываем входной файл
        with open(args.input, "r") as input_file:
            config_text = input_file.read()

        # Парсим и преобразуем в XML
        config_parser = ConfigParser(config_text)
        config_parser.parse()
        xml_output = config_parser.to_xml()

        # Сохраняем результат в выходной файл
        with open(args.output, "w") as output_file:
            output_file.write(xml_output)

        print("Conversion successful.")
    except Exception as e:
        print(f"Error: {e}")
