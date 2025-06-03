# learning.py

import MalmoPython
import os
import sys
import random
import time
import json
from qLearn_helper import (
    get_inventory_item_count,
    get_state_active_scan_5_points,
    print_intuitive_state_5_points,
    step,
    teleport_agent,
    get_ticks_since_mission_start,
    VALID_FARM_COORDINATES, # Make sure these are imported or defined here
    ACTIONS_LIST,
    ACTION_NAMES
)
from q_agent import QLearningAgent
import matplotlib.pyplot as plt # Ensure matplotlib is imported

# --- Class to Tee stdout to a file (as provided before) ---
# --- Class to Tee stdout to a file ---
class Logger(object):
    def __init__(self, filename="Default.log", mode="a", buff=1): # CHANGED mode to "a"
        self.stdout = sys.stdout
        # Python 3+ uses 'buffering=', Python 2 uses 'bufsize=' or just the integer for 'buff'
        if sys.version_info[0] >= 3:
            self.file = open(filename, mode, buffering=buff, encoding='utf-8') # Added encoding for robustness
        else: # Python 2
            self.file = open(filename, mode, buff)
        self.filename = filename

    def write(self, message):
        self.stdout.write(message)
        self.file.write(message)
        # If line buffering (buff=1) is working as expected, explicit flush per write might not be strictly necessary.
        # However, for very critical live logging, or if issues persist, uncommenting flush can help.
        # self.flush() 

    def flush(self): 
        self.stdout.flush()
        self.file.flush()

    def close(self): 
        # print("DEBUG: Logger close called. sys.stdout is self: {}".format(sys.stdout == self)) # Debug print
        original_stdout_ref = self.stdout # Keep a local reference
        if self.file is not None:
            # print("DEBUG: Closing file: {}".format(self.filename)) # Debug print
            self.file.close()
            self.file = None
        if original_stdout_ref is not None:
            # Only restore if sys.stdout is still our logger instance
            if sys.stdout == self: 
                sys.stdout = original_stdout_ref
            self.stdout = None

    def __del__(self): 
        # print("DEBUG: Logger __del__ called.") # Debug print
        self.close()


# --- Main script execution block ---
if __name__ == "__main__":

# --- Main script execution block ---
    log_filename = "mission_RL_output.log"
    logger_instance = Logger(log_filename, mode="w") 
    sys.stdout = logger_instance
    
    print("--- Script Start ---")
    print("Standard output is now being logged to: {}".format(log_filename))

    # ... (mission_xml and agent_host setup as before) ...


    mission_xml = '''
<?xml version="1.0" encoding="UTF-8" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <About>
        <Summary>Frank's Test - Step 2</Summary>
    </About>
    <ModSettings>
        <MsPerTick>3</MsPerTick>
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
            <ObservationFromGrid>
                <Grid name="wheatField">
                    <min x="-3" y="225" z="-6"/>
                    <max x="3" y="229" z="0"/>
                </Grid>
            </ObservationFromGrid>
            <ObservationFromRay />
            <ObservationFromFullInventory/>
            <ObservationFromFullStats />
        </AgentHandlers>
    </AgentSection>
</Mission>
'''    
    agent_host = MalmoPython.AgentHost()
    # ... (agent_host.parse, client_pool, mission_spec setup) ...
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print('ERROR parsing arguments:', e); print(agent_host.getUsage())
        if isinstance(sys.stdout, Logger): sys.stdout.close(); exit(1)
    if agent_host.receivedArgument("help"):
        print(agent_host.getUsage())
        if isinstance(sys.stdout, Logger): sys.stdout.close(); exit(0)

    my_client_pool = MalmoPython.ClientPool()
    my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    my_mission_record = MalmoPython.MissionRecordSpec()

    # --- RL Setup ---
    training_state_filename = "farm_training_state.pkl" # Define filename

    q_agent = QLearningAgent(
        actions_list=list(range(len(ACTIONS_LIST))), 
        alpha=0.1, gamma=0.9, epsilon=1.0, 
        epsilon_decay=0.98, min_epsilon=0.05   
    )

    # Load existing training state (Q-table, epsilon, histories)
    start_episode_num, episode_rewards, episode_wheat_collected = q_agent.load_training_state(training_state_filename)
    # episode_rewards and episode_wheat_collected will be populated with historical data if loaded

    # --- Malmo Mission Start ---
    # ... (your mission start loop as before) ...
    max_retries = 3
    for retry in range(max_retries):
        try:
            agent_host.startMission(my_mission, my_client_pool, my_mission_record, 0, "Frank_RL_Farmer_Role")
            break
        except RuntimeError as e:
            if retry == max_retries - 1: print("Error starting mission:", e); exit(1)
            else: print("Retry starting mission..."); time.sleep(2)
    print("Waiting for the mission to start", end=' '); world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun: print(".", end=""); sys.stdout.flush(); time.sleep(0.1); world_state = agent_host.getWorldState()
    for error in world_state.errors: print("\nERROR:", error.text)
    print("\nMission started!")


    # --- RL Training Loop ---
    # num_episodes_this_session is how many MORE episodes to run in THIS session
    num_episodes_this_session = 150  
    total_episodes_target = start_episode_num + num_episodes_this_session 
    max_steps_per_episode = 100 

    if not 'VALID_FARM_COORDINATES' in globals() and not 'VALID_FARM_COORDINATES' in locals():
         print("ERROR: VALID_FARM_COORDINATES not defined/imported!")
         if isinstance(sys.stdout, Logger): sys.stdout.close(); exit(1)
    initial_farm_spots = list(VALID_FARM_COORDINATES) 

    start_time = 0

    try: 
        # Loop from the loaded start_episode_num up to the new target
        for episode_idx in range(start_episode_num, total_episodes_target):
            # episode_idx is 0-indexed internally for loop, actual episode number is episode_idx + 1
            actual_episode_number = episode_idx + 1

            start_x, start_z = random.choice(initial_farm_spots)
            teleport_agent(agent_host, start_x + 0.5, 227.0, start_z + 0.5)
            time.sleep(0.2) 

            current_x, current_z = start_x, start_z
            current_cumulative_reward = 0
            
            time.sleep(0.1) 
            initial_wheat_count = get_inventory_item_count(agent_host, "wheat")
            if initial_wheat_count < 0: 
                print("WARNING: Error getting initial wheat count for episode {}. Setting to 0.".format(actual_episode_number))
                initial_wheat_count = 0
            
            current_state = get_state_active_scan_5_points(agent_host, current_x, current_z)

            print("\n" + "=" * 70)
            print("========== S T A R T   O F   E P I S O D E : {:>5} ==========".format(actual_episode_number))
            print("=" * 70)
            print("Initial position: ({}, {}), Initial wheat in inventory: {}".format(current_x, current_z, initial_wheat_count))
            print("Current Epsilon (start of ep): {:.4f}".format(q_agent.epsilon))
            print_intuitive_state_5_points(current_state)
            
            # time.sleep(0.5)  
            # # print("-" * 70) 
            # ticks = get_ticks_since_mission_start(agent_host)
            # ticks = ticks - start_time
            # print()
            # print("episode length: ")
            # print(ticks)
            # print()
            # time.sleep(0.5) 
            # start_time = get_ticks_since_mission_start(agent_host)
            # print("start time:")
            # print(start_time)
            # print()
            # time.sleep(0.5) 

            for step_num in range(max_steps_per_episode):
                # ... (step execution logic as before) ...
                world_state = agent_host.getWorldState() 
                if not world_state.is_mission_running:
                    print("Mission ended prematurely in episode {} at step {}.".format(actual_episode_number, step_num + 1))
                    break
                for error in world_state.errors: print("MALMO RUNTIME ERROR: {}".format(error.text))

                action_idx = q_agent.choose_action(current_state)
                (next_x, next_z), reward = step(agent_host, action_idx, current_x, current_z, current_state)
                current_cumulative_reward += reward
                time.sleep(0.1) 
                next_state = get_state_active_scan_5_points(agent_host, next_x, next_z)
                q_agent.learn(current_state, action_idx, reward, next_state)
                current_state = next_state
                current_x, current_z = next_x, next_z
                print("Ep {}, St {}: @({}, {}), Act:{}, Rew:{:.1f}, TotRew:{:.1f}, Eps:{:.3f}".format(
                    actual_episode_number, step_num + 1, current_x, current_z, ACTION_NAMES.get(action_idx, "Unknown"), 
                    reward, current_cumulative_reward, q_agent.epsilon))
                time.sleep(0.05)  

            # --- End of Episode ---
            # Append to the potentially loaded lists
            episode_rewards.append(current_cumulative_reward) 
            q_agent.decay_epsilon()

            final_wheat_count = get_inventory_item_count(agent_host, "wheat")
            if final_wheat_count < 0: 
                print("WARNING: Error getting final wheat count for episode {}. Assuming no change.".format(actual_episode_number))
                final_wheat_count = initial_wheat_count 
            wheat_collected_this_episode = final_wheat_count - initial_wheat_count
            episode_wheat_collected.append(wheat_collected_this_episode)

            # ... (obnoxious end of episode print statements, using actual_episode_number) ...
            print("-" * 70)
            print("*" * 70)
            print("********** E N D   O F   E P I S O D E : {:>5} **********".format(actual_episode_number))
            print("Total Reward for Episode: {:.2f}".format(current_cumulative_reward))
            print("Wheat Collected This Episode: {}".format(wheat_collected_this_episode))
            print("Total Wheat in Inventory: {}".format(final_wheat_count))
            print("Current Epsilon (end of ep): {:.4f}".format(q_agent.epsilon))
            print("*" * 70)
            sys.stdout.flush()

            # Save training state at the end of every episode
            # Pass episode_idx (0-indexed) as last_episode_completed
            q_agent.save_training_state(training_state_filename, episode_idx, episode_rewards, episode_wheat_collected)

    except KeyboardInterrupt:
        print("\nINFO: Training interrupted. Saving final state...")
    finally: 
        if 'q_agent' in locals() and 'episode_idx' in locals(): 
             q_agent.save_training_state(training_state_filename, episode_idx, episode_rewards, episode_wheat_collected)
        elif 'q_agent' in locals(): # If interrupted before first episode completed
             q_agent.save_training_state(training_state_filename, -1, episode_rewards, episode_wheat_collected)


        print("\n" + "#" * 70)
        print("############ T R A I N I N G   S E S S I O N   E N D E D ############")
        print("#" * 70)

        if episode_rewards: 
            try:
                plt.figure(figsize=(14, 6))
                plt.subplot(1, 2, 1)
                plt.plot(episode_rewards) # This will now plot the full history
                plt.title('Cumulative Episode Rewards Over All Time')
                plt.xlabel('Overall Episode Number (across sessions)')
                plt.ylabel('Total Reward')
                plt.grid(True)

                plt.subplot(1, 2, 2)
                plt.plot(episode_wheat_collected) # Full history
                plt.title('Cumulative Wheat Collected Per Episode')
                plt.xlabel('Overall Episode Number (across sessions)')
                plt.ylabel('Net Wheat Collected')
                plt.grid(True)
                
                plt.tight_layout()
                plot_filename = "training_plots_cumulative.png" 
                plt.savefig(plot_filename)
                print("INFO: Cumulative plots saved to {}".format(plot_filename))
            except ImportError: print("WARNING: matplotlib not found.")
            except Exception as e: print("ERROR: Could not generate plots - {}".format(e))

        if agent_host.getWorldState().is_mission_running:
            print("INFO: Mission still running, sending quit command.")
            agent_host.sendCommand("quit"); time.sleep(1)
        print("--- Script End ---")
        if isinstance(sys.stdout, Logger):
            print("INFO: Closing log file: {}".format(sys.stdout.filename))

            sys.stdout.close()