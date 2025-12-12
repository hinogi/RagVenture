from sentence_transformers import SentenceTransformer, util

# Singleton damit der speicher nicht so schnell ausgeht :)

class _EmbeddingUtils:

    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.util = util

_instance = _EmbeddingUtils()
model = _instance.model
util = _instance.util