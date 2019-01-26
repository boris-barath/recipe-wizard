import json
import nltk

from ingredient_parser import parse

if __name__ == "__main__":
    with open('data.json', 'r') as file:
        data = json.loads(file.read())

        for recipe in data['recipes']:
            for ingredient in recipe['ingredientLines']:
                ingredient = parse(ingredient)['name']
                tokens = nltk.word_tokenize(ingredient)
                tagged = nltk.pos_tag(tokens)
                print(tagged)

            break
