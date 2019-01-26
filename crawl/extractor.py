import json

import itertools
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
                ingredients = itertools.dropwhile(lambda ingredient: not ingredient[1].startswith('NN'), tagged)
                ingredients = itertools.takewhile(lambda ingredient: ingredient[1].startswith('NN'), ingredients)
                ingredients = map(lambda ingredient: ingredient[0], ingredients)

                print(f"Extracted: {' '.join(list(ingredients))} - All: {ingredient}")