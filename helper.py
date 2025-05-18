import json
import time

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
                            print(f"Warning: Could not convert prop_age '{age_str}' to int.")
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
            print("Error decoding JSON for LineOfSight observation:", msg)
            return -2 # Indicate JSON error
        except Exception as e:
            print(f"Error processing LineOfSight observation: {e}")
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

def look_down_harvest_and_replant(agent_host):
    """
    Makes the agent look straight down, harvest the wheat, and replant seeds.
    Dynamically finds the hotbar slot with seeds.
    """
    # Look straight down
    agent_host.sendCommand("setPitch 90")
    time.sleep(0.2)

    # Harvest (attack)
    agent_host.sendCommand("attack 1")
    time.sleep(0.2)
    agent_host.sendCommand("attack 0")
    time.sleep(2)

    # Find seeds in hotbar
    slot = find_seeds_slot(agent_host)
    if slot is not None:
        agent_host.sendCommand("hotbar.{slot} 1".format(slot=slot))
        agent_host.sendCommand("hotbar.{slot} 0".format(slot=slot))
        time.sleep(0.1)
        # Replant (use seeds)
        agent_host.sendCommand("use 1")
        time.sleep(0.2)
        agent_host.sendCommand("use 0")
        time.sleep(0.1)
    else:
        print("No seeds found in hotbar to replant!")