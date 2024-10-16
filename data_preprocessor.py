from gensim import corpora
import re

class DataPreprocessor:
    def swapAcronyms(self, tokenizedDocument):
        acronyms = {
            "aif": "Admission Information Form",
            "ipc": "International Peer Community",
            "elpe": "English Language Proficiency Exam",
            "sin": "Social insurance number",
            "flc": "Financial Literacy Competition",
            "iep": "Individual education plan",
            "oat": "Online Academic Tools",
            "casper": "Computer based Assessment for Sampling Personal Characteristics",
            "od": "Doctor of Optometry"
        }
        ret = []
        for token in tokenizedDocument:
            if token in acronyms:
                ret.append(acronyms[token].lower())
            else:
                ret.append(token)
        return ret

    def tokenize(self, document):
        return re.sub(r'[!"#$%&\'()*+, -./:;<=>?@\[\\\]^_`{|}~]', ' ', document.lower()).split()
    
    def full_preprocess(self, document):
        return list(filter(lambda x: x in self.dictionary.token2id, self.swapAcronyms(self.tokenize(document))))
        

    def __init__(self, corpus, file='models/words.dict'):
        if corpus is None:
            self.dicitonary = corpora.Dicitionary()
            self.dictionary.load(file)
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
            self.dictionary = corpora.Dictionary(processed_corpus)
            self.dictionary.save(file)



