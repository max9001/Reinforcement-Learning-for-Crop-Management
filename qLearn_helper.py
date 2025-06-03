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
ACTION_MOVE = 0
ACTION_HARVEST = 1
ACTION_PLANT = 2

ACTIONS_LIST = [ACTION_MOVE, ACTION_HARVEST, ACTION_PLANT]

ACTION_NAMES = {
    ACTION_MOVE: "Move",
    ACTION_HARVEST: "Harvest",
    ACTION_PLANT: "Plant"
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



# VALID_FARM_COORDINATES and ILLEGAL_COORD_MARKER should still be defined globally
# from qLearn_helper import get_wheat_age_in_los, teleport_agent
# (Assuming these are in qLearn_helper.py or defined in the same file)

def get_state_active_scan_5_points(agent_host_instance, current_x, current_z):
    """
    Gets the state by actively checking the current cell and its 4 cardinal neighbors.
    State: (current_x, current_z, age_N, age_E, age_S, age_W, age_current_spot)
    NO SEED INFORMATION INCLUDED.
    """
    original_pos_y = 227.0 # Agent's standing Y level

    # Define relative offsets for N, E, S, W (relative to current agent position)
    # Order: North, East, South, West
    cardinal_offsets = [
        (0, -1),  # North (Z decreases)
        (1, 0),   # East  (X increases)
        (0, 1),   # South (Z increases)
        (-1, 0)   # West  (X decreases)
    ]

    neighbor_ages = [] # To store ages of N, E, S, W

    # Make agent look down before starting scans
    agent_host_instance.sendCommand("setPitch 90") 
    time.sleep(0.1) # Allow pitch to settle

    # 1. Get age at the agent's current spot first
    age_current_spot = get_wheat_age_in_los(agent_host_instance)
    # Normalize error codes from get_wheat_age_in_los to -1 for simplicity in state
    age_current_spot = age_current_spot if age_current_spot is not None and age_current_spot >= 0 else -1


    # 2. Scan the 4 cardinal neighbors
    for dx, dz in cardinal_offsets:
        neighbor_x = current_x + dx
        neighbor_z = current_z + dz

        if (neighbor_x, neighbor_z) in VALID_FARM_COORDINATES:
            teleport_agent(agent_host_instance, neighbor_x + 0.5, original_pos_y, neighbor_z + 0.5)
            age = get_wheat_age_in_los(agent_host_instance)
            neighbor_ages.append(age if age is not None and age >= 0 else -1) 
        else:
            neighbor_ages.append(ILLEGAL_COORD_MARKER)
    
    # 3. Teleport back to the original position
    teleport_agent(agent_host_instance, current_x + 0.5, original_pos_y, current_z + 0.5)
    # Agent should still be looking down from the initial setPitch 90.

    # Construct the state tuple in a consistent order:
    # (current_x, current_z, age_N, age_E, age_S, age_W, age_current_spot)
    state_list = [current_x, current_z]
    state_list.extend(neighbor_ages) # Adds the 4 neighbor ages
    state_list.append(age_current_spot) 
    
    return tuple(state_list)





# Assume ILLEGAL_COORD_MARKER is defined globally

def print_intuitive_state_5_points(state_tuple):
    """
    Prints the 5-point state tuple (without seed info) in a more human-readable format.
    Assumes state_tuple format:
    (current_x, current_z, age_N, age_E, age_S, age_W, age_current_spot)
    """
    if not isinstance(state_tuple, tuple) or len(state_tuple) != 7: # Length is now 7
        print("Invalid state tuple format for intuitive printing (expected 7 elements).")
        print("Raw state: {}".format(state_tuple))
        return

    current_x, current_z, age_N, age_E, age_S, age_W, age_current_spot = state_tuple
    
    # Helper to format age or illegal marker
    def format_age(age_value):
        if age_value == ILLEGAL_COORD_MARKER:
            return "XXX"  # Indicates out of bounds / illegal
        elif age_value == -1: # Specifically for "not wheat" or "no age property" as normalized by get_state
            return "-1"   # Display as "-1"
        elif age_value < -1: # For other potential negative error codes from get_wheat_age_in_los if they existed
            return "ERR"  # Or some other error indicator like "???"
        elif age_value >= 0 and age_value <=7: # Valid wheat age
            return str(age_value)
        else: # Should not happen if get_state normalizes properly
            return "???"


    print("--- Agent State (5-Point Scan) ---")
    print("Current Position: ({}, {})".format(current_x, current_z))
    # "Has Seeds" line removed
    print("Wheat Ages:")
    print("        ({})       ".format(format_age(age_N)))                 # North
    print("         ^         ")
    print(" ({}) <-- ({}) --> ({}) ".format(
        format_age(age_W),      # West
        format_age(age_current_spot), # Current
        format_age(age_E)       # East
    ))
    print("         v         ")
    print("        ({})       ".format(format_age(age_S)))                 # South
    print("------------------------------------")





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


def step(agent_host_instance, action_index, current_x, current_z, current_state_tuple): # Added agent_host_instance
    """
    Executes an action, calculates reward, and determines next position.
    """
    # global agent_host # REMOVE THIS LINE

    reward = 0
    next_x, next_z = current_x, current_z
    age_at_current_spot = current_state_tuple[2] 


    if action_index == ACTION_MOVE:
        # Randomly pick a valid direction
        possible_moves = [ (0, -1), (1, 0), (0, 1), (-1, 0) ]
        random.shuffle(possible_moves)
        for dx, dz in possible_moves:
            nx, nz = current_x + dx, current_z + dz
            if (nx, nz) in VALID_FARM_COORDINATES:
                next_x, next_z = nx, nz
                teleport_agent(agent_host_instance, next_x + 0.5, 227.0, next_z + 0.5)
                break
            print("INFO: Action Move - Invalid move to ({}, {}).".format(nx, nz))
    elif action_index == ACTION_HARVEST:
        if age_at_current_spot == 7:
            reward = 50
            print("INFO: Action Harvest - Harvested mature wheat! (age {})".format(age_at_current_spot))
            perform_harvest_sequence(agent_host_instance) # Pass agent_host_instance
        elif age_at_current_spot >= 0 and age_at_current_spot < 7:
            reward = -40
            print("INFO: Action Harvest - Penalized for breaking immature wheat (age {}).".format(age_at_current_spot))
            perform_harvest_sequence(agent_host_instance) # Pass agent_host_instance
        else: 
            reward = -20
            print("INFO: Action Harvest - Tried to harvest empty spot (age {}).".format(age_at_current_spot))
    elif action_index == ACTION_PLANT:
        if age_at_current_spot == -1:
            reward = 50
            print("INFO: Action Plant - Planted seed on empty spot.")
            perform_plant_sequence(agent_host_instance) # Pass agent_host_instance
        else: 
            reward = -20
            print("INFO: Action Plant - Tried to plant on non-empty/unsuitable spot (age {}).".format(age_at_current_spot))

    return (next_x, next_z), reward




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

# Instead of get_state_active_scan_5_points, use:
def get_simple_state(agent_host, x, z):
    age = get_wheat_age_in_los(agent_host)
    return (age,)