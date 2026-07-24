import numpy as np

def practice_rehape() -> np.ndarray:
    arr = np.arange(12)
    reshaped = arr.reshape(3,4)
    return reshaped

def practice_transpose(matrix: np.ndarray) -> np.ndarray:
    return matrix.T

def practice_matmul(matrix_A: np.ndarray, matrix_B: np.ndarray) -> np.ndarray:
    return matrix_A @ matrix_B

def practice_identity(size: int) -> np.ndarray:
    return np.eye(size)

def practice_inverse(matrix: np.ndarray) -> np.ndarray:
    return np.linalg.inv(matrix)

def practice_broadcasting(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    return matrix + vector

if __name__ == "__main__":

    print("Practice Reshape:\n", practice_rehape())
    print("\nPractice Transpose:\n", practice_transpose(np.array([[1, 2], [3, 4], [5, 6]])))
    print("\nPractice Matrix Multiplication:\n", practice_matmul(np.array([[1, 2], [3, 4]]), np.array([[5, 6, 7], [8, 9, 10]])))
    print("\nPractice Identity Matrix:\n", practice_identity(3))
    print("\nPractice Inverse:\n", practice_inverse(np.array([[4, 7], [2, 6]])))
    print("\nPractice Broadcasting:\n", practice_broadcasting(np.array([[10, 20, 30], [40, 50, 60]]), np.array([1,2,3])))