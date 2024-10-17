from gensim import corpora
import re

class DataPreprocessor:
    def swapAcronyms(self, tokenizedDocument):
        acronyms = {
            "aif": "admission information form".split(),
            "ipc": "international peer community".split(),
            "elpe": "english language proficiency exam".split(),
            "sin": "social insurance number".split(),
            "flc": "financial literacy competition".split(),
            "iep": "individual education plan".split(),
            "oat": "online academic tools".split(),
            "casper": "computer based assessment sampling personal characteristics".split(),
            "od": "doctor optometry".split(),
            "pd": "professional development".split()
        }
        ret = []
        for token in tokenizedDocument:
            if token in acronyms:
                ret += acronyms[token]
            else:
                ret.append(token)
        return ret

    def tokenize(self, document):
        return re.sub(r'[!"#$%&\'()*+, -./:;<=>?@\[\\\]^_`{|}~]', ' ', document.lower()).split()
    
    def full_preprocess(self, document):
        return list(filter(lambda x: x in self.words, self.swapAcronyms(self.tokenize(document))))
        

    def __init__(self, corpus, file='models/words.dict'):
        if corpus is None:
            self.words = set(map(lambda x: x[:-1], open(file, 'r')))
        else:
            stopwords = set(''.join(open('spaCy_stopwords.txt', 'r')).split())
            texts = [[word for word in self.swapAcronyms(self.tokenize(document)) if word not in stopwords] for document in corpus]
            freq = {}
            for text in texts:
                for word in text:
                    if word not in freq:
                        freq[word] = 1
                    else:
                        freq[word] = freq[word] + 1
            processed_corpus = [[token for token in text if freq[token] > 1 and len(token) > 1] for text in texts]
            dictionary = corpora.Dictionary(processed_corpus)
            self.words = set(dictionary.token2id.keys())
            open(file, 'w').write('\n'.join(self.words))



