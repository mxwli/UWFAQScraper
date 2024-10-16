import pandas as pd, gensim, duckdb
from data_preprocessor import DataPreprocessor
import random

# fetch dataset
print("fetching dataset")
dbConnection = duckdb.connect("persistent.duckdb")
qna_master = dbConnection.execute("SELECT question, answer, source FROM qna").df()
print(qna_master.head())
print("------------\n")

# init preprocessor
preprocessor = DataPreprocessor(qna_master['question'] + qna_master['answer'])
randidx = random.randint(0, qna_master.shape[0]-1)
print(f"""sample preprocessing of random element in dataset:
original data at {randidx}:

----------
{qna_master['answer'][randidx]}
----------

processed data:

----------
{preprocessor.full_preprocess(str(qna_master['answer'][randidx]))}
----------

""")

for i in range(qna_master.shape[0]-1):
    question = qna_master['question'][i]
    answer = qna_master['answer'][i]
    q = preprocessor.full_preprocess(question)
    a = preprocessor.full_preprocess(answer)
    if (len(q) == 0):
        print(f"question {question} gives empty processing")
    if (len(a) == 0):
        print(f"answer {answer} gives empty processing")


documents_Q = [gensim.models.doc2vec.TaggedDocument(preprocessor.full_preprocess(str(doc)), [i]) for i,doc in 
    enumerate(qna_master["question"])]
documents_A = [gensim.models.doc2vec.TaggedDocument(preprocessor.full_preprocess(str(doc)), [i]) for i,doc in 
    enumerate(qna_master["answer"])]
documents_QA = [gensim.models.doc2vec.TaggedDocument(preprocessor.full_preprocess(str(doc)), [i]) for i,doc in 
    enumerate(qna_master["question"] + qna_master["answer"])]

print("generating model Q")
# generate model
model_Q = gensim.models.Doc2Vec(documents_Q, vector_size=100, window=4, min_count=1, workers=20, epochs=10, negative=15, sample=1e-5, dm=1)
model_Q.save("models/model_Q_vector_size_100_window_4_min_count_1_workers_20_epochs_10_negative_15_sample_1e-5_dm_1")

print("generating model A")
model_A = gensim.models.Doc2Vec(documents_A, vector_size=100, window=4, min_count=1, workers=20, epochs=10, negative=15, sample=1e-5, dm=1)
model_A.save("models/model_A_vector_size_100_window_4_min_count_1_workers_20_epochs_10_negative_15_sample_1e-5_dm_1")

print("generating model QA")
model_QA = gensim.models.Doc2Vec(documents_QA, vector_size=100, window=4, min_count=1, workers=20, epochs=10, negative=15, sample=1e-5, dm=1)
model_QA.save("models/model_QA_vector_size_100_window_4_min_count_5_workers_20_epochs_10_negative_15_sample_1e-5_dm_1")

print("testing model")
model_Q_index = gensim.similarities.MatrixSimilarity([model_Q.dv[i] for i in range(408)], num_features=100)
# model_A_index = gensim.similarities.MatrixSimilarity(model_A.dv)
# model_QA_index = gensim.similarities.MatrixSimilarity(model_QA.dv)
while True:
    print("enter query")
    query = preprocessor.full_preprocess(input())
    print("processed to " + str(query))
    inferrence = model_Q.infer_vector(query, epochs=100)
    highest = model_Q_index[inferrence].argmax()
    print(qna_master["question"][highest])

