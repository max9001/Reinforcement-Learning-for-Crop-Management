import sys
sys.path.append("/usr/local/lib/python3.5/dist-packages/malmo/") 

#--------------------------------------------------------------------------

import MalmoPython
import os
import sys # <<< IMPORTANT: Ensure this is imported
import random
import time
import json
from helper import *

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
            <InventoryCommands />
            <AbsoluteMovementCommands/>
            <ContinuousMovementCommands turnSpeedDegs="180"/>
            <AgentQuitFromTimeUp timeLimitMs="30000000" description="Mission Ended (Time Up)."/>
            <ObservationFromGrid>
                <Grid name="wheatField">
                    <min x="-3" y="225" z="-6"/>
                    <max x="3" y="229" z="0"/>
                </Grid>
            </ObservationFromGrid>
            <ObservationFromFullInventory flat="false"/> <!-- ADD THIS LINE -->
            <ObservationFromFullStats />
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

# Mission setup - try stuff below here:

# --- Agent Action Sequence ---

agent_host.sendCommand("setPitch 90")
time.sleep(0.01)

teleport_agent(agent_host, 0.5, 227, -2.5)
current_x = 0
current_z = -3

start_time = get_ticks_since_mission_start(agent_host)
print(start_time)

print_counter = 0

while agent_host.getWorldState().is_mission_running:
    
#     print_counter += 1
# #     time.sleep(0.5)
    
#     choice = random.randint(1, 3)

#     if choice == 1:
#         time.sleep(0.2) 
#         attack(agent_host)
#     elif choice == 2:
#         time.sleep(0.2) 
#         plant_seed(agent_host)
#     elif choice == 3:
#         time.sleep(0.2) 
#         current_x, current_z = perform_random_teleport_step(agent_host, current_x, current_z)        

    time.sleep(59)
    
    iterate_through_farm(agent_host)
    
#     if (print_counter % 40 == 0):
    time.sleep(0.5)  
    ticks = get_ticks_since_mission_start(agent_host)
    ticks = ticks - start_time
    time.sleep(0.5)  
    wheats = get_inventory_item_count(agent_host, "wheat")
    print("({}, {})".format(ticks, wheats))
        
    time.sleep(0.5)  
    

print()
print("Mission ended")
# Mission has ended.