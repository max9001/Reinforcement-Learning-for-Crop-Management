import sys
sys.path.append("/home/malmo/MalmoPlatform/Malmo/samples/Python_examples")

# --------------------------------------------------------------------------

import MalmoPython  # <<< IMPORTANT: Change to import MalmoPython if not using Docker
import os
import sys  # <<< IMPORTANT: Ensure this is imported
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
    agent_host.parse(sys.argv)  # sys.argv needs 'import sys'
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
my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))  # Default Malmo port

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
    for error in world_state.errors:  # Check for errors reported by Malmo
        print("\nERROR during mission start:", error.text)
        # If there are errors here, it often means an XML issue or client connection problem
print("\nMission started!")

# --- Agent Action Sequence ---
# while agent_host.getWorldState().is_mission_running:
# random_method(agent_host)

# iteration_method(agent_host)

# wait_10mins_method(agent_host)

# --- RL Setup ---
# Define your action space (index to method)

ACTIONS = [
    "move_up",
    "move_down",
    "move_left",
    "move_right",
    "harvest",  # equals attack
    "plant",
    "wait"  # waiting for maturity
]


# define actions with their rewards
def step(agent_host, action_idx, x, z):
    #     action = ACTIONS[action_idx]
    reward = 0
    next_x, next_z = x, z

    if action == 0:
        next_z = z - 1
    elif action == 1:
        next_z = z + 1
    elif action == 2:
        next_x = x - 1
    elif action == 3:
        next_x = x + 1
    elif action == 4:
        age = get_wheat_age_in_los(agent_host)
        if age == 7:
            reward = 1
        elif age >= 0:
            reward = -1
        look_down_harvest_and_replant(agent_host)
    elif action == 5:
        plant_seed(agent_host)
    elif action == 6:
        time.sleep(0.5)

    teleport_agent(agent_host, next_x + 0.5, 227, next_z + 0.5)
    return (next_x, next_z), reward


# --- RL Training Loop ---

num_episodes = 10  # Increase for real training
max_steps_per_episode = 50  # number of actions can be performed per episode

agent = QLearningAgent(
    actions=list(range(len(ACTIONS))),
    alpha=0.1,
    gamma=0.9,
    epsilon=0.2
)

for episode in range(num_episodes):
    #     print(f"\n=== Episode {episode + 1} ===")

    x, z = 0, -3
    teleport_agent(agent_host, x + 0.5, 227, z + 0.5)

    state = get_state(x, z, agent_host)

    for t in range(max_steps_per_episode):
        action = agent.choose_action(state)
        (next_x, next_z), reward = step(agent_host, action, x, z)
        next_state = get_state(next_x, next_z, agent_host)

        agent.learn(state, action, reward, next_state)

        #         print(f"Step {t}: action={ACTIONS[action]}, reward={reward}, state={next_state}")

        state = next_state
        x, z = next_x, next_z

print("\nTraining complete.")
print("\nMission ended")
# Mission has ended.