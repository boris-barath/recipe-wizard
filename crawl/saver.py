import json

if __name__ == "__main__":
    with open('data.json', 'rb') as file:
        with open('output.txt', 'wb') as out:
            data = json.loads(file.read())

            for recipe in data['recipes']:
                for ingredient in recipe['ingredients']:
                    out.write(f'{ingredient["text"]}\n'.encode('utf-8'))

                out.write(f'-\n'.encode('utf-8'))