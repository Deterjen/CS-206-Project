from sentence_transformers import SentenceTransformer


class TextEmbedder:
    def __init__(self, model='all-MiniLM-L6-v2'):
        self.embedding_model = SentenceTransformer(model)

    def encode(self, texts, dimension_size=-1):
        """
        Batch encode texts to embeddings
        Args:
            texts: Either a single string or list of strings
            dimension_size: Size to truncate embeddings to, -1 for full size
        Returns:
            numpy array of embeddings
        """
        embedding = self.embedding_model.encode(texts)
        if dimension_size == -1:
            return embedding
        return embedding[:dimension_size]
