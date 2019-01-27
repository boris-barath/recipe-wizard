from collections import defaultdict
import json
import random


class Recipe:
    def __init__(self, id, name, calories, ingredients, directions):
        self.id = id
        self.name = name
        self.calories = calories
        self.ingredients = list(ingredients)
        self.directions = list(directions)
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
    """
    Returns dictionary
    {
        available_recipes: [...],
        next_question: <string>
    }

    """
    to_remove = []
    ret = {
            "available_recipes": [],
            "recipes": None
          }

    print("number of available recipes: ", len(recipes))

    for i, recipe in enumerate(recipes):
        for item in not_available:
            if item in recipe.ingredients:
                recipe.impossible()
                to_remove.append(i)
                continue

        for item in available:
            if item in recipe.ingredients:
                recipe.ingredients.remove(item)

        if len(recipe.ingredients) == 0:
            ret["recipes"].append(recipe)
            to_remove.append(i)

    for i in to_remove[::-1]:
        recipes.pop(i)

    for ingredient in available + not_available:
        if ingredient in reverse_mapping:
            del reverse_mapping[ingredient]

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

        if recipe.difficulty > difficulty and recipe.difficulty < 1:
            difficulty = recipe.difficulty
            easiest_recipe = recipe

    ingredient_difficulty = 0
    easiest_ingredient = None
    for ingredient in easiest_recipe.ingredients:
        if frequencies[ingredient] > ingredient_difficulty:
            ingredient_difficulty = frequencies[ingredient]
            easiest_ingredient = ingredient

    print(difficulty, ingredient_difficulty)

    ret["question"] = easiest_ingredient

    return ret


def get_recipes(data):
    return map(lambda x:
               Recipe(
                   x.get('id'),
                   x.get('name'),
                   x.get('calories'),
                   map(lambda y: y.get('ingredient').lower(), x.get('ingredients')),
                   map(lambda y: y.get('direction'), x.get('directions'))
               ),
               data)


def get_data(path='recipes.json'):
    with open(path, 'r') as file:
        data = json.loads(file.read())
        recipes = list(filter(lambda x: len(x.ingredients) > 0, get_recipes(data)))

        reverse_mapping = defaultdict(list)
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                reverse_mapping[ingredient].append(recipe)

        return recipes, reverse_mapping


def main():
    recipes, reverse_mapping = get_data()

    n_of_recipes = 3

    available = []
    not_available = []
    available_recipes = []

    while True:
        question = return_question(reverse_mapping, recipes, available, not_available)

        available_recipes.extend(question["recipes"])
        if available_recipes:
            k = min(len(available_recipes), n_of_recipes)
            suggestions = random.sample(available_recipes, k)

            for recipe in suggestions:
                available_recipes.remove(recipe)
            suggestions = list(map(str, map(id, suggestions)))
            print(" ".join(suggestions))

        print(f'Do you have: {question["question"]}')

        response = input("Do you have this ingredient: ")
        if response == 'yes':
            available.append(question["question"])
        else:
            not_available.append(question["question"])

if __name__ == "__main__":
    main()
