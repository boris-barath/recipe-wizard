from google.cloud import vision
import io
import json
import string

home = "/Users/mackopes/"
illegal_characters = set('0123456789%$£€:#')
min_word_length = 3

class IngredientDatabase:
    def __init__(self, path, alphabet = string.ascii_lowercase):
        self.root = dict()
        self.alphabet = alphabet

        with open(path, "r") as ingredients:
            for line in ingredients:
                for word in line.split():
                    self.add(word.lower())
    
    def add(self, word):
        if len(word) < min_word_length or any(c not in self.alphabet for c in word):
            return

        cur = self.root

        for letter in word:
            cur = cur.setdefault(letter, {})
        cur["end"] = "end"

    def contains_substr_of(self, substr):
        for i in range(len(substr)):
            word = substr[i:]
            cur = self.root
            for letter in word:
                if "end" in cur:
                    return True
                elif letter in cur:
                    cur = cur[letter]
                else:
                    continue
        else:
            return False

ingredient_database = IngredientDatabase('ingredients.txt')

# ingredient_database = set([
#     "cola",
#     "coke",
#     "pepsi",
#     "donut",
#     "banana",
#     "tomato",
#     "bread",
#     "pizza",
#     "raspber",
#     "blueber",
#     "avodaco",
#     "oat",
#     "cheese"
#     ])

def detect_ingredients(path):
    """Detects document features in an image."""
    client = vision.ImageAnnotatorClient.from_service_account_json(home + "Desktop/creds-e3262d3bc3f9.json")

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.document_text_detection(image=image)

    all_blocks = [block for page in response.full_text_annotation.pages for block in page.blocks]
    lines = list(set(get_block_with_ingridients(all_blocks)))

    return lines


def connect_words(paragraph, symbols = ".,-"):
    words = []
    concat_word = ""
    for word in paragraph:
        if word in symbols:
            last_word = ""
            if concat_word == "" and len(words) > 0:
                last_word = words[-1]
                words = words[:-1]
            concat_word = concat_word + last_word + word
        else:
            words.append(concat_word + word)
            concat_word = ""
    if concat_word != "":
        words.append(concat_word)

    return words

def possible_line_break(symbol):
    try:
        t = symbol.property.detected_break.type
        if t > 1:
            return "\n"
    except:
        pass
    
    return ""

def get_words(paragraph):
    words = connect_words(
                [''.join([
                    symbol.text for symbol in word.symbols
                ]).lower() + possible_line_break(word.symbols[-1])
                for word in paragraph.words])
    return words

def get_lines(paragraph):
    words = get_words(paragraph)

    lines = []
    line = []
    for word in words:
        new_line = False
        if word[-1] == '\n':
            new_line = True
            word = word[:-1]

        if len(word) < min_word_length or any(c in illegal_characters for c in word):
            word = ""

        if len(word) > 0:
            line.append(word)

        if new_line and len(line) > 0:
            lines.append(line)
            line = []

    return lines

def block_to_lines_generator(block):
    for paragraph in block.paragraphs:
        for line in get_lines(paragraph):
            yield ' '.join(line)

def get_block_with_ingridients(blocks):
    cur_max = 0
    max_lines = []
    for block in blocks:
        lines = list(block_to_lines_generator(block))
        # check if ingredient is in line
        ingredient_count = [has_ingridient(line) for line in lines].count(True)
        if ingredient_count >= cur_max:
            cur_max = ingredient_count
            max_lines = lines

    return max_lines

# def has_ingridient(line):
#     for ingredient in ingredient_database:
#         if ingredient in line:
#             return True
#     return False

def has_ingridient(line):
    return ingredient_database.contains_substr_of(line)

if __name__ == "__main__":
    for line in detect_ingredients(home + "Desktop/image.jpeg"):
        print(line)
