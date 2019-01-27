#!/usr/bin/env python
# coding: utf8
"""Example of training an additional entity type

This script shows how to add a new entity type to an existing pre-trained NER
model. To keep the example short and simple, only four sentences are provided
as examples. In practice, you'll need many more — a few hundred would be a
good start. You will also likely need to mix in examples of other entity
types, which might be obtained by running the entity recognizer over unlabelled
sentences, and adding their annotations to the training set.

The actual training is performed by looping over the examples, and calling
`nlp.entity.update()`. The `update()` method steps through the words of the
input. At each word, it makes a prediction. It then consults the annotations
provided on the GoldParse instance, to see whether it was right. If it was
wrong, it adjusts its weights so that the correct action will score higher
next time.

After training your model, you can save it to a directory. We recommend
wrapping models as Python packages, for ease of deployment.

For more details, see the documentation:
* Training: https://spacy.io/usage/training
* NER: https://spacy.io/usage/linguistic-features#named-entities

Compatible with: spaCy v2.0.0+
"""
from __future__ import unicode_literals, print_function

import csv

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding


# new entity label
LABEL = 'INGREDIENT'

# training data
# Note: If you're using an existing model, make sure to mix in examples of
# other entity types that spaCy correctly recognized before. Otherwise, your
# model might learn the new type, but "forget" what it previously knew.
# # https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting
# TRAIN_DATA = [
#     ("Horses are too tall and they pretend to care about your feelings", {
#         'entities': [(0, 6, 'INGREDIENT')]
#     }),
#
#     ("Do they bite?", {
#         'entities': []
#     }),
#
#     ("horses are too tall and they pretend to care about your feelings", {
#         'entities': [(0, 6, 'INGREDIENT')]
#     }),
#
#     ("horses pretend to care about your feelings", {
#         'entities': [(0, 6, 'INGREDIENT')]
#     }),
#
#     ("they pretend to care about your feelings, those horses", {
#         'entities': [(48, 54, 'INGREDIENT')]
#     }),
#
#     ("horses?", {
#         'entities': [(0, 6, 'INGREDIENT')]
#     })
# ]

DATA = []

with open('trainer/nyt-ingredients-snapshot-2015.csv', 'r', encoding="utf8") as file:
    content = csv.reader(file)
    count = 0

    for row in content:
        count += 1

        if count == 1:
            continue

        start = row[1].find(row[2])
        length = len(row[2])

        if length == 0 or start == -1:
            continue

        DATA.append((row[1], {'entities': [(start, start + length, 'INGREDIENT')]}))

random.shuffle(DATA)
TRAIN_DATA = DATA[:int(len(DATA) * 0.8)]
TEST_DATA = DATA[int(len(DATA) * 0.8):]

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))
def main(model=None, new_model_name='animal', output_dir=None, n_iter=10):
    """Set up the pipeline and entity recognizer, and train the new entity."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')  # create blank Language class
        print("Created blank 'en' model")
    # Add entity recognizer to model if it's not in the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    # otherwise, get it, so we can add labels to it
    else:
        ner = nlp.get_pipe('ner')

    ner.add_label(LABEL)   # add new entity label to entity recognizer
    if model is None:
        optimizer = nlp.begin_training()
    else:
        # Note that 'begin_training' initializes the models, so it'll zero out
        # existing entity types.
        optimizer = nlp.entity.create_optimizer()

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35,
                           losses=losses)

            total = 0
            correct = 0

            # test the trained model
            for data in TEST_DATA:
                test_text = data[0]
                doc = nlp(test_text)

                total += 1

                for ent in doc.ents:
                    start = data[1]['entities'][0][0]
                    end = data[1]['entities'][0][1]

                    if ent.label_ == 'INGREDIENT' and ent.text == data[0][start:end]:
                        correct += 1
                        break

            print(f'Losses: {losses} Accuracy: {correct / total}')

            # save model to output directory
            if output_dir is not None:
                output_dir = Path(output_dir)
                if not output_dir.exists():
                    output_dir.mkdir()
                nlp.meta['name'] = new_model_name  # rename model
                nlp.to_disk(output_dir)


if __name__ == '__main__':
    plac.call(main)