import json
import time
import random


# Define the globally valid farmable coordinates (as per your example)
VALID_FARM_COORDINATES = set([
    (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0),
    (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0),
    (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0),    
    (0, -6),  (0, -5),  (0, -4),            (0, -2),  (0, -1),  (0, 0), # Gap at (0, -3)
    (1, -6),  (1, -5),  (1, -4),  (1, -3),  (1, -2),  (1, -1),  (1, 0),
    (2, -6),  (2, -5),  (2, -4),  (2, -3),  (2, -2),  (2, -1),  (2, 0),
    (3, -6),  (3, -5),  (3, -4),  (3, -3),  (3, -2),  (3, -1),  (3, 0),
])
# ACTIONS for the Q-Learning Agent
ACTION_MOVE_N = 0
ACTION_MOVE_E = 1
ACTION_MOVE_S = 2
ACTION_MOVE_W = 3
ACTION_HARVEST_CURRENT = 4 # Just attempt to harvest (attack) current spot
ACTION_PLANT_CURRENT = 5   # Attempt to plant on current spot (if empty)
ACTION_WAIT = 6            # Do nothing for a short period

ACTIONS_LIST = [
    ACTION_MOVE_N,
    ACTION_MOVE_E,
    ACTION_MOVE_S,
    ACTION_MOVE_W,
    ACTION_HARVEST_CURRENT, # Changed from HARVEST_PLANT_CURRENT
    ACTION_PLANT_CURRENT,
    ACTION_WAIT
]

ACTION_NAMES = { # For printing/logging
    ACTION_MOVE_N: "Move_N",
    ACTION_MOVE_E: "Move_E",
    ACTION_MOVE_S: "Move_S",
    ACTION_MOVE_W: "Move_W",
    ACTION_HARVEST_CURRENT: "Harvest", # Changed name
    ACTION_PLANT_CURRENT: "Plant",
    ACTION_WAIT: "Wait"
}


ILLEGAL_COORD_MARKER = -99 # Special value for out-of-bounds/invalid spots

def get_wheat_age_in_los(agent_host_instance):
    """
    Checks the agent's line of sight for a wheat block and returns its age.

    Args:
        agent_host_instance: The MalmoPython.AgentHost object.

    Returns:
        int: 0-7 if the agent is looking at wheat.
             -1 if the agent is not looking at wheat
             -2 if there's an error getting or parsing observations.
    """
    world_state = agent_host_instance.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        try:
            observations = json.loads(msg)
            if "LineOfSight" in observations:
                los = observations["LineOfSight"]
                
                # Check if looking at a block and if that block is wheat
                if los.get('hitType') == 'block' and los.get('type') == 'wheat':
                    # Check for "prop_age"
                    # Block properties are directly in the los object as per your successful log
                    age_str = los.get('prop_age') 
                    if age_str is not None:
                        try:
                            return int(age_str)
                        except ValueError:
#                             print(f"Warning: Could not convert prop_age '{age_str}' to int.")
                            return -1 # Indicate error in age property format
                    else:
                        # print("Debug: 'prop_age' not found in LineOfSight for wheat.")
                        return -1 # Wheat, but no age property (shouldn't happen for vanilla wheat if F3 shows it)
                else:
                    # print("Debug: Not looking at a wheat block.")
                    return -1 # Not looking at wheat
            else:
                # print("Debug: 'LineOfSight' not in current observations.")
                return -1 # No LineOfSight data
        except json.JSONDecodeError:
#             print("Error decoding JSON for LineOfSight observation:", msg)
            return -2 # Indicate JSON error
        except Exception as e:
#             print(f"Error processing LineOfSight observation: {e}")
            return -2 # Indicate other processing error
    else:
        # print("Debug: No new observations since last state.")
        return -1 # No new observations
    
def teleport_agent(agent_host, x, y, z):
    """
    Teleports the agent to the specified (x, y, z) coordinates.
    Requires <AbsoluteMovementCommands/> in the mission XML.
    """
    agent_host.sendCommand("tp {x} {y} {z}".format(x=x, y=y, z=z))
    time.sleep(0.2)  # Give time for the teleport to register



def get_state(x, z, agent_host):
    agent_host.sendCommand("setPitch 90")
    age = get_wheat_age_in_los(agent_host)
    age = -1 if age is None else age

    has_seed = False
    world_state = agent_host.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        obs = json.loads(msg)
        for i in range(9):
            if obs.get("InventorySlot_{}_item".format(i)) == "wheat_seeds":
                if obs.get("InventorySlot_{}_size".format(i), 0) > 0:
                    has_seed = True
                    break

    return (x, z, age, int(has_seed))



def plant_seed(agent_host):
    """
    Makes frank place wheat
    check makes frank more intelligent; he will only plant if there is no wheat
    """
    agent_host.sendCommand("use 1")
    time.sleep(0.01)
    agent_host.sendCommand("use 0")
    
def attack(agent_host):
    """
    Makes frank attack for long enough to break wheat. he will only attack if there is wheat
    """
    if get_wheat_age_in_los(agent_host) >= 0:
        agent_host.sendCommand("attack 1")
        time.sleep(0.01)
        agent_host.sendCommand("attack 0")

def look_down_harvest_and_replant(agent_host):
    """
    Makes the agent look straight down, harvest the wheat, and replant seeds..
    """
    agent_host.sendCommand("attack 1")
    time.sleep(0.01)
    agent_host.sendCommand("attack 0")
    time.sleep(0.1)
    agent_host.sendCommand("use 1")
    time.sleep(0.01)
    agent_host.sendCommand("use 0")



CONDITION_OUT_OF_BOUNDS = 0        # For spots outside VALID_FARM_COORDINATES
CONDITION_EMPTY_FARMABLE = 1     # Spot is valid farmland, but no wheat (age -1 from LoS)
CONDITION_IMMATURE_WHEAT = 2     # Wheat age 0-6
CONDITION_MATURE_WHEAT = 3       # Wheat age 7

def _convert_age_to_condition(raw_age_value, is_valid_farm_coord):
    """
    Helper to convert raw age to our simplified condition,
    considering if the coordinate itself is valid farmable land.
    """
    if not is_valid_farm_coord:
        return CONDITION_OUT_OF_BOUNDS
    
    # If it's valid farm coordinate, now check wheat status
    if raw_age_value == 7:
        return CONDITION_MATURE_WHEAT
    elif raw_age_value >= 0 and raw_age_value < 7: # Covers 0-6
        return CONDITION_IMMATURE_WHEAT
    elif raw_age_value == -1: # LoS reported "not wheat" or "no age" on valid farmland
        return CONDITION_EMPTY_FARMABLE
    else: # raw_age_value is -2 (LoS error) or other unexpected on valid farmland
          # Defaulting to empty farmable, or could be a separate error condition
        print("Warning: Unexpected raw_age_value ({}) on valid farm coord. Treating as Empty/Farmable.".format(raw_age_value))
        return CONDITION_EMPTY_FARMABLE
    



def get_state_abstracted_5_points(agent_host_instance, current_x, current_z):
    """
    Gets an abstracted state based on the condition of the current cell and its 4 cardinal neighbors.
    State: (condition_N, condition_E, condition_S, condition_W, condition_current_spot)
    Conditions: 0 (OOB), 1 (Empty/Farmable), 2 (Immature), 3 (Mature).
    """
    original_pos_y = 227.0 
    cardinal_offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)] # N, E, S, W
    neighbor_conditions = []

    agent_host_instance.sendCommand("setPitch 90") 
    time.sleep(0.1)

    # 1. Get condition at the agent's current spot first
    # Current spot is assumed to be within VALID_FARM_COORDINATES if agent starts there and moves validly
    is_current_spot_valid_farm = (current_x, current_z) in VALID_FARM_COORDINATES
    raw_age_current_spot = get_wheat_age_in_los(agent_host_instance)
    condition_current_spot = _convert_age_to_condition(raw_age_current_spot, is_current_spot_valid_farm)

    # 2. Scan the 4 cardinal neighbors
    for dx, dz in cardinal_offsets:
        neighbor_x = current_x + dx
        neighbor_z = current_z + dz
        is_neighbor_valid_farm = (neighbor_x, neighbor_z) in VALID_FARM_COORDINATES

        if is_neighbor_valid_farm: # Only teleport and check LoS if it's a valid farm coordinate
            teleport_agent(agent_host_instance, neighbor_x + 0.5, original_pos_y, neighbor_z + 0.5)
            raw_age_neighbor = get_wheat_age_in_los(agent_host_instance)
            neighbor_conditions.append(_convert_age_to_condition(raw_age_neighbor, True)) # True because we checked
        else:
            # If outside VALID_FARM_COORDINATES, it's directly OOB
            neighbor_conditions.append(CONDITION_OUT_OF_BOUNDS) 
    
    teleport_agent(agent_host_instance, current_x + 0.5, original_pos_y, current_z + 0.5)

    state_list = []
    state_list.extend(neighbor_conditions) 
    state_list.append(condition_current_spot)
    return tuple(state_list)




# helper.py
# ... (ILLEGAL_COORD_MARKER defined)

# helper.py

# ... (CONDITION_ constants defined above) ...

def print_intuitive_abstracted_state(state_tuple):
    """
    Prints the abstracted 5-point state tuple in a more human-readable format.
    (condition_N, condition_E, condition_S, condition_W, condition_current_spot)
    """
    if not isinstance(state_tuple, tuple) or len(state_tuple) != 5:
        print("Invalid abstracted state tuple format (expected 5 elements).")
        print("Raw state: {}".format(state_tuple)); return

    cond_N, cond_E, cond_S, cond_W, cond_curr = state_tuple
    
    def format_condition(cond_value):
        if cond_value == CONDITION_MATURE_WHEAT: return " M "
        elif cond_value == CONDITION_IMMATURE_WHEAT: return " I "
        elif cond_value == CONDITION_EMPTY_FARMABLE: return " E " # Empty/Farmable
        elif cond_value == CONDITION_OUT_OF_BOUNDS: return "XXX" # Out of Bounds
        else: return " ? "

    print("--- Agent Abstracted Local State ---")
    print("       ({})      ".format(format_condition(cond_N)))
    print("        ^        ")
    print("({}) <-- ({}) --> ({})".format(format_condition(cond_W),format_condition(cond_curr),format_condition(cond_E)))
    print("        v        ")
    print("       ({})      ".format(format_condition(cond_S)))
    print("------------------------------------")
    print("(M=Mature, I=Immature, E=Empty/Farmable, XXX=OutOfBounds)")





    # Assume VALID_FARM_COORDINATES and ILLEGAL_COORD_MARKER are defined globally
# Assume teleport_agent is defined or imported

def choose_random_valid_adjacent_move(agent_host_instance, current_x, current_z, state_tuple):
    """
    Chooses a random valid cardinal direction to move to from the current position.
    The 'state_tuple' provides information about which adjacent cells are valid.
    State tuple does NOT contain seed information.

    Args:
        agent_host_instance: The MalmoPython.AgentHost object.
        current_x (int): Agent's current X coordinate.
        current_z (int): Agent's current Z coordinate.
        state_tuple (tuple): The state representation:
            (curr_x, curr_z, age_N, age_E, age_S, age_W, age_curr_spot)

    Returns:
        tuple: (new_x, new_z) of the agent's new position after teleporting.
               Returns (current_x, current_z) if no valid moves are found.
    """
    if not isinstance(state_tuple, tuple) or len(state_tuple) != 7: # Length is now 7
        print("ERROR: Invalid state tuple provided to choose_random_valid_adjacent_move (expected 7 elements).")
        return current_x, current_z

    # Unpack relevant parts of the state (ages of neighbors)
    # State: (curr_x_in_state, curr_z_in_state, age_N, age_E, age_S, age_W, age_curr_spot)
    # Indices for neighbor ages: N=2, E=3, S=4, W=5 (these remain the same relative to start of tuple)
    age_N = state_tuple[2]
    age_E = state_tuple[3]
    age_S = state_tuple[4]
    age_W = state_tuple[5]

    potential_moves = [
        ((0, -1), age_N),  # North
        ((1, 0),  age_E),  # East
        ((0, 1),  age_S),  # South
        ((-1, 0), age_W)   # West
    ]

    valid_moves = []
    for (dx, dz), age_at_destination in potential_moves:
        if age_at_destination != ILLEGAL_COORD_MARKER:
            valid_moves.append((current_x + dx, current_z + dz))

    if not valid_moves:
        print("WARNING: No valid adjacent moves found from ({}, {}). Agent will stay put.".format(current_x, current_z))
        return current_x, current_z

    chosen_next_x, chosen_next_z = random.choice(valid_moves)
    teleport_agent(agent_host_instance, chosen_next_x + 0.5, 227.0, chosen_next_z + 0.5)
    print("ACTION: Randomly moved to ({}, {})".format(chosen_next_x, chosen_next_z))
    return chosen_next_x, chosen_next_z














# Assume these are defined:
# agent_host (global or passed in)
# VALID_FARM_COORDINATES (global)
# ILLEGAL_COORD_MARKER (global)
# from qLearn_helper import teleport_agent, get_wheat_age_in_los 
# (or however you access these)

# Helper function: You already have this, make sure it's accessible
# def look_down_harvest_and_replant(agent_host): ... (from previous code)
# def plant_seed(agent_host): ... (from previous code, just sends use 1/ use 0)

def perform_harvest_sequence(agent_host_instance):
    """Simulates harvesting (attacking) the block at the current spot."""
    # Assumes agent is looking down and positioned correctly.
    print("ACTION_HELPER: Performing harvest (attack).")
    agent_host_instance.sendCommand("attack 1")
    # This sleep duration is critical and depends on MsPerTick and game mode (Survival)
    # For wheat in survival, it might take a few hits or a longer press.
    # With MsPerTick=1, 0.2s = 200 ticks. With MsPerTick=50, 0.2s = 4 ticks.
    # Let's make it a bit longer to ensure breaking in survival if MsPerTick is higher.
    time.sleep(0.01) # Adjust this based on observed breaking time
    agent_host_instance.sendCommand("attack 0")
    time.sleep(0.2) # Allow item drops to occur and potentially be picked up

def perform_plant_sequence(agent_host_instance):
    """Simulates planting a seed at the current spot."""
    # Assumes agent is looking down and positioned correctly.
    # Assumes agent is holding seeds.
    agent_host_instance.sendCommand("use 1")
    time.sleep(0.01)
    agent_host_instance.sendCommand("use 0")
    time.sleep(0.1)


# Define the step penalty
STEP_PENALTY = 0.1 # You can tune this value

# ... (perform_harvest_sequence, perform_plant_sequence functions as before) ...


def step(agent_host_instance, action_index, current_x, current_z, current_abstracted_state_tuple):
    base_reward_for_action = 0
    next_x, next_z = current_x, current_z # Agent stays put by default

    # Extract conditions from the state tuple (N, E, S, W, Current_Spot)
    cond_N, cond_E, cond_S, cond_W, condition_at_current_spot = current_abstracted_state_tuple

    move_deltas_and_dest_conditions = {
        ACTION_MOVE_N: ((0, -1), cond_N),
        ACTION_MOVE_E: ((1, 0),  cond_E),
        ACTION_MOVE_S: ((0, 1),  cond_S),
        ACTION_MOVE_W: ((-1, 0), cond_W)
    }

    if action_index in move_deltas_and_dest_conditions:
        (dx, dz), dest_condition = move_deltas_and_dest_conditions[action_index]
        potential_next_x, potential_next_z = current_x + dx, current_z + dz
        
        # A destination is valid for MOVEMENT if its condition was not OUT_OF_BOUNDS
        if dest_condition != CONDITION_OUT_OF_BOUNDS:
            next_x, next_z = potential_next_x, potential_next_z
            teleport_agent(agent_host_instance, next_x + 0.5, 227.0, next_z + 0.5)
        else:
            base_reward_for_action = -0.5 # Penalty for trying to move out of bounds
            # print("INFO: Agent tried to move to OOB spot.")
            
    elif action_index == ACTION_HARVEST_CURRENT:
        if condition_at_current_spot == CONDITION_MATURE_WHEAT:
            base_reward_for_action = 10.0  
            print("INFO: Action Harvest - Harvested mature wheat!")
            perform_harvest_sequence(agent_host_instance) # Only attacks
        elif condition_at_current_spot == CONDITION_IMMATURE_WHEAT:
            base_reward_for_action = -5.0 
            print("INFO: Action Harvest - Penalized for breaking immature wheat.")
            perform_harvest_sequence(agent_host_instance) # Only attacks
        else: # CONDITION_EMPTY_FARMABLE or CONDITION_OUT_OF_BOUNDS (if current somehow became OOB)
            base_reward_for_action = -1.0 
            print("INFO: Action Harvest - Tried to harvest non-wheat/empty/OOB spot.")

    elif action_index == ACTION_PLANT_CURRENT:
        if condition_at_current_spot == CONDITION_EMPTY_FARMABLE: 
            base_reward_for_action = 5.0 # Reward for planting on a suitable empty spot
            print("INFO: Action Plant - Planted seed on empty farmable spot.")
            perform_plant_sequence(agent_host_instance)
        else: # Mature, Immature wheat already present, or current spot is OOB
            base_reward_for_action = -1.0 # Penalty
            print("INFO: Action Plant - Tried to plant on non-empty or unsuitable spot (Cond: {}).".format(condition_at_current_spot))

    elif action_index == ACTION_WAIT:
        time.sleep(0.5) # Adjust sleep based on MsPerTick. This is 0.5 real seconds.
        print("INFO: Action Wait.")
        if condition_at_current_spot == CONDITION_MATURE_WHEAT:
             base_reward_for_action = -0.2 # Small penalty for not harvesting mature wheat
        elif condition_at_current_spot == CONDITION_OUT_OF_BOUNDS:
             base_reward_for_action = -1.0 # Penalty for waiting on an OOB spot (shouldn't happen if moves are valid)


    final_reward = base_reward_for_action - STEP_PENALTY 
    return (next_x, next_z), final_reward





def get_inventory_item_count(agent_host_instance, item_name_to_find):
    """
    Counts the total quantity of a specific item in the agent's main inventory.
    Compatible with older Python versions (no f-strings).
    """
    total_quantity = 0
    # print("DEBUG: Attempting to count '{}'.".format(item_name_to_find)) # You can keep or remove this outer debug
    world_state = agent_host_instance.getWorldState()

    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        # print("DEBUG: Raw observation for inventory: {}".format(msg)) 
        try:
            observations = json.loads(msg)
            
            if "inventory" in observations: # This is for flat="false"
                # print("DEBUG: Found 'inventory' key. Content: {}".format(observations['inventory'])) # You can keep or remove this
                for item_slot in observations["inventory"]:
                    item_type = item_slot.get("type")
                    inventory_source = item_slot.get("inventory")
                    quantity = item_slot.get("quantity", 0)

                    if inventory_source == "inventory" and item_type == item_name_to_find: # <--- THE FIX
                        # print("DEBUG: MATCH! Adding {} of {} from player inventory.".format(quantity, item_name_to_find)) # Optional match print
                        total_quantity += quantity
            else:
                # Fallback for flat=true format (though your log shows flat=false is working)
                # print("DEBUG: 'inventory' key (for flat=false) NOT found. Checking for flat=true format...")
                found_in_flat_format = False
                for i in range(40): 
                    item_key = "InventorySlot_{}_item".format(i)
                    size_key = "InventorySlot_{}_size".format(i)
                    if item_key in observations and observations[item_key] == item_name_to_find:
                        current_quantity_str = observations.get(size_key, "0")
                        try:
                            current_quantity = int(current_quantity_str)
                        except ValueError:
                            # print("WARNING: Could not convert flat inventory size '{}' to int for slot {}.".format(current_quantity_str, i))
                            current_quantity = 0
                        total_quantity += current_quantity
                        found_in_flat_format = True
                
                if not found_in_flat_format:
                    available_keys = []
                    if isinstance(observations, dict): 
                        available_keys = list(observations.keys())
                    # print("DEBUG: Item '{}' not found in any known inventory format. Available keys in observation: {}".format(item_name_to_find, available_keys))


        except json.JSONDecodeError:
            # print("ERROR: JSONDecodeError while parsing inventory: {}".format(msg))
            return 0 
        except Exception as e:
            # print("ERROR: {} while processing inventory: {}".format(type(e).__name__, e))
            return 0
    # else:
        # print("DEBUG: No new observations received for inventory check.")

    # print("DEBUG: Final count for '{}': {}".format(item_name_to_find, total_quantity)) # You can keep or remove this
    return total_quantity



def get_ticks_since_mission_start(agent_host_instance):
    """
    Gets the number of game ticks the agent has been alive in the current mission.

    Args:
        agent_host_instance: The MalmoPython.AgentHost object.

    Returns:
        int: The value of "TimeAlive" from observations, or -1 if not found or error.
    """
    ticks_alive = -1
    world_state = agent_host_instance.getWorldState()

    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        try:
            observations = json.loads(msg)
            if "TimeAlive" in observations:
                ticks_alive = observations["TimeAlive"] 
                # TimeAlive is usually an integer number of ticks.
        except json.JSONDecodeError:
            print("ERROR: JSONDecodeError while getting TimeAlive: {}".format(msg))
            return -1 
        except Exception as e:
            print("ERROR: {} while getting TimeAlive: {}".format(type(e).__name__, e))
            return -1
    return ticks_alive