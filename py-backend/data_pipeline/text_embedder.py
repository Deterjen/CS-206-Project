from sentence_transformers import SentenceTransformer


class TextEmbedder:
    def __init__(self, model='all-MiniLM-L6-v2'):
        self.embedding_model = SentenceTransformer(model)

    def encode(self, text, dimension_size=-1):
        embedding = self.embedding_model.encode(text)
        if dimension_size == -1:
            return embedding
        return embedding[:dimension_size]
