import numpy as np
import matplotlib.pyplot as plt

# Parameters
num_agents = 20  # Number of agents
num_iterations = 50  # Number of iterations
connectivity_prob = 0.7  # Probability of connection between agents

# Generate random network topology (adjacency matrix)
adj_matrix = np.random.rand(num_agents, num_agents) < connectivity_prob
adj_matrix = np.triu(adj_matrix, 1)  # Upper triangular to avoid double counting
adj_matrix = adj_matrix + adj_matrix.T  # Make symmetric
np.fill_diagonal(adj_matrix, 0)  # Remove self-loops

# Normalize adjacency matrix (degree-normalized Laplacian)
degree_matrix = np.diag(adj_matrix.sum(axis=1))
laplacian = degree_matrix - adj_matrix
normalized_matrix = np.eye(num_agents) - np.linalg.pinv(degree_matrix) @ laplacian

# Initialize agent values randomly
values = np.random.rand(num_agents)
history = np.zeros((num_agents, num_iterations))  # Store value history
history[:, 0] = values

# Display initial values
print("Initial values:")
print(values)

# Consensus process
for t in range(1, num_iterations):
    # Update values based on neighbors
    values = normalized_matrix @ values
    history[:, t] = values

# Display final values
print("Final values (consensus reached):")
print(values)

# Plot value evolution
plt.plot(history.T)
plt.xlabel("Iteration")
plt.ylabel("Value")
plt.title("Decentralized Consensus of Continuous Variable")
plt.show()
