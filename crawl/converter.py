import json

import spacy

if __name__ == "__main__":
    with open('data.json', 'r') as file:
        data = json.loads(file.read())

    nlp = spacy.load('../model/')

    for recipe in data['recipes']:
        del recipe['digest']
        del recipe['ingredientLines']

        for ingredient in recipe['ingredients']:

            doc = nlp(ingredient['text'])

            print(len(doc.ents))
            if len(doc.ents) > 1:
                ingredient['text'] = doc.ents[0].text

    with open('data_out.json', 'w') as file:
        file.write(data)