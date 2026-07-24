import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

corpus = [
     "Apple is a fruit.",
    "Orange is a fruit.",
    "BMW makes cars.",
    "Tesla builds EVs.",
    "Python is a language.",
    "Swift is a language."
]

def search_similar_sentences(query: str, top_k: int = 3):
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), lowercase=True)
    corpus_embeddings = vectorizer.fit_transform(corpus)
    query_embedding = vectorizer.transform([query])
    similarities = cosine_similarity(query_embedding, corpus_embeddings).flatten()
    ranked_indices = np.argsort(similarities)[::-1]

    print(f"Query: '{query}'")
    print("-" * 50)
    for i in range(top_k):
        index = ranked_indices[i]
        score = similarities[index]
        print(f"rank {i+1}: Score = {score:.4f} | {corpus[index]}")
        print("\n")

if __name__ == "__main__":

    search_similar_sentences(query= "electric car", top_k=4)
    search_similar_sentences(query= "programming syntax", top_k=2)
    