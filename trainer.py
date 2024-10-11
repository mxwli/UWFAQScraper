import pandas as pd, gensim, duckdb

# fetch dataset
print("fetching dataest")
dbConnection = duckdb.connect("persistent.duckdb")
qna_master = dbConnection.execute("SELECT question, answer, source FROM qna").df()
print(qna_master.head())
print("------------\n")

documents_Q = [gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(str(doc)), [i]) for i,doc in 
    enumerate(qna_master["question"])]
documents_A = [gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(str(doc)), [i]) for i,doc in 
    enumerate(qna_master["answer"])]
documents_QA = [gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(str(doc)), [i]) for i,doc in 
    enumerate(qna_master["question"] + qna_master["answer"])]

print("generating model Q")
# generate model
model_Q = gensim.models.Doc2Vec(documents_Q, vector_size=100, window=8, min_count=5, workers=20, epochs=17, negative=15, sample=1e-5)
model_Q.save("models/model_Q_vector_size_100_window_8_min_count_5_workers_20_epochs_17_negative_15_sample_1e-5")

print("generating model A")
model_A = gensim.models.Doc2Vec(documents_A, vector_size=100, window=8, min_count=5, workers=20, epochs=17, negative=15, sample=1e-5)
model_A.save("models/model_A_vector_size_100_window_8_min_count_5_workers_20_epochs_17_negative_15_sample_1e-5")

print("generating model QA")
model_QA = gensim.models.Doc2Vec(documents_QA, vector_size=100, window=8, min_count=5, workers=20, epochs=17, negative=15, sample=1e-5)
model_QA.save("models/model_QA_vector_size_100_window_8_min_count_5_workers_20_epochs_17_negative_15_sample_1e-5")

