from google.cloud import vision
import io
import json

home = "/Users/mackopes/"

def detect_document(path):
    """Detects document features in an image."""
    client = vision.ImageAnnotatorClient.from_service_account_json(home + "Desktop/creds-e3262d3bc3f9.json")

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                for line in get_lines(paragraph):
                    print(' '. join(line))

            print('############ end of block ##############')

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
                ]) + possible_line_break(word.symbols[-1])
                for word in paragraph.words])
    return words

def get_lines(paragraph):
    illegal_characters = set('0123456789%$£€:#')

    words = get_words(paragraph)

    lines = []
    line = []
    for word in words:
        new_line = False
        if word[-1] == '\n':
            new_line = True
            word = word[:-1]

        if any(c in illegal_characters for c in word):
            word = ""

        if len(word) > 0:
            line.append(word)

        if new_line and len(line) > 0:
            lines.append(line)
            line = []

    return lines
        
if __name__ == "__main__":
    detect_document(home + "Desktop/IMG_1764.JPG")
