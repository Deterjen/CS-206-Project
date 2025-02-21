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
            If input is single string: numpy array of embedding
            If input is list: numpy array of embeddings
        """
        # Handle single text case
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        else:
            single_input = False

        # Generate embeddings in batch
        embeddings = self.embedding_model.encode(texts)

        # Truncate if needed
        if dimension_size > 0:
            embeddings = embeddings[:, :dimension_size]

        # Return single embedding for single input
        if single_input:
            return embeddings[0]
        return embeddings
