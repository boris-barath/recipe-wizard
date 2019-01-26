import json

import itertools

import math
import operator

import nltk
from collections import defaultdict

from ingredient_parser import parse


class Recipe:
    def __init__(self):
        self.all_ingredients = set()
        self.ingredients = set()
        self.is_impossible = False

    def impossible(self):
        self.is_impossible = True

    def add_ingredient(self, ingredient):
        self.all_ingredients.add(ingredient)
        self.ingredients.add(ingredient)

    def calculate_ease(self, frequency_table):
        if self.is_impossible:
            self.difficulty = -1
            return

        self.difficulty = 1

        for ingredient in self.ingredients:
            self.difficulty *= frequency_table[ingredient]


def return_question(reverse_mapping, formatted_recipes, available, not_available):
    can_complete = []

    for recipe in formatted_recipes:
        for item in available:
            if item in recipe.ingredients:
                recipe.ingredients.remove(item)

        for item in not_available:
            if item in recipe.ingredients:
                recipe.impossible()

        if len(recipe.ingredients) == 0:
            can_complete.append(recipe)

    for ingredient in available + not_available:
        if ingredient in reverse_mapping:
            del reverse_mapping[ingredient]

    if can_complete:
        return can_complete
    else:
        frequencies = defaultdict(float)

        for recipe in formatted_recipes:
            for ingredient in recipe.ingredients:
                frequencies[ingredient] += 1

        maximum_ingredient = frequencies[max(frequencies, key=frequencies.get)]

        for key in frequencies:
            frequencies[key] /= maximum_ingredient

        difficulty = 0
        easiest_recipe = None

        for recipe in formatted_recipes:
            recipe.calculate_ease(frequencies)

            if recipe.difficulty > difficulty:
                difficulty = recipe.difficulty
                easiest_recipe = recipe

        ingredient_difficulty = 0
        easiest_ingredient = None
        for ingredient in easiest_recipe.ingredients:
            if frequencies[ingredient] > ingredient_difficulty:
                ingredient_difficulty = frequencies[ingredient]
                easiest_ingredient = ingredient

        print(difficulty, ingredient_difficulty)

        return easiest_ingredient


if __name__ == "__main__":
    with open('data.json', 'r') as file:
        data = json.loads(file.read())
        reverse_mapping = defaultdict(list)
        formatted_recipes = []

        for recipe in data['recipes']:
            formatted_ingredients = set()
            formatted_recipe = Recipe()

            for ingredient in recipe['ingredientLines']:
                ingredient = parse(ingredient)['name']
                tokens = nltk.word_tokenize(ingredient)
                tagged = nltk.pos_tag(tokens)
                ingredients = itertools.dropwhile(lambda ingredient: not ingredient[1].startswith('NN'), tagged)
                ingredients = itertools.takewhile(lambda ingredient: ingredient[1].startswith('NN'), ingredients)
                ingredients = map(lambda ingredient: ingredient[0], ingredients)

                formatted = ' '.join(list(ingredients))

                formatted_recipe.add_ingredient(formatted)
                reverse_mapping[formatted].append(formatted_recipe)

            formatted_recipes.append(formatted_recipe)

    print(reverse_mapping)
    available = []
    not_available = []

    while True:
        question = return_question(reverse_mapping, formatted_recipes, available, not_available)

        if type(question) == str:
            print(f'Do you have: {question}')
        else:
            print(f'Recipe: {question[0].all_ingredients}')

        response = input("Do you have this ingredient: ")
        if response == 'yes':
            available.append(question)
        else:
            not_available.append(question)
