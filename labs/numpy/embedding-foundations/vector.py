import numpy as np

"""Calculates the magnitude/length (L2 norm) of a vector."""
def vector_length(v: np.ndarray) -> float:
    return float(np.linalg.norm(v))

"""Scales a vector to have a length of 1 (unit vector)."""
def normalize(v: np.ndarray) -> np.ndarray:
    length = vector_length(v)
    if length == 0:
        return v
    return v / length

"""Computes the dot product of two vectors."""
def dot_product(v1: np.ndarray, v2: np.ndarray) -> float:
    return float(np.dot(v1,v2))


"""Measures the cosine of the angle between two vectors."""
def cosine_similarity(v1: np.ndarray, v2:np.ndarray) -> float:
    len_v1 = vector_length(v1)
    len_v2 = vector_length(v2)
    if len_v1 == 0 or len_v2 == 0:
        return 0.0
    return dot_product(v1, v2) / (len_v1 * len_v2)

"""Calculates the straight-line distance between two points."""
def euclidean_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    return float(np.linalg.norm(v1 - v2))


if __name__ == "__main__":
    v1 = np.array([3.0, 4.0])
    v2 = np.array([1.0, 2.0])

    print("Vector Length of v1:", vector_length(v1))
    print("Normalized v1:", normalize(v1))
    print("Dot Product of v1 and v2:", dot_product(v1, v2))
    print("Cosine Similarity of v1 and v2:", cosine_similarity(v1, v2))
    print("Euclidean Distance between v1 and v2:", euclidean_distance(v1, v2))