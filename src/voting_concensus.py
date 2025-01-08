import numpy as np
import matplotlib.pyplot as plt


def rank_convergence_with_plot(initial_rankings, max_iterations=100, tolerance=1e-5):
    """
    Simulates the convergence of rankings in a chain of agents and plots the rankings over iterations.

    Parameters:
        initial_rankings (list of lists): Initial rankings for each agent (list of lists).
        max_iterations (int): Maximum number of iterations to prevent infinite loops.
        tolerance (float): Tolerance for determining convergence.

    Returns:
        list: Final consensus ranking for the agents.
    """
    num_agents = len(initial_rankings)
    num_options = len(initial_rankings[0])
    rankings = np.array(initial_rankings, dtype=float)

    # Store rankings for plotting
    rankings_over_time = [rankings.copy()]

    for iteration in range(max_iterations):
        new_rankings = rankings.copy()

        for i in range(num_agents):
            if i == 0:  # First agent, influenced by agent 2
                new_rankings[i] = (rankings[i] + rankings[i + 1]) / 2
            elif i == num_agents - 1:  # Last agent, influenced by agent 2
                new_rankings[i] = (rankings[i] + rankings[i - 1]) / 2
            else:  # Middle agent, influenced by agents 1 and 3
                new_rankings[i] = (rankings[i - 1] + rankings[i] + rankings[i + 1]) / 3

        # Store the updated rankings for plotting
        rankings_over_time.append(new_rankings.copy())

        # Check for convergence
        if np.max(np.abs(new_rankings - rankings)) < tolerance:
            print(f"Converged after {iteration + 1} iterations")
            rankings_over_time = np.array(rankings_over_time)
            plot_rankings(rankings_over_time, num_options)
            return new_rankings.tolist()

        rankings = new_rankings

    print("Max iterations reached without full convergence")
    rankings_over_time = np.array(rankings_over_time)
    plot_rankings(rankings_over_time, num_options)
    return rankings.tolist()


def plot_rankings(rankings_over_time, num_options):
    """
    Plots the rankings of agents over iterations.

    Parameters:
        rankings_over_time (numpy.ndarray): Rankings recorded over iterations.
        num_options (int): Number of options being ranked.
    """
    iterations = rankings_over_time.shape[0]
    num_agents = rankings_over_time.shape[1]

    plt.figure(figsize=(10, 6))
    for agent in range(num_agents):
        for option in range(num_options):
            plt.plot(
                range(iterations),
                rankings_over_time[:, agent, option],
                label=f"Agent {agent + 1}, Option {option + 1}",
                linestyle='--' if agent % 2 == 0 else '-',
                linewidth=1.5
            )

    plt.xlabel("Iterations")
    plt.ylabel("Rank Value")
    plt.title("Agent Rankings Over Iterations")
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Example usage
# Initial rankings for 3 agents with 4 options
initial_rankings = [
    [1, 4, 3, 2],  # Agent 1's initial ranking
    [3, 1, 4, 2],  # Agent 2's initial ranking
    [2, 3, 1, 4],  # Agent 3's initial ranking
]

final_ranking = rank_convergence_with_plot(initial_rankings)
print("Final Consensus Rankings:")
for i, ranking in enumerate(final_ranking, start=1):
    print(f"Agent {i}: {ranking}")
