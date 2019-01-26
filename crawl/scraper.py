import os
import requests
from ratelimiter import RateLimiter
import json

PATH = 'https://api.edamam.com/search'
APP_ID = os.environ['APP_ID']
APP_KEY = os.environ['APP_KEY']


@RateLimiter(max_calls=5, period=60)
def search(query, data, seen):
    response = requests.get(PATH, params={'app_id': APP_ID, 'app_key': APP_KEY, 'q': query, 'to': 100})
    json = response.json()

    print(f'Query: {query} Results: {len(json["hits"])}')

    for hit in json['hits']:
        recipe = hit['recipe']

        if recipe['url'] not in seen:
            seen.add(recipe['url'])
            del recipe['totalNutrients']
            del recipe['totalDaily']
            data['recipes'].append(recipe)


MEAT = ['beef', 'chicken', 'salmon', 'prawn', 'lamb', 'fish', 'pork', 'turkey', 'goose', 'duck', 'tuna', 'steak', 'maskerel']
ADDITIONAL = ['rice', 'pasta', 'bread', 'vegetables', 'fruit', 'eggs', 'cheese', 'potatoes', 'avocado', 'aubergine', 'couscous', 'tofu', 'kale', 'spinach', 'lentil', 'mushroom', 'beetroot', 'leek', 'cauliflower', 'broccoli', 'asparagus']

if __name__ == "__main__":
    with open('data.json', 'r') as file:
        data = json.loads(file.read())
        seen = set()

        for recipe in data['recipes']:
            seen.add(recipe['url'])

    count = 0

    for meat in MEAT:
        if count >= 4:
            break

        for additional in ADDITIONAL:
            search(f'{meat}, {additional}', data, seen)
            count += 1

            if count >= 4:
               break

    with open('data.json', 'w') as file:
        json.dump(data, file)