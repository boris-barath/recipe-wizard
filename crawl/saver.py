import json

from ingredient_parser import parse

if __name__ == "__main__":
    with open('data.json', 'rb') as file:
        with open('output-parsed.txt', 'wb') as out:
            data = json.loads(file.read())

            for recipe in data['recipes']:
                for ingredient in recipe['ingredients']:
                    ingredient = parse(ingredient["text"])['name']
                    out.write(f'{ingredient}\n'.encode('utf-8'))

                out.write(f'-\n'.encode('utf-8'))
