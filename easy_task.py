import MalmoPython
import os
import sys # <<< IMPORTANT: Ensure this is imported
import time
import json


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
                <DrawBlock x="0" y="227" z="0" type="wheat"/>
            </DrawingDecorator>
            <ServerQuitWhenAnyAgentFinishes />
        </ServerHandlers>
    </ServerSection>
    <AgentSection mode="Creative">
        <Name>Frank</Name>
        <AgentStart>
            <Placement x="0.5" y="227.0" z="3.5" yaw="180" />
            <Inventory />
        </AgentStart>
        <AgentHandlers>
            <AgentQuitFromTimeUp timeLimitMs="300000" description="Step 2 Test Ended."/>
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
            print("Is the Minecraft client running and waiting for a mission?")
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

# --- Main Loop (Simplified for testing) ---
commands_sent = 0
target_commands = 4 # 3 moves + 1 attack command sequence

while world_state.is_mission_running:
    time.sleep(0.1) # Wait a bit between polling
    world_state = agent_host.getWorldState()

    if commands_sent == 0:
        print("Sending: move 1 (forward)")
        agent_host.sendCommand("move 1")
        commands_sent += 1
    elif commands_sent == 1:
        print("Sending: move 1 (forward)")
        agent_host.sendCommand("move 1")
        commands_sent += 1
    elif commands_sent == 2:
        print("Sending: move 1 (forward)")
        agent_host.sendCommand("move 1")
        commands_sent += 1
    elif commands_sent == 3: # After 3 moves, try attacking
        print("Sending: attack 1")
        agent_host.sendCommand("attack 1")
        commands_sent += 1 # Increment to stop sending commands
    # Stop sending commands after the sequence
    # The agent will stop moving/attacking on its own after a short period for discrete commands
    # or we could send "move 0" / "attack 0" explicitly after a delay.

    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        try:
            observations = json.loads(msg)
            # print("Observations:", observations)
            if "inventory" in observations:
                for item_slot in observations["inventory"]:
                    if item_slot.get("type") == "minecraft:wheat" or item_slot.get("type") == "wheat": # check both
                        print("\nFrank has wheat in inventory!")
                        # Mission should quit automatically due to AgentQuitFromCollectingItem
                        break
        except json.JSONDecodeError:
            print("\nError decoding JSON observations:", msg)


    for reward in world_state.rewards:
        print(f"\nReward received: {reward.getValue()}")

    for error in world_state.errors: # Check for runtime errors
        print("\nERROR during mission:", error.text)

print("\nMission ended.")
# Check remarks for success
mission_successful = False
for remark in world_state.mission_ended_remarks:
    print(f"Mission End Remark: {remark}")
    if "Success! Collected the wheat." in remark:
        mission_successful = True
        break

if mission_successful:
    print("Frank successfully collected the wheat!")
else:
    print("Frank did not collect the wheat or mission ended for other reasons.")