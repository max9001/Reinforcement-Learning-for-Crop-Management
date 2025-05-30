import json
import time
import random

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



def find_seeds_slot(agent_host):
    """
    Returns the hotbar slot (1-9) containing wheat_seeds, or None if not found.
    Looks for InventorySlot_{i}_item == "wheat_seeds" for i in 0..8.
    """
    world_state = agent_host.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        obs = json.loads(msg)
        for i in range(9):  # Hotbar slots 0-8
            if obs.get("InventorySlot_{i}_item".format(i = i)) == "wheat_seeds":
                return i + 1  # Malmo hotbar commands are 1-indexed
    return None


def iterate_through_farm(agent_host):
    """
    **************************
    Most efficient Benchmark!!
    **************************
    
    Example usage:
    
    # --- Agent Action Sequence ---
    agent_host.sendCommand("setPitch 90")
    time.sleep(0.2)

    for _ in range(num_steps):
        iterate_through_farm(agent_host)

    
    Iterates the agent through predefined wheat locations on the farm by teleporting.
    The agent is positioned at Y=227, centered on the X and Z of each wheat block.

    Args:
        agent_host_instance: The MalmoPython.AgentHost object.
    """
    wheat_locations = [
        # Row X = -3
        (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0),
        # Row X = -2
        (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0),
        # Row X = -1
        (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0),    
        # Row X = 0 (note the gap at Z = -3)
        (0, -6), (0, -5), (0, -4),           (0, -2), (0, -1), (0, 0),
        # Row X = 1
        (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0),
        # Row X = 2
        (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0),
        # Row X = 3
        (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0),
    ]

    agent_y_position = 227.0  # Agent stands on the same level as the wheat plants

    print("Starting farm iteration by teleporting...")
    for x_wheat, z_wheat in wheat_locations:
        # Calculate agent's target position to be centered on the block
        agent_target_x = x_wheat + 0.5
        agent_target_z = z_wheat + 0.5
        
        age = get_wheat_age_in_los(agent_host)
        
        if age == 7:
            
            look_down_harvest_and_replant(agent_host)
                
            time.sleep(0.2)
            
        teleport_agent(agent_host, agent_target_x, agent_y_position, agent_target_z)

    print("Farm iteration complete.")


def perform_random_teleport_step(agent_host, current_x, current_z, agent_y=227.0):
    """
    Performs a single random walk step by teleporting the agent one unit
    in a random cardinal direction (North, South, East, West) from its
    current X, Z position. Avoids teleporting to the forbidden water block.

    The agent is teleported to be centered on the new block (X_new + 0.5, Z_new + 0.5).

    Args:
        agent_host_instance: The MalmoPython.AgentHost object.
        current_x (float): The agent's current logical X coordinate (e.g., -1.0, 0.0, 1.0).
                           Assumed to be the center of a block if it ends in .0,
                           or already adjusted if it ends in .5.
                           The function will normalize this to the block's base X.
        current_z (float): The agent's current logical Z coordinate.
        agent_y (float, optional): The Y level at which the agent should be teleported.
                                   Defaults to 227.0.

    Returns:
        tuple: (new_x_logical, new_z_logical) representing the new logical
               block coordinates after the random step. If no valid move
               is possible (e.g., surrounded by the forbidden block or edges
               if you add boundary checks), it returns the original coordinates.
    """
    base_current_x = int(round(current_x - 0.5)) if isinstance(current_x, float) and current_x % 1 != 0 else int(current_x)
    base_current_z = int(round(current_z - 0.5)) if isinstance(current_z, float) and current_z % 1 != 0 else int(current_z)

    possible_moves = [
        (0, 1),   # Move South (positive Z)
        (0, -1),  # Move North (negative Z)
        (1, 0),   # Move East (positive X)
        (-1, 0)   # Move West (negative X)
    ]
    random.shuffle(possible_moves)  # Shuffle to try directions in a random order

    forbidden_x, forbidden_y, forbidden_z = 0, 227, -3 # The water block to avoid

    for dx, dz in possible_moves:
        next_logical_x = base_current_x + dx
        next_logical_z = base_current_z + dz

        if next_logical_x == forbidden_x and next_logical_z == forbidden_z:
            continue  # Skip this move, try the next random direction

        farm_min_x, farm_max_x = -3, 3
        farm_min_z, farm_max_z = -6, 0
        if not (farm_min_x <= next_logical_x <= farm_max_x and \
                farm_min_z <= next_logical_z <= farm_max_z):
            continue

        # Calculate agent's actual teleport target (centered on the new block)
        agent_teleport_x = next_logical_x + 0.5
        agent_teleport_z = next_logical_z + 0.5
        teleport_agent(agent_host, agent_teleport_x, agent_y, agent_teleport_z)
        
        return next_logical_x, next_logical_z # Return the new logical block coordinates
    return base_current_x, base_current_z # Return original logical coords if no move was made  
    


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

def wait_10mins_method(agent_host, waiting_time=12, num_steps=5):
    """
    Waits for a specified time (default 10 minutes) before starting the iteration.
    """
    agent_host.sendCommand("setPitch 90")
    time.sleep(0.2)
    for _ in range(num_steps):
        time.sleep(waiting_time)
        iterate_through_farm(agent_host)
    
        
def iteration_method(agent_host, num_steps=10):
    agent_host.sendCommand("setPitch 90")
    time.sleep(0.2)
    for _ in range(num_steps):
        iterate_through_farm(agent_host)


def random_method(agent_host, num_steps=10):
    """
    Randomly teleports the agent to a new location within the farm area.
    The agent is teleported to be centered on the new block (X_new + 0.5, Z_new + 0.5).
    """
    agent_host.sendCommand("setPitch 90")
    time.sleep(0.01)

    teleport_agent(agent_host, 0.5, 227, -2.5)
    current_x = 0
    current_z = -3

    for _ in range(num_steps):
        time.sleep(0.5)
        
        choice = random.randint(1, 3)

        if choice == 1:
            attack(agent_host)

        elif choice == 2:
            plant_seed(agent_host)
        elif choice == 3:
            current_x, current_z = perform_random_teleport_step(agent_host, current_x, current_z)

    
def get_state(agent_host):
    """
    Returns the current state of the agent based on its inventory and position.
    """
    agent_host.sendCommand("setPitch 90")
    num_wheat = 0
    wheat_locations = [
        # Row X = -3
        (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0),
        # Row X = -2
        (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0),
        # Row X = -1
        (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0),    
        # Row X = 0 (note the gap at Z = -3)
        (0, -6), (0, -5), (0, -4),           (0, -2), (0, -1), (0, 0),
        # Row X = 1
        (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0),
        # Row X = 2
        (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0),
        # Row X = 3
        (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0),
    ]

    agent_y_position = 227.0  # Agent stands on the same level as the wheat plants

    for x_wheat, z_wheat in wheat_locations:
        # Calculate agent's target position to be centered on the block
        agent_target_x = x_wheat + 0.5
        agent_target_z = z_wheat + 0.5
        
        age = get_wheat_age_in_los(agent_host)
        
        if age == 7:
            
            num_wheat += 1
            
        teleport_agent(agent_host, agent_target_x, agent_y_position, agent_target_z)

    return num_wheat

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


def get_wheat_count(agent_host):
    """
    Returns the number of wheat
    """
    agent_host.sendCommand("setPitch 90")
    total = 0
    world_state = agent_host.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        try:
            obs_text = world_state.observations[-1].text
            obs = json.loads(obs_text)
            for i in range(36):
                item_key = "InventorySlot_{}_item".format(i)
                size_key = "InventorySlot_{}_size".format(i)
                if obs.get(item_key) == "wheat":
                    total += obs.get(size_key, 0)
        except Exception as e:
            print("Error reading inventory:", e)
    return total


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