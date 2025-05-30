import numpy as np
import random
from collections import defaultdict

class QLearningAgent:
    def __init__(self, actions_list, alpha=0.1, gamma=0.9, epsilon=0.2, epsilon_decay=0.999, min_epsilon=0.01):
        self.q_table = defaultdict(lambda: np.zeros(len(actions_list)))
        self.alpha = alpha          # Learning rate
        self.gamma = gamma          # Discount factor
        self.epsilon = epsilon        # Exploration rate
        self.epsilon_decay = epsilon_decay # Rate at which epsilon decreases
        self.min_epsilon = min_epsilon   # Minimum exploration rate
        self.actions = actions_list # List of action indices (e.g., [0, 1, 2, 3, 4, 5, 6])

    def choose_action(self, state_tuple):
        if random.random() < self.epsilon:
            return random.choice(self.actions)  # Explore: choose a random action
        else:
            q_values = self.q_table[state_tuple]
            # Exploit: choose the action with the highest Q-value
            # If multiple actions have the same max Q, choose randomly among them
            max_q = np.max(q_values)
            candidates = [action_idx for action_idx, q in enumerate(q_values) if q == max_q]
            return random.choice(candidates) # Return the action index

    def learn(self, state_tuple, action_index, reward, next_state_tuple):
        q_predict = self.q_table[state_tuple][action_index]
        q_target_next_max = np.max(self.q_table[next_state_tuple]) if next_state_tuple is not None else 0
        q_target = reward + self.gamma * q_target_next_max
        self.q_table[state_tuple][action_index] += self.alpha * (q_target - q_predict)

    def decay_epsilon(self):
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay