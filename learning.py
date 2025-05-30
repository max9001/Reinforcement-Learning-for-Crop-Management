# import sys
# sys.path.append("/usr/local/lib/python3.5/dist-packages/malmo/") 

#--------------------------------------------------------------------------

# import malmo.MalmoPython as MalmoPython # <<< IMPORTANT: Change to import MalmoPython if not using Docker

import MalmoPython  # <<< IMPORTANT: Change to import MalmoPython if not using Docker
import os
import sys # <<< IMPORTANT: Ensure this is imported
import random
import time
import json
from qLearn_helper import *
from q_agent import QLearningAgent

# <InventoryItem slot="0" type="dye" quantity="64" colour="WHITE"/>

# <AgentQuitFromCollectingItem>
#     <Item type="wheat" description="Success! Collected the wheat."/>
# </AgentQuitFromCollectingItem>







mission_xml = '''
<?xml version="1.0" encoding="UTF-8" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <About>
        <Summary>Frank's Test - Step 2</Summary>
    </About>
    <ModSettings>
        <MsPerTick>1</MsPerTick>
    </ModSettings>
    <ServerSection>
        <ServerInitialConditions>
            <Time><StartTime>6000</StartTime><AllowPassageOfTime>false</AllowPassageOfTime></Time>
            <Weather>clear</Weather>
            <AllowSpawning>false</AllowSpawning>
        </ServerInitialConditions>
        <ServerHandlers>
            <FlatWorldGenerator generatorString="3;7,225*minecraft:dirt,minecraft:farmland;1;" />
            <DrawingDecorator>
                <!-- Draw wheats -->
                <DrawBlock x="-1" y="227" z="-6" type="wheat"/>
                <DrawBlock x="-1" y="227" z="-5" type="wheat"/>
                <DrawBlock x="-1" y="227" z="-4" type="wheat"/>
                <DrawBlock x="-1" y="227" z="-3" type="wheat"/>
                <DrawBlock x="-1" y="227" z="-2" type="wheat"/>
                <DrawBlock x="-1" y="227" z="-1" type="wheat"/>
                <DrawBlock x="-1" y="227" z="0" type="wheat"/>

                <DrawBlock x="-2" y="227" z="-6" type="wheat"/>
                <DrawBlock x="-2" y="227" z="-5" type="wheat"/>
                <DrawBlock x="-2" y="227" z="-4" type="wheat"/>
                <DrawBlock x="-2" y="227" z="-3" type="wheat"/>
                <DrawBlock x="-2" y="227" z="-2" type="wheat"/>
                <DrawBlock x="-2" y="227" z="-1" type="wheat"/>
                <DrawBlock x="-2" y="227" z="0" type="wheat"/>

                <DrawBlock x="-3" y="227" z="-6" type="wheat"/>
                <DrawBlock x="-3" y="227" z="-5" type="wheat"/>
                <DrawBlock x="-3" y="227" z="-4" type="wheat"/>
                <DrawBlock x="-3" y="227" z="-3" type="wheat"/>
                <DrawBlock x="-3" y="227" z="-2" type="wheat"/>
                <DrawBlock x="-3" y="227" z="-1" type="wheat"/>
                <DrawBlock x="-3" y="227" z="0" type="wheat"/>

                <DrawBlock x="0" y="227" z="-6" type="wheat"/>
                <DrawBlock x="0" y="227" z="-5" type="wheat"/>
                <DrawBlock x="0" y="227" z="-4" type="wheat"/>
                <!--           skip 0,-3 for watr          -->
                <DrawBlock x="0" y="227" z="-2" type="wheat"/>
                <DrawBlock x="0" y="227" z="-1" type="wheat"/>
                <DrawBlock x="0" y="227" z="-0" type="wheat"/>


                <DrawBlock x="1" y="227" z="-6" type="wheat"/>
                <DrawBlock x="1" y="227" z="-5" type="wheat"/>
                <DrawBlock x="1" y="227" z="-4" type="wheat"/>
                <DrawBlock x="1" y="227" z="-3" type="wheat"/>
                <DrawBlock x="1" y="227" z="-2" type="wheat"/>
                <DrawBlock x="1" y="227" z="-1" type="wheat"/>
                <DrawBlock x="1" y="227" z="0" type="wheat"/>

                <DrawBlock x="2" y="227" z="-6" type="wheat"/>
                <DrawBlock x="2" y="227" z="-5" type="wheat"/>
                <DrawBlock x="2" y="227" z="-4" type="wheat"/>
                <DrawBlock x="2" y="227" z="-3" type="wheat"/>
                <DrawBlock x="2" y="227" z="-2" type="wheat"/>
                <DrawBlock x="2" y="227" z="-1" type="wheat"/>
                <DrawBlock x="2" y="227" z="0" type="wheat"/>

                <DrawBlock x="3" y="227" z="-6" type="wheat"/>
                <DrawBlock x="3" y="227" z="-5" type="wheat"/>
                <DrawBlock x="3" y="227" z="-4" type="wheat"/>
                <DrawBlock x="3" y="227" z="-3" type="wheat"/>
                <DrawBlock x="3" y="227" z="-2" type="wheat"/>
                <DrawBlock x="3" y="227" z="-1" type="wheat"/>
                <DrawBlock x="3" y="227" z="0" type="wheat"/>



                <!-- Draw water to keep wheat alive-->
                <DrawBlock x="0" y="226" z="-3" type="water" />
            </DrawingDecorator>
            <ServerQuitWhenAnyAgentFinishes />
        </ServerHandlers>
    </ServerSection>
    <AgentSection mode="Survival">
        <Name>Frank</Name>
        <AgentStart>
            <Placement x="0.5" y="227.0" z="3.5" yaw="180" />
            <Inventory>

                <InventoryItem slot="0" type="wheat_seeds" quantity="64"/> 

            </Inventory>
        </AgentStart>
        <AgentHandlers>
            <ContinuousMovementCommands turnSpeedDegs="180"/> 
            <DiscreteMovementCommands />
            <InventoryCommands />
            <AbsoluteMovementCommands/>

            <AgentQuitFromTimeUp timeLimitMs="100000000" description="Mission Ended (Time Up)."/>
            <ObservationFromGrid>
                <Grid name="wheatField">
                    <min x="-3" y="225" z="-6"/>
                    <max x="3" y="229" z="0"/>
                </Grid>
            </ObservationFromGrid>
            <ObservationFromRay />
            <ObservationFromFullInventory/>
        </AgentHandlers>
    </AgentSection>
</Mission>
'''

# --- Agent Setup ---
agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse(sys.argv) # sys.argv needs 'import sys'
except RuntimeError as e:
    print('ERROR parsing arguments:', e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

# --- Setup ClientPool ---
# This is generally more robust for starting missions
my_client_pool = MalmoPython.ClientPool()
my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000)) # Default Malmo port

my_mission = MalmoPython.MissionSpec(mission_xml, True)
my_mission_record = MalmoPython.MissionRecordSpec()

max_retries = 3
for retry in range(max_retries):
    try:
        # Attempt to start the mission using the client pool:
        # The last parameter (0) is the experiment_id, unique for each agent if running multiple.
        # The last string ("Frank_experiment") is a unique role ID for this agent in this experiment.
        agent_host.startMission(my_mission, my_client_pool, my_mission_record, 0, "Frank_Wheat_Collector_Role")
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:", e)
            print("*********")
            print("Most likely incorrect formatting in your XML section -Max")
            print("*********")
            exit(1)
        else:
            print("Retry starting mission in 2 seconds...")
            time.sleep(2)

print("Waiting for the mission to start", end=' ')
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors: # Check for errors reported by Malmo
        print("\nERROR during mission start:", error.text)
        # If there are errors here, it often means an XML issue or client connection problem
print("\nMission started!")

# --- Agent Action Sequence ---
# while agent_host.getWorldState().is_mission_running:
#random_method(agent_host)       

    # iteration_method(agent_host)

#wait_10mins_method(agent_host)

# --- RL Setup ---
# Define your action space (index to method)

# ACTIONS = [
#     "move_up",
#     "move_down",
#     "move_left",
#     "move_right",
#     "harvest",      # equals attack
#     "plant",
#     "wait"          # waiting for maturity
# ]




# --- RL Training Loop ---
# Assuming agent_host is initialized and mission is started
# Assuming record_initial_mission_time() has been called

num_episodes = 1000  # Increase significantly for real training
max_steps_per_episode = 100 # Max actions per episode

# Initialize Q-learning agent
q_agent = QLearningAgent(
    actions_list=list(range(len(ACTIONS_LIST))), # Pass indices [0, 1, ..., 6]
    alpha=0.1,      # Learning rate
    gamma=0.9,      # Discount factor for future rewards
    epsilon=1.0,    # Initial exploration rate (start high)
    epsilon_decay=0.999, # Decay epsilon slowly
    min_epsilon=0.05   # Minimum exploration rate
)

# For tracking rewards
episode_rewards = []

# Ensure VALID_FARM_COORDINATES and ILLEGAL_COORD_MARKER are defined
# Ensure helper functions like get_state_active_scan_5_points, teleport_agent are defined/imported

# Starting position for episodes (can be randomized within VALID_FARM_COORDINATES)
initial_farm_spots = list(VALID_FARM_COORDINATES)


for episode in range(num_episodes):
    # Reset agent to a random valid starting spot for each episode
    start_x, start_z = random.choice(initial_farm_spots)
    teleport_agent(agent_host, start_x + 0.5, 227.0, start_z + 0.5)
    time.sleep(0.2) # Settle after teleport

    current_x, current_z = start_x, start_z
    current_cumulative_reward = 0
    
    # Get initial state
    # Important: ensure agent looks down before get_state if it relies on LineOfSight for current spot
    # agent_host.sendCommand("setPitch 90") 
    # time.sleep(0.1)
    current_state = get_state_active_scan_5_points(agent_host, current_x, current_z)
    # agent_host.sendCommand("setPitch 0") # Look forward again, or manage pitch within step/actions
    # time.sleep(0.1)

    print("--- Episode: {} ---".format(episode + 1))
    print("Initial state at ({}, {}):".format(current_x, current_z))
    print_intuitive_state_5_points(current_state)


    for step_num in range(max_steps_per_episode):
        if not agent_host.getWorldState().is_mission_running:
            print("Mission ended prematurely in episode {} at step {}.".format(episode + 1, step_num))
            break

        action_idx = q_agent.choose_action(current_state)
        
        # Execute action, get next position and reward
        # Pass agent_host to the step function
        (next_x, next_z), reward = step(agent_host, action_idx, current_x, current_z, current_state) # ADD agent_host HERE
        current_cumulative_reward += reward
        
        # Get the state for the new position
        next_state = get_state_active_scan_5_points(agent_host, next_x, next_z) # Already passing agent_host here

        # Agent learns
        q_agent.learn(current_state, action_idx, reward, next_state)

        # Update for next iteration
        current_state = next_state
        current_x, current_z = next_x, next_z

        # Print status (can be made less verbose for long training)
        print("Ep {}, Step {}: Agent at ({},{}), Action: {}, Reward: {:.2f}, TotalEpReward: {:.2f}, Epsilon: {:.3f}".format(
            episode + 1, step_num + 1, current_x, current_z, ACTION_NAMES[action_idx], reward, current_cumulative_reward, q_agent.epsilon
        ))
        # print_intuitive_state_5_points(current_state) # Optional: print state every step

        # Small delay for game to process, can be adjusted
        # MsPerTick=1 is very fast, so this sleep might be many game ticks.
        time.sleep(0.05) 

    episode_rewards.append(current_cumulative_reward)
    q_agent.decay_epsilon() # Decay epsilon at the end of each episode
    print("End of Episode {}. Total Reward: {:.2f}. Epsilon: {:.3f}".format(episode + 1, current_cumulative_reward, q_agent.epsilon))
    # Optional: Save Q-table periodically
    # if (episode + 1) % 100 == 0:
    #     save_q_table(q_agent.q_table, "q_table_episode_{}.pkl".format(episode + 1))


print("\n--- Training Complete ---")
# print("Episode rewards:", episode_rewards)
# You can plot episode_rewards to see learning progress.
# You might want to save the final Q-table here.

# Make sure mission ends if it hasn't already (e.g. if AgentQuitFromTimeUp is very long)
if agent_host.getWorldState().is_mission_running:
    agent_host.sendCommand("quit")




