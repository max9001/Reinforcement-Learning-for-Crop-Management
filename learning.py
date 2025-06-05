# learning.py

import MalmoPython
import os
import sys
import random
import time
import json
from qLearn_helper import *
from q_agent import QLearningAgent # Assuming QLearningAgent is in q_agent.py
import matplotlib.pyplot as plt

# --- Logger Class (as before) ---
class Logger(object):
    def __init__(self, filename="Default.log", mode="a", buff=1):
        self.stdout = sys.stdout
        if sys.version_info[0] >= 3:
            self.file = open(filename, mode, buffering=buff, encoding='utf-8')
        else:
            self.file = open(filename, mode, buff)
        self.filename = filename
    def write(self, message): self.stdout.write(message); self.file.write(message)
    def flush(self): self.stdout.flush(); self.file.flush()
    def close(self): 
        original_stdout_ref = self.stdout
        if self.file is not None: self.file.close(); self.file = None
        if original_stdout_ref is not None:
            if sys.stdout == self: sys.stdout = original_stdout_ref
            self.stdout = None
    def __del__(self): self.close()

# --- Main script execution block ---
if __name__ == "__main__":
    log_filename = "mission_RL_output.log"
    logger_instance = Logger(log_filename, mode="w") 
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
    try: agent_host.parse(sys.argv)
    except RuntimeError as e: print('ERROR:',e); print(agent_host.getUsage()); sys.stdout.close(); exit(1)
    if agent_host.receivedArgument("help"): print(agent_host.getUsage()); sys.stdout.close(); exit(0)

    my_client_pool = MalmoPython.ClientPool(); my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))
    my_mission = MalmoPython.MissionSpec(mission_xml, True); my_mission_record = MalmoPython.MissionRecordSpec()

    training_state_filename = "farm_abstract_q_table.pkl" # Use a new name for state changes
    q_agent = QLearningAgent(
        actions_list=list(range(len(ACTIONS_LIST))), 
        alpha=0.1, gamma=0.9, epsilon=1.0, 
        epsilon_decay=0.995, min_epsilon=0.05   
    )
    start_episode_num, cumulative_episode_rewards, cumulative_episode_wheat = q_agent.load_training_state(training_state_filename)
    
    # For tracking stats specific to THIS run/session
    current_session_episode_rewards = []
    current_session_wheat_collected = []


    max_retries = 3
    for retry in range(max_retries):
        try: agent_host.startMission(my_mission, my_client_pool, my_mission_record, 0, "Frank_RL_Farmer"); break
        except RuntimeError as e:
            if retry == max_retries - 1: print("Error starting mission:", e); sys.stdout.close(); exit(1)
            else: print("Retry starting mission..."); time.sleep(2)
    print("Waiting for mission to start", end=''); world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun: print(".", end=""); sys.stdout.flush(); time.sleep(0.1); world_state = agent_host.getWorldState()
    for error in world_state.errors: print("\nERROR:", error.text)
    print("\nMission started!")

    num_episodes_this_session = 12 
    total_episodes_target = start_episode_num + num_episodes_this_session 
    max_steps_per_episode = 100 

    if 'VALID_FARM_COORDINATES' not in globals() and 'VALID_FARM_COORDINATES' not in locals():
         print("CRITICAL ERROR: VALID_FARM_COORDINATES not defined!"); sys.stdout.close(); exit(1)
    initial_farm_spots = list(VALID_FARM_COORDINATES) 

    last_saved_episode_idx = start_episode_num -1 # Track last successfully saved episode


    agent_host.sendCommand("setPitch 90")

    try: 
        for episode_idx in range(start_episode_num, total_episodes_target):
            actual_episode_number = episode_idx + 1
            start_x, start_z = random.choice(initial_farm_spots)
            teleport_agent(agent_host, start_x + 0.5, 227.0, start_z + 0.5); time.sleep(0.2)
            current_x, current_z = start_x, start_z
            current_ep_cumulative_reward = 0 # Reward for THIS episode
            
            time.sleep(0.1) 
            initial_wheat_count_this_ep = get_inventory_item_count(agent_host, "wheat")
            if initial_wheat_count_this_ep < 0: initial_wheat_count_this_ep = 0
            
            current_state = get_state_abstracted_5_points(agent_host, current_x, current_z) 

            print("\n" + "=" * 70 + "\n========== S T A R T   O F   E P I S O D E : {:>5} ==========\n".format(actual_episode_number) + "=" * 70)
            print("Physical Position: ({}, {}), Initial Ep Wheat: {}".format(current_x, current_z, initial_wheat_count_this_ep))
            print("Current Epsilon (start): {:.4f}".format(q_agent.epsilon))
            print_intuitive_abstracted_state(current_state); print("-" * 70) 

            for step_num in range(max_steps_per_episode):
                world_state = agent_host.getWorldState() 
                if not world_state.is_mission_running: print("Mission ended: Ep {}, St {}.".format(actual_episode_number, step_num + 1)); break
                for error in world_state.errors: print("MALMO RUNTIME ERROR: {}".format(error.text))

                action_idx = q_agent.choose_action(current_state)
                (next_x, next_z), reward = step(agent_host, action_idx, current_x, current_z, current_state)
                current_ep_cumulative_reward += reward
                time.sleep(0.1) 
                next_state = get_state_abstracted_5_points(agent_host, next_x, next_z)
                q_agent.learn(current_state, action_idx, reward, next_state)
                current_state = next_state; current_x, current_z = next_x, next_z
                print("Ep {}, St {}: @({}, {}), Act:{}, Rew:{:.1f}, TotEpRew:{:.1f}, Eps:{:.3f}".format(
                    actual_episode_number, step_num + 1, current_x, current_z, ACTION_NAMES.get(action_idx, "Unk"), 
                    reward, current_ep_cumulative_reward, q_agent.epsilon))
                time.sleep(0.05)

            # --- End of Episode ---
            cumulative_episode_rewards.append(current_ep_cumulative_reward) # Append to CUMULATIVE list
            current_session_episode_rewards.append(current_ep_cumulative_reward) # Append to THIS SESSION's list
            q_agent.decay_epsilon()

            final_wheat_count_this_ep = get_inventory_item_count(agent_host, "wheat")
            if final_wheat_count_this_ep < 0: final_wheat_count_this_ep = initial_wheat_count_this_ep
            wheat_collected_this_ep = final_wheat_count_this_ep - initial_wheat_count_this_ep
            
            cumulative_episode_wheat.append(wheat_collected_this_ep) # Append to CUMULATIVE list
            current_session_wheat_collected.append(wheat_collected_this_ep) # Append to THIS SESSION's list

            print("-" * 70 + "\n" + "*" * 70)
            print("********** E N D   O F   E P I S O D E : {:>5} **********\n".format(actual_episode_number) +
                  "Total Reward for Episode: {:.2f}\n".format(current_ep_cumulative_reward) +
                  "Wheat Collected This Episode: {}\n".format(wheat_collected_this_ep) +
                  "Total Wheat in Inventory (end of ep): {}\n".format(final_wheat_count_this_ep) +
                  "Current Epsilon (end of ep): {:.4f}\n".format(q_agent.epsilon) + "*" * 70); sys.stdout.flush()
            
            q_agent.save_training_state(training_state_filename, episode_idx, cumulative_episode_rewards, cumulative_episode_wheat)
            last_saved_episode_idx = episode_idx


    except KeyboardInterrupt: print("\nINFO: Training interrupted. Saving final state...")
    finally: 
        if 'q_agent' in locals():
             q_agent.save_training_state(training_state_filename, last_saved_episode_idx, cumulative_episode_rewards, cumulative_episode_wheat)
        
        print("\n" + "#" * 70 + "\n############ T R A I N I N G   S E S S I O N   E N D E D ############\n" + "#" * 70)

        print("\n" * 7)
        print(current_session_wheat_collected)



        # if cumulative_episode_rewards: 
        #     try:
        #         plt.figure(figsize=(18, 6)) # Wider figure
                
        #         # Plot for CUMULATIVE (all runs) rewards
        #         plt.subplot(1, 3, 1) # Changed to 1 row, 3 cols, 1st subplot
        #         plt.plot(cumulative_episode_rewards) 
        #         plt.title('Overall Rewards (All Sessions)')
        #         plt.xlabel('Overall Episode Number')
        #         plt.ylabel('Total Reward Per Episode')
        #         plt.grid(True)

        #         # Plot for CUMULATIVE (all runs) wheat
        #         plt.subplot(1, 3, 2) # Changed to 1 row, 3 cols, 2nd subplot
        #         plt.plot(cumulative_episode_wheat) 
        #         plt.title('Overall Wheat Collected (All Sessions)')
        #         plt.xlabel('Overall Episode Number')
        #         plt.ylabel('Net Wheat Per Episode')
        #         plt.grid(True)

        #         # Plot for THIS SESSION ONLY wheat collected
        #         plt.subplot(1, 3, 3) # Changed to 1 row, 3 cols, 3rd subplot
        #         # X-axis for this session plot: number of episodes run in this session
        #         session_episode_numbers = range(1, len(current_session_wheat_collected) + 1)
        #         plt.plot(session_episode_numbers, current_session_wheat_collected, color='orange') 
        #         plt.title('Wheat Collected (This Session Only)')
        #         plt.xlabel('Episode Number in This Session')
        #         plt.ylabel('Net Wheat Per Episode')
        #         plt.grid(True)
                
        #         plt.tight_layout()
        #         plot_filename = "training_plots_summary.png" 
        #         plt.savefig(plot_filename); print("INFO: Summary plots saved to {}".format(plot_filename))
        #     except ImportError: print("WARNING: matplotlib not found.")
        #     except Exception as e: print("ERROR: Could not generate plots - {}".format(e))

        if agent_host.getWorldState().is_mission_running: agent_host.sendCommand("quit"); time.sleep(1)
        print("--- Script End ---")
        if isinstance(sys.stdout, Logger): print("INFO: Closing log file: {}".format(sys.stdout.filename)); sys.stdout.close()




















