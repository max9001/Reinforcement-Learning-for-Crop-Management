from qLearn_helper import *

def move_up(agent_host, x, z):
    new_z = z - 1
    teleport_agent(agent_host, x + 0.5, 227, new_z + 0.5)
    return x, new_z, 0

def move_down(agent_host, x, z):
    new_z = z + 1
    teleport_agent(agent_host, x + 0.5, 227, new_z + 0.5)
    return x, new_z, 0

def move_left(agent_host, x, z):
    new_x = x - 1
    teleport_agent(agent_host, new_x + 0.5, 227, z + 0.5)
    return new_x, z, 0

def move_right(agent_host, x, z):
    new_x = x + 1
    teleport_agent(agent_host, new_x + 0.5, 227, z + 0.5)
    return new_x, z, 0

def harvest(agent_host, x, z):
    age = get_wheat_age_in_los(agent_host)
    if age == 7:
        reward = 1
    elif age >= 0:
        reward = -1
    else:
        reward = 0
    look_down_harvest_and_replant(agent_host)
    return x, z, reward

def plant(agent_host, x, z):
    plant_seed(agent_host)
    return x, z, 0

def wait(agent_host, x, z):
    time.sleep(0.5)
    return x, z, 0



