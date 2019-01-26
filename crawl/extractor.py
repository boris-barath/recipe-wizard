from collections import defaultdict
import json


class Recipe:
    def __init__(self, id, ingredients):
        self.id = id
        self.ingredients = list(ingredients)
        self.is_impossible = False

    def impossible(self):
        self.is_impossible = True

    def add_ingredient(self, ingredient):
        self.ingredients.add(ingredient)

    def calculate_ease(self, frequency_table):
        if self.is_impossible:
            self.difficulty = -1
            return

        self.difficulty = 1

        for ingredient in self.ingredients:
            self.difficulty *= frequency_table[ingredient]


def return_question(reverse_mapping, recipes, available, not_available):
    can_complete = []

    for recipe in recipes:
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

        for recipe in recipes:
            for ingredient in recipe.ingredients:
                frequencies[ingredient] += 1

        maximum_ingredient = frequencies[max(frequencies, key=frequencies.get)]

        for key in frequencies:
            frequencies[key] /= maximum_ingredient

        difficulty = 0
        easiest_recipe = None

        for recipe in recipes:
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


def get_recipes(data):
    return map(lambda x:
               Recipe(
                   x.get('id'),
                   map(lambda y: y.get('ingredient').lower(), x.get('ingredients'))),
               data)


def get_data():
    with open('recipes.json', 'r') as file:
        data = json.loads(file.read())
        recipes = list(filter(lambda x: len(x.ingredients) > 0, get_recipes(data)))

        reverse_mapping = defaultdict(list)
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                reverse_mapping[ingredient].append(recipe)

        return recipes, reverse_mapping


def main():
    recipes, reverse_mapping = get_data()

    available = []
    not_available = []

    while True:
        question = return_question(reverse_mapping, recipes, available, not_available)

        if type(question) == str:
            print(f'Do you have: {question}')
        else:
            print(f'Recipe: {question[0].id}')

        response = input("Do you have this ingredient: ")
        if response == 'yes':
            available.append(question)
        else:
            not_available.append(question)


if __name__ == "__main__":
    main()
