import numpy as np
import random
from collections import defaultdict

class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = defaultdict(lambda: np.zeros(len(actions)))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.actions = actions

    def choose_action(self, state):
        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        q_values = self.q_table[state]
        max_q = np.max(q_values)
        # If multiple actions have the same max Q, choose randomly among them
        candidates = [action for action, q in enumerate(q_values) if q == max_q]
        return self.actions[random.choice(candidates)]

    def learn(self, state, action, reward, next_state):
        # Q-learning update
        q_predict = self.q_table[state][action]
        q_target = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[state][action] += self.alpha * (q_target - q_predict)