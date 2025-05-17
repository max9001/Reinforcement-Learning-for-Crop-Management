import json


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