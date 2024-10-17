
class MeanInference:
    def __init__(self, model, vector_size):
        self.wv = model.wv
        self.vector_size = vector_size

    def infer_vector(self, doc):
        A = [0.0] * self.vector_size
        for i in doc:
            n = self.wv[i]
            A = map(lambda x: x[0] + x[1], zip(A, n))
        return list(map(lambda x: x / len(doc), A))


