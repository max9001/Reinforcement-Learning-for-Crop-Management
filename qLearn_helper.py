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
                            return -1  # Indicate error in age property format
                    else:
                        # print("Debug: 'prop_age' not found in LineOfSight for wheat.")
                        return -1  # Wheat, but no age property (shouldn't happen for vanilla wheat if F3 shows it)
                else:
                    # print("Debug: Not looking at a wheat block.")
                    return -1  # Not looking at wheat
            else:
                # print("Debug: 'LineOfSight' not in current observations.")
                return -1  # No LineOfSight data
        except json.JSONDecodeError:
            #             print("Error decoding JSON for LineOfSight observation:", msg)
            return -2  # Indicate JSON error
        except Exception as e:
            #             print(f"Error processing LineOfSight observation: {e}")
            return -2  # Indicate other processing error
    else:
        # print("Debug: No new observations since last state.")
        return -1  # No new observations


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