import chardet
from _codecs import encode


def toUnicode(text):
    if isinstance(text, str):
        encoding=chardet.detect(text)['encoding']
        return text.decode(encoding,"ignore")
    return text