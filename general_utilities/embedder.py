# general_utilities/embedder.py

import requests
import json
import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_distances, cosine_similarity
from sklearn.decomposition import PCA

class TextEmbedder:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer('sentence-transformers/msmarco-distilbert-base-v4')
        return cls._model

    @classmethod
    def embed(cls, text):
        """
        Embed a given text or list of texts using the SentenceTransformer model.

        :param text: The text or list of texts to be embedded.
        :return: The embedding vector(s) of the text(s).
        """
        model = cls.get_model()
        if isinstance(text, list):
            return model.encode(text)
        else:
            return model.encode([text])

    @staticmethod
    def co_sim(question_vector, list_of_vectors):
        """
        Compute the cosine similarities between a question vector and a list of vectors.

        :param question_vector: The question vector.
        :param list_of_vectors: The list of vectors.
        :return: The cosine similarities.
        """
        return cosine_similarity([question_vector], list_of_vectors)

    @staticmethod
    def compare(vector1, vector2):
        """
        Compare two embedding vectors using cosine distance.

        :param vector1: The first embedding vector.
        :param vector2: The second embedding vector.
        :return: The cosine distance between the two vectors.
        """
        return cosine_distances([vector1], [vector2])[0][0]

    @staticmethod
    def reduce(vector_list, n_components=2):
        """
        Reduce the dimensionality of a list of vectors using PCA.

        :param vector_list: List of embedding vectors.
        :param n_components: Number of dimensions to reduce to.
        :return: The reduced vectors.
        """
        if len(vector_list) == 1 or len(vector_list[0]) <= n_components:
            return vector_list  # Return the original vectors if PCA cannot be applied
        pca = PCA(n_components=n_components)
        return pca.fit_transform(vector_list)

    @classmethod
    def find_most_similar(cls, question, df):
        """
        Find the most similar vector in the DataFrame to the given question.

        :param question: The question to compare.
        :param df: The DataFrame containing vectors to compare against.
        :return: The row in the DataFrame that contains the most similar vector.
        """
        # Embed the question
        question_vector = cls.embed(question)
        # Reduce the question vector to 2 dimensions
        question_vector_reduced = cls.reduce(question_vector, n_components=2)[0]
        # Calculate cosine similarity
        df['similarity'] = df['vector'].apply(lambda x: cosine_similarity([question_vector_reduced], [x])[0][0])
        # Find the most similar vector
        most_similar_index = df['similarity'].idxmax()
        return df.loc[most_similar_index]

    @staticmethod
    def find_closest(vector, vector_list):
        """
        Find the vector in the list that is closest to the given vector based on cosine distance.

        :param vector: The vector to compare.
        :param vector_list: The list of vectors to search.
        :return: The index of the closest vector in the list and the distance.
        """
        distances = cosine_distances([vector], vector_list)[0]
        min_index = distances.argmin()
        return min_index, distances[min_index]

    @classmethod
    def embed_soup(cls, soup_text):
        """
        Embed the full soup text.

        :param soup_text: The soup text to be embedded.
        :return: The embedding vector of the soup text.
        """
        return cls.embed(soup_text)

    @classmethod
    def embed_link(cls, url, names):
        """
        Embed the URL and list of names for links.

        :param url: The URL of the link.
        :param names: The list of names (anchor texts) of the link.
        :return: The embedding vector of the link.
        """
        text_to_embed = url + " " + " ".join(names)
        return cls.embed(text_to_embed)

    @classmethod
    def embed_form(cls, form_text):
        """
        Embed the form text.

        :param form_text: The form text to be embedded.
        :return: The embedding vector of the form text.
        """
        return cls.embed(form_text)
