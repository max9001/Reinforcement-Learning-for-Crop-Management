# learning.py

import MalmoPython
import os
import sys
import random
import time
import json
from qLearn_helper import *
from q_agent import QLearningAgent

# --- Class to Tee stdout to a file (as provided before) ---
class Logger(object):
    def __init__(self, filename="Default.log", mode="a", buff=1): # Changed buff to 1 for line buffering
        self.stdout = sys.stdout
        self.file = open(filename, mode, buffering=buff if sys.version_info[0] >=3 else buff) # Python 3+ uses buffering
        self.filename = filename # Store filename for messages

    def write(self, message):
        self.stdout.write(message)
        self.file.write(message)
        # No explicit flush needed per write if line buffered, but can be added if issues.

    def flush(self): # Keep flush method if manual flushing is desired
        self.stdout.flush()
        self.file.flush()

    def close(self): 
        if self.stdout is not None:
            # Only restore if sys.stdout is still our logger instance
            if sys.stdout == self: 
                sys.stdout = self.stdout 
            self.stdout = None # Break circular reference for original stdout
        if self.file is not None:
            self.file.close()
            self.file = None

    def __del__(self): 
        self.close()

# --- Main script execution block ---
if __name__ == "__main__":
    # --- Setup logging ---
    log_filename = "mission_RL_output.log"
    # Create a logger instance and redirect stdout
    # IMPORTANT: Do this BEFORE any other print statements you want captured.
    logger_instance = Logger(log_filename, mode="w") # 'w' to overwrite for each new run
    sys.stdout = logger_instance
    
    print("--- Script Start ---")
    print("Standard output is now being logged to: {}".format(log_filename))

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
            <ChatCommands/>

            <AgentQuitFromTimeUp timeLimitMs="9999999999999999" description="Mission Ended (Time Up)."/>
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

    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print('ERROR parsing arguments:', e)
        print(agent_host.getUsage())
        if isinstance(sys.stdout, Logger): sys.stdout.close() # Ensure log file is closed
        exit(1)
    if agent_host.receivedArgument("help"):
        print(agent_host.getUsage())
        if isinstance(sys.stdout, Logger): sys.stdout.close()
        exit(0)

    my_client_pool = MalmoPython.ClientPool()
    my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))

    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    my_mission_record = MalmoPython.MissionRecordSpec()

    max_retries = 3
    for retry in range(max_retries):
        try:
            agent_host.startMission(my_mission, my_client_pool, my_mission_record, 0, "Frank_RL_Farmer_Role")
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:", e)
                if isinstance(sys.stdout, Logger): sys.stdout.close()
                exit(1)
            else:
                print("Retry starting mission in 2 seconds...")
                time.sleep(2)

    print("Waiting for the mission to start", end=' ')
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        print(".", end="")
        sys.stdout.flush() # Force console print
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("\nERROR during mission start:", error.text)
    print("\nMission started!")

    # --- RL Setup ---
    q_agent = QLearningAgent(
        actions_list=list(range(len(ACTIONS_LIST))),
        alpha=0.05,      
        gamma=0.95,      
        epsilon=1.0,    
        epsilon_decay=0.995, # A more reasonable decay
        min_epsilon=0.05   
    )

    # --- RL Training Loop ---
    num_episodes = 500  # Adjust as needed
    max_steps_per_episode = 100 # Adjust as needed

    episode_rewards = []
    episode_wheat_collected = [] 

    # Ensure VALID_FARM_COORDINATES is accessible (defined in qLearn_helper.py or here)
    if not 'VALID_FARM_COORDINATES' in globals() and not 'VALID_FARM_COORDINATES' in locals():
         print("ERROR: VALID_FARM_COORDINATES not defined/imported!")
         # Define it here if it's not in qLearn_helper or qLearn_helper isn't fully imported
         # For example:
         # VALID_FARM_COORDINATES = set([(-3,-6), ...]) # Your full list
         # For now, exiting if not found, assuming it's in qLearn_helper
         if isinstance(sys.stdout, Logger): sys.stdout.close()
         exit(1)

    initial_farm_spots = list(VALID_FARM_COORDINATES) 

    for episode in range(num_episodes):
        start_x, start_z = random.choice(initial_farm_spots)
        teleport_agent(agent_host, start_x + 0.5, 227.0, start_z + 0.5)
        time.sleep(0.2) 

        current_x, current_z = start_x, start_z
        current_cumulative_reward = 0
        
        time.sleep(0.1) 
        initial_wheat_count = get_inventory_item_count(agent_host, "wheat")
        if initial_wheat_count < 0: 
            print("WARNING: Error getting initial wheat count for episode {}. Setting to 0.".format(episode + 1))
            initial_wheat_count = 0
        
        current_state = get_simple_state(agent_host, current_x, current_z)

        print("\n" + "=" * 70)
        print("========== S T A R T   O F   E P I S O D E : {:>5} ==========".format(episode + 1))
        print("=" * 70)
        print("Initial position: ({}, {}), Initial wheat in inventory: {}".format(current_x, current_z, initial_wheat_count))
        # print_intuitive_state_5_points(current_state)
        print("-" * 70) 

        agent_host.sendCommand("setPitch 90")
        for step_num in range(max_steps_per_episode):
            world_state = agent_host.getWorldState() # Get fresh world state
            if not world_state.is_mission_running:
                print("Mission ended prematurely in episode {} at step {}.".format(episode + 1, step_num))
                break
            
            # Check for Malmo errors during step
            for error in world_state.errors:
                print("MALMO RUNTIME ERROR: {}".format(error.text))


            action_idx = q_agent.choose_action(current_state)
            
            (next_x, next_z), reward = step(agent_host, action_idx, current_x, current_z, current_state)
            current_cumulative_reward += reward
            
            # Small delay to allow observation to catch up with the action's effects
            time.sleep(0.1) # THIS IS IMPORTANT, especially after an action modifying the world
            
            next_state = get_simple_state(agent_host, next_x, next_z)
            q_agent.learn(current_state, action_idx, reward, next_state)

            current_state = next_state
            current_x, current_z = next_x, next_z

            print("Ep {}, St {}: @({}, {}), Act:{}, Rew:{:.1f}, TotRew:{:.1f}, Eps:{:.3f}".format(
                episode + 1, step_num + 1, current_x, current_z, ACTION_NAMES.get(action_idx, "Unknown"), 
                reward, current_cumulative_reward, q_agent.epsilon
            ))
            
            # A very short sleep if MsPerTick is low, or longer if MsPerTick is high
            # With MsPerTick=50, 0.05s is 2.5 ticks.
            # With MsPerTick=3, 0.05s is ~16 ticks.
            time.sleep(0.05)  # General loop delay

        # --- End of Episode ---
        episode_rewards.append(current_cumulative_reward)
        q_agent.decay_epsilon()

        final_wheat_count = get_inventory_item_count(agent_host, "wheat")
        # if final_wheat_count < 0: 
        #     print("WARNING: Error getting final wheat count for episode {}. Assuming no change.".format(episode + 1))
        #     final_wheat_count = initial_wheat_count 
            
        # wheat_collected_this_episode = final_wheat_count - initial_wheat_count
        # episode_wheat_collected.append(wheat_collected_this_episode)
        episode_wheat_collected.append(final_wheat_count)


        print("-" * 70)
        print("*" * 70)
        print("********** E N D   O F   E P I S O D E : {:>5} **********".format(episode + 1))
        print("Total Reward for Episode: {:.2f}".format(current_cumulative_reward))
        # print("Wheat Collected This Episode: {}".format(wheat_collected_this_episode))
        print("Total Wheat in Inventory: {}".format(final_wheat_count))
        print("Current Epsilon: {:.4f}".format(q_agent.epsilon))
        print("*" * 70)
        sys.stdout.flush() # Ensure all episode summary is written to file

        agent_host.sendCommand("chat /clear Frank wheat") 
        agent_host.sendCommand("give wheat_seeds 64")      

    # --- End of Training ---
    print("\n" + "#" * 70)
    print("############ T R A I N I N G   C O M P L E T E ############")
    print("#" * 70)

    # Plotting
    # try:
    #     plt.figure(figsize=(14, 6))
    #     plt.subplot(1, 2, 1)
    #     plt.plot(episode_rewards)
    #     plt.title('Episode Rewards Over Time')
    #     plt.xlabel('Episode')
    #     plt.ylabel('Total Reward')
    #     plt.grid(True)

    #     plt.subplot(1, 2, 2)
    #     plt.plot(episode_wheat_collected)
    #     plt.title('Wheat Collected Per Episode')
    #     plt.xlabel('Episode')
    #     plt.ylabel('Net Wheat Collected')
    #     plt.grid(True)
        
    #     plt.tight_layout()
    #     plot_filename = "training_plots.png"
    #     plt.savefig(plot_filename)
    #     print("INFO: Plots saved to {}".format(plot_filename))
    #     # plt.show() # This will block if run in a non-interactive environment
    # except ImportError:
    #     print("WARNING: matplotlib not found. Cannot generate plots. Please install it (`pip install matplotlib`).")
    # except Exception as e:
    #     print("ERROR: Could not generate plots - {}".format(e))
    # Print episode rewards and wheat collected as comma-separated lists for external plotting
    print("\nEpisode Rewards (comma-separated):")
    print(','.join(str(r) for r in episode_rewards))

    print("\nWheat Collected Per Episode (comma-separated):")
    print(','.join(str(w) for w in episode_wheat_collected))

    if agent_host.getWorldState().is_mission_running:
        print("INFO: Mission still running, sending quit command.")
        agent_host.sendCommand("quit")
        time.sleep(1) # Give time for quit to process

    print("--- Script End ---")
    
    # Explicitly close the logger at the very end
    # This also restores original stdout
    if isinstance(sys.stdout, Logger):
        print("INFO: Closing log file: {}".format(sys.stdout.filename))
        sys.stdout.close()