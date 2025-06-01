# q_agent.py
import numpy as np
import random
from collections import defaultdict
import pickle
import os

class QLearningAgent:
    def __init__(self, actions_list, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.q_table = defaultdict(lambda: np.zeros(len(actions_list)))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.actions = actions_list

    def choose_action(self, state_tuple):
        # ... (choose_action logic remains the same) ...
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            q_values = self.q_table[state_tuple]
            if np.all(q_values == 0):
                 return random.choice(self.actions)
            max_q = np.max(q_values)
            candidates_indices = [i for i, q_val in enumerate(q_values) if q_val == max_q]
            return random.choice(candidates_indices)

    def learn(self, state_tuple, action_index, reward, next_state_tuple):
        # ... (learn logic remains the same) ...
        q_predict = self.q_table[state_tuple][action_index]
        q_target = reward + self.gamma * np.max(self.q_table[next_state_tuple])
        self.q_table[state_tuple][action_index] += self.alpha * (q_target - q_predict)

    def decay_epsilon(self):
        # ... (decay_epsilon logic remains the same) ...
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay
        else:
            self.epsilon = self.min_epsilon

    def save_training_state(self, filename, episode_num, ep_rewards, ep_wheat_collected):
        """Saves the Q-table, current epsilon, episode number, and tracking lists."""
        data_to_save = {
            'q_table': dict(self.q_table),
            'epsilon': self.epsilon,
            'last_episode_completed': episode_num,
            'episode_rewards_history': ep_rewards,
            'episode_wheat_collected_history': ep_wheat_collected
            # You could also save alpha, gamma if you plan to change them and resume
        }
        try:
            with open(filename, 'wb') as f:
                pickle.dump(data_to_save, f)
            print("INFO: Training state (Q-table, epsilon, episode {}, reward/wheat history) saved to {}".format(episode_num + 1, filename))
        except Exception as e:
            print("ERROR: Could not save training state - {}".format(e))

    def load_training_state(self, filename):
        """
        Loads the Q-table, epsilon, last completed episode, and tracking lists.
        Returns:
            tuple: (last_episode_completed, episode_rewards_history, episode_wheat_collected_history)
                   Returns (0, [], []) if file not found or error.
        """
        if os.path.exists(filename):
            try:
                with open(filename, 'rb') as f:
                    data_loaded = pickle.load(f)
                    self.q_table = defaultdict(lambda: np.zeros(len(self.actions)), data_loaded['q_table'])
                    self.epsilon = data_loaded.get('epsilon', self.epsilon)
                    last_episode = data_loaded.get('last_episode_completed', -1) # -1 so next episode is 0
                    rewards_history = data_loaded.get('episode_rewards_history', [])
                    wheat_history = data_loaded.get('episode_wheat_collected_history', [])
                print("INFO: Training state loaded from {}. Resuming from episode {}.".format(filename, last_episode + 2))
                # last_episode is 0-indexed, so we resume from last_episode + 1
                return last_episode + 1, rewards_history, wheat_history 
            except Exception as e:
                print("ERROR: Could not load training state from {} - {}. Starting fresh.".format(filename, e))
                return 0, [], [] # Start from episode 0, empty histories
        else:
            print("INFO: No training state file found at {}. Starting fresh.".format(filename))
            return 0, [], [] # Start from episode 0, empty histories