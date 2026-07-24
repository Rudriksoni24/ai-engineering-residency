import torch

zeros_pt = torch.zeros(2, 3)
ons_pt = torch.ones(2, 3)
eye_pt = torch.eye(3)
print(zeros_pt)
print(ons_pt)
print(eye_pt)

x = torch.arange(1, 7)
x_reshaped = x.reshape(2, 3)
print(x_reshaped)

matrix = torch.tensor([[1, 2, 3], [4, 5, 6]])
transposed_matrix = matrix.t()
print(transposed_matrix)

tensor_a = torch.tensor([[1, 2], [3, 4]])
tensor_b = torch.tensor([[5, 6], [7, 8]])
matrix_product = torch.matmul(tensor_a, tensor_b)
matrix_product_alt = tensor_a @ tensor_b
print(matrix_product)
print(matrix_product_alt)

x = torch.tensor([3.0], requires_grad=True)
print(x)
y = x ** 2 + 4
y.backward()
print(y)
print(x.grad)
