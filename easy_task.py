import MalmoPython
import os
import sys # <<< IMPORTANT: Ensure this is imported
import time
import json
from helper import get_wheat_age_in_los


mission_xml = '''
<?xml version="1.0" encoding="UTF-8" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <About>
        <Summary>Frank's Test - Step 2</Summary>
    </About>
    <ModSettings>
        <MsPerTick>100</MsPerTick>
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
                <InventoryItem slot="0" type="dye" quantity="64" colour="WHITE"/>
            </Inventory>
        </AgentStart>
        <AgentHandlers>
            <ContinuousMovementCommands turnSpeedDegs="180"/> 
            <DiscreteMovementCommands />
            <InventoryCommands />
            <AgentQuitFromCollectingItem>
                <Item type="wheat" description="Success! Collected the wheat."/>
                <!-- You can add more <Item /> tags here if you want to quit on collecting other items too -->
            </AgentQuitFromCollectingItem>
            <AgentQuitFromTimeUp timeLimitMs="30000" description="Mission Ended (Time Up)."/>
            <ObservationFromGrid>
                <Grid name="wheatField">
                    <min x="-3" y="225" z="-6"/>
                    <max x="3" y="229" z="0"/>
                </Grid>
            </ObservationFromGrid>
            <ObservationFromRay />
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
my_mission_record = MalmoPython.MissionRecordSpec() # Not recording anything specific here

# Experiment: Request video to see if it forces a more stable client connection
# my_mission.requestVideo(320, 240)
# my_mission.setViewpoint(0) # Agent's perspective

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

# Mission setup - try stuff below here:

# --- Agent Action Sequence ---

# Action: Select Bone Meal (or specified item) from Hotbar
# Assumes the item needed (e.g., bonemeal/dye) is in the first hotbar slot.
# 'hotbar.1 1' simulates pressing the '1' key.
# 'hotbar.1 0' simulates releasing the '1' key.
print("AGENT ACTION: Selecting item in hotbar slot 1.")
agent_host.sendCommand("hotbar.1 1") # Press hotbar key 1
agent_host.sendCommand("hotbar.1 0") # Release hotbar key 1
time.sleep(1)                        # Pause to ensure item selection registers in-game.

# Action: Adjust Agent's View (Pitch Down)
# 'pitch 0.3' starts tilting the agent's view downwards.
# Positive values for pitch typically mean looking down.
# This is often used to aim at blocks at the agent's feet (e.g., crops).
print("AGENT ACTION: Pitching view downwards.")
agent_host.sendCommand("pitch 0.3") # Start tilting view downwards.
time.sleep(1)                       # Continue pitching for 1 second to reach desired angle.
agent_host.sendCommand("pitch 0")   # Stop pitching to hold the current view angle.
time.sleep(1)                       # Pause to stabilize view.

# Action: Strafe (Sidestep) to the Right
# 'strafe 1' starts moving the agent sideways to its right, without changing facing direction.
print("AGENT ACTION: Strafing right.")
agent_host.sendCommand("strafe 1")  # Start strafing right.
time.sleep(0.5)                     # Strafe for 0.5 seconds.
agent_host.sendCommand("strafe 0")  # Stop strafing.
time.sleep(1)                       # Pause after movement.

# Action: Move Forward
# 'move 1' starts moving the agent forward in its current facing direction.
print("AGENT ACTION: Moving forward.")
agent_host.sendCommand("move 1")    # Start moving forward.
time.sleep(0.5)                     # Move forward for 0.5 seconds.
agent_host.sendCommand("move 0")    # Stop moving forward.
# Note: A longer pause might be needed here if the agent needs to reach a specific block.

# Action: Use Selected Item (e.g., Apply Bonemeal)
# 'use 1' simulates a right-click action with the currently held item.
# 'use 0' stops the use action. For bonemeal, this sequence applies it once.
# The long sleep is because bonemeal application might have an in-game animation or effect delay.
print("AGENT ACTION: Attempting to use selected item (e.g., apply bonemeal).")
agent_host.sendCommand("use 1")     # Start 'use' action (right-click).
time.sleep(3)                       # Hold the 'use' action for 3 seconds.
                                    # This duration might be excessive for a single bonemeal application;
                                    # for a single use, a very short delay or just use 1 then use 0 quickly is more common.
                                    # For continuous use like eating, a longer delay is appropriate.
agent_host.sendCommand("use 0")     # Stop 'use' action.
time.sleep(1)                       # Pause after use action.

print(get_wheat_age_in_los(agent_host))

time.sleep(2) 

# Action: Strafe (Sidestep) to the Right
# 'strafe 1' starts moving the agent sideways to its right, without changing facing direction.
print("AGENT ACTION: Strafing right.")
agent_host.sendCommand("strafe 1")  # Start strafing right.
time.sleep(0.5)                     # Strafe for 0.5 seconds.
agent_host.sendCommand("strafe 0")  # Stop strafing.
time.sleep(1)                       # Pause after movement.


print(get_wheat_age_in_los(agent_host))

time.sleep(25)


# # Action: Attack (e.g., Break Wheat)
# # 'attack 1' simulates a left-click action to break a block or attack an entity.
# # 'attack 0' stops the attack action. This quick sequence is for a single hit.
# print("AGENT ACTION: Attempting to attack/break block in front.")
# agent_host.sendCommand("attack 1")  # Start 'attack' action (left-click).
# time.sleep(0.1)                     # Hold attack briefly (enough for one hit on many blocks in creative).
# agent_host.sendCommand("attack 0")  # Stop 'attack' action.
# # Note: Breaking blocks, especially in survival, might require repeated attack commands or holding attack 1 for longer.

# # Action: Move Forward
# # 'move 1' starts moving the agent forward in its current facing direction.
# print("AGENT ACTION: Moving forward.")
# agent_host.sendCommand("move 1")    # Start moving forward.
# time.sleep(1)                       # Move forward for 0.5 seconds.
# agent_host.sendCommand("move 0")    # Stop moving forward.
# # Note: A longer pause might be needed here if the agent needs to reach a specific block.


# # Loop until mission ends:
# while world_state.is_mission_running:
#     if world_state.number_of_observations_since_last_state > 0:
#         msg = world_state.observations[-1].text
#         observations = json.loads(msg)
#         if "wheatField" in observations:
#                 wheat_field = observations["wheatField"]
#                 print("Wheat Field Grid:", wheat_field)
#                 print("Grid Size:", len(wheat_field))
#     print(".", end="")
#     time.sleep(0.1)
#     world_state = agent_host.getWorldState()
#     for error in world_state.errors:
#         print("Error:",error.text)

print()
print("Mission ended")
# Mission has ended.