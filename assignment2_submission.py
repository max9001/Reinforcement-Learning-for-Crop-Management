import random

# state space
# at most odie can have 3 items

# odie can have the empty set
# odie can have only one item ('pumpkin:1', 'sugar:1', 'egg:1', 'pumpkin_seeds:4', 'pumpkin_pie')
# odie can have two items ('pumpkin:1', 'sugar:1', 'egg:1', 'pumpkin_seeds:4')
    # combination of pumpkin, pumpkinseeds is IMPOSSIBLE so -1 from this calculation
    # double egg is a possibility so add +1 
    # option to craft pumpkin pie, so pumpkin pie and second egg are possible, so add +1
# odie can have three items ('pumpkin:1', 'sugar:1', 'egg:1', 'pumpkin_seeds:4')
    # combination of pumpkin, pumpkinseeds is IMPOSSIBLE so -1 from this calculation
    # 2 eggs available, so double egg + a third item is possible. add 3

# 1 + 5 + (4C2 -1 + 1 + 1) + (4C3 - 1 + 3) = 19

# state space pt 2
# at most odie can have 3 items

# odie can have the empty set
# odie can have only one item ('pumpkin:1', 'sugar:1', 'egg:1', 'pumpkin_seeds:4', 'pumpkin_pie', 'red_mushroom', 'planks', 'mushroom_stew', 'bowl')
# odie can have two items ('pumpkin:1', 'sugar:1', 'egg:1', 'pumpkin_seeds:4', 'red_mushroom', 'planks')
    # combination of pumpkin, pumpkinseeds is IMPOSSIBLE so -1 from this calculation
    # double egg is a possibility so add +1 
    # option to craft pumpkin pie, so pumpkin pie + second egg, red mushroom, planks, bowl, mushroom stew are possible, so add +5
    # option to craft bowl, so bowl + pumkin, sugar, egg, seeds, red mushroom, planks are pssobile, so add +6
    # option to craft mushroom stew, ao stew + pumkin, sugar, egg, seeds so add +4
# odie can have three items ('pumpkin:1', 'sugar:1', 'egg:1', 'pumpkin_seeds:4', 'red_mushroom', 'planks')
    # combination of pumpkin, pumpkinseeds is IMPOSSIBLE so -1 from this calculation
    # 2 eggs available, so double egg + a third item is possible. add 5. same case for planks add 5

# 1 + 5 + (6C2 -1 + 1 + 5 + 6 + 4) + (6C3 - 1 + 5 + 5) = 65

# items=['pumpkin', 'sugar', 'egg', 'egg', 'red_mushroom', 'planks', 'planks']
items=['pumpkin', 'sugar', 'egg', 'egg']

food_recipes = {'pumpkin_pie': ['pumpkin', 'egg', 'sugar'],
                'pumpkin_seeds': ['pumpkin'],
                'bowl': ['planks', 'planks'],
                'mushroom_stew': ['bowl', 'red_mushroom']}

# rewards_map = {'pumpkin': 5, 
#                'egg': 5, 
#                'sugar': 5,
#                'pumpkin_pie': 100, 
#                'pumpkin_seeds': -50,
#                'red_mushroom': 5,
#                'planks': 5,
#                'bowl': 50,
#                'mushroom_stew': 100}

rewards_map = {'pumpkin': -5, 'egg': -25, 'sugar': -10,
               'pumpkin_pie': 100, 'pumpkin_seeds': -50,
               'red_mushroom': 5, 'planks': 5, 
               'bowl': 1, 'mushroom_stew': 100}

def is_solution(reward):
    return reward == 105

def get_curr_state(items):
    return tuple(sorted(items))

def choose_action(curr_state, possible_actions, eps, q_table):
    rnd = random.random()
    
    # return a random action with probaility eps
    if (rnd < eps):       
        a = random.randint(0, len(possible_actions) - 1)
        return possible_actions[a]
    
    # probaility 1-eps it picks the action with the highest Q-value
    else:
        valid_q_values = {}
        q_values_for_state = q_table[curr_state].items()
        
        for action, q_value in q_values_for_state:
            if action in possible_actions:
                valid_q_values[action] = q_value

        return max(valid_q_values, key=valid_q_values.get)

