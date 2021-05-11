from html.parser import HTMLParser


class MLStripper(object, HTMLParser):
    def __init__(self):
        super(MLStripper, self).__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

    @staticmethod
    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

def ngrams(text, n):
    return zip(*[normalize(text).split()[i:] for i in range(n)])

nltk.download('punkt') # if necessary...

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(MLStripper.strip_tags(text).lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]

print(cosine_sim('a little bird', 'a little bird'))
print(cosine_sim('a little bird', 'a little bird chirps'))
print(cosine_sim('a little bird', 'a big dog barks'))


# print(strip_tags("""<p>Deep clone an {@code Object} using serialization.</p>
#
#  <p>This is many times slower than writing clone methods by hand
#  on all objects in your object graph. However, for complex object
#  graphs, or for those that don't support deep cloning this can
#  be a simple alternative implementation. Of course all the objects
#  must be {@code Serializable}.</p>"""))

import spacy
nlp = spacy.load('en')
doc1 = nlp(u'Hello hi there!')
doc2 = nlp(u'Hello hi there!')
doc3 = nlp(u'Hey whatsup?')

print(doc1.similarity(doc2)) # 0.999999954642
print(doc2.similarity(doc3)) # 0.699032527716
print(doc1.similarity(doc3)) # 0.699032527716

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer

vect = TfidfVectorizer(min_df=1)

tfidf = vect.fit_transform(["My name is Ankit",
                             "Ankit name is very famous",
                             "Ankit like his name",
                             "India has a lot of beautiful cities"])

print((tfidf * tfidf.T).A)
