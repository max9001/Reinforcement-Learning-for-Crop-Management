import matplotlib.pyplot as plt
import numpy as np

# Data points (as provided)
efficient_run1 = [(24567, 0), (60274, 14), (103184, 38), (151842, 70), (190363, 88),
                  (241983, 124), (280587, 142), (330709, 176), (374252, 201),
                  (421568, 231), (465878, 257), (508777, 281), (558081, 314)]
efficient_run2 = [(19848, 0), (44804, 8), (74429, 25), (105179, 44), (136847, 65),
                  (172288, 93), (201455, 109), (233784, 131), (266046, 153),
                  (299358, 177), (330004, 196), (362278, 218), (392935, 238),
                  (425164, 259), (456331, 279), (489433, 302), (521268, 323),
                  (551518, 341), (582800, 361)]
random_run1 = [(30931, 0), (63593, 1), (96562, 5), (128260, 6), (159938, 10),
               (191450, 12), (222892, 14), (255482, 16), (287660, 21), (319120, 23),
               (350471, 25), (381754, 26), (414058, 27), (446414, 30),
               (478328, 32), (509804, 32), (540524, 32), (572020, 34)]
random_run2 = [(31230, 0), (63529, 0), (95250, 4), (127629, 6), (161317, 10),
               (192208, 12), (224676, 12), (256884, 14), (287609, 15),
               (319149, 18), (351978, 22), (384452, 24), (416092, 25),
               (449353, 28), (480982, 29), (512837, 30), (545648, 34), (577518, 35)]
wait_run1 = [(100175, 39), (206193, 87), (310975, 133), (415864, 179), (521806, 227)]
wait_run2 = [(97770, 36), (202105, 83), (306558, 130), (410380, 176), (513975, 222)]

q_learning_wheat_per_episode = [0,4,9,5,10,4,5,4,3,3,3,8,3,1,2,8,4,5,4,5,8,3,2,4,8,2,6,5,3,7,1,3,3,4,1,2,3,2,6,2,3,3,3,3,4,9,3,4,6,4,4,2,6,6,2,2,3,1,4,2,3,2,6,3,3,4,4,0,4,6,1,5,5,6,5,3,4,3,2,6,3,0,2,3,7,4,4,6,4,5,4,3,1,4,3,0,4,9,7,2,5,7,6,7,3,2,4,7,4,5,3,5,2,2,4,6,4,4,4,7,5,4,3,3,5,5,7,3,3,3,7,6,1,5,3,5,4,6,6,5,5,7,5,6,3,4,3,4,5,3,4,6,6,4,4,9,5,2,6,4,5,6,2,4,7,3,3,3,5,6,6,2,4,7,9,5,3,4,4,3,6,3,1,3,6,5,3,3,5,8,6,6,4,6,2,6,8,8,9,7,6,6,4,4,4,6,7,8,4,3,8,3,6,3,5,5,5,3,2,6,7,2,7,10,6,7,5,4,9,2,6,7,4,7,4,3,4,9,2,5,6,5,3,5,3,5,7,3,8,4,1,5,5,9,5,3,7,6,3,4,3,5,2,4,7,8,6,7,4,6,4,8,6,4,4,5,3,6,6,5,3,4,4,7,5,8,8,7,0,5,7,5,4,7,3,2,7,4,4,6,9,3,7,6,4,3,4,5,7,5,5,6,8,1,7,9,8,7,7,6,7,3,0,10,10,3,6,10,10,6,3,3,2,6,5,5,3,11,11,4,6,3,6,4,6,5,8,5,6,9,8,3,6,6,5,4,5,7,4,3,9,6,4,2,6,5,6,2,7,5,3,13,7,6,4,8,2,6,5,5,6,6,4,3,6,9,0,7,8,9,2,4,5,2,8,6,4,8,7,4,7,9,4,7,8,6,6,4,9,6,6,5,7,3,9,8,6,4,6,9,5,8,5,1,8,4,4,6,8,3,6,8,4,9,5,4,8,5,9,6,3,7,5,6,7,6,5,4,5,11,3,10,5,5,6,6,5,3,9,9,7,8,5,6,8,8,5,7,8,7,6,4,5,5,5,2,6,3,10,4,6,11,7,5,7,6,10,2,8,13,7,8,5,8,4,10,10,9,6,5,10,4,5,1,13,5,13,9,2,7,7,8,10,8,5,8,4,6,7,9,9,6,5,9,11,3,4,10,4,8,6,7,10,6,12,6,3,9,8,7,5,5,7,9,9,6,6,2,6,9,7,7,7,5,7,5,9,6,7,7,9,5,6,10,13,5,9,3,6,6,9,6,9,6,5,7,5,7,4,5,9,6,11,4,7,3,8,9,2,3,10,7,12,6,8,1,8,2,6,6,6,10,6,7,5,10,7,9,10,7,9,8,4,5,5,8,5,7,7,5,9,7,5,9,5,4,7,8,7,8,6,12,10,7,5,4,8,3,7,7,4,6,6,6,9,7,7,7,7,4,9,9,5,0,9,9,5,12,8,7,10,9,5,10,4,9,4,7,7,7,9,6,6,5,4,11,6,5,6,6,8,4,6,12,1,6,5,11,9,9,5,9,13,9,8,6,6,8,4,6,10,9,8,5,8,9,9,11,9,7,5,8,6,4,9,11,11,5,7,9,7,10,2,7,5,7,8,7,9,12,10,7,10,8,8,10,10,7,10,9,8,9,9,6,5,7,7,6,11,11,11,8,8,6,11,5,6,9,5,7,9,5,7,7,6,11,7,9,5,7,7,9,2,8,10,9,11,3,8,8,8,11,3,5,11,9,8,6,8,9,8,11,13,7,4,7,7,5,8,9,7,7,7,6,8,7,6,7,10,10,6,12,8,5,4,7,12,5,7,8,7,9,5,9,10,14,6,5,8,9,7,8,14,6,1,9,12,6,11,10,10,10,7,9,10,8,5,5,8,9,4,9,11,11,10,5,8,13,7,4,9,6,13,10,9,6,11,9,5,11,9,16,9,13,6,9,11,10,14,4,13,11,11,4,9,7,11,7,8,12,6,14,7,11,5,10,11,11,3,7,10,7,9,12,8,16,8,8,2,4,15,7,8,13,7,6,12,10,7,8,11,8,12,10,7,16,6,8,11,11,7,5,8,8,13,6,15,7,3,11,10,10,6,11,6,10,15,9,8,10,13,4,8,10,11,7,19,13,14,4,14,8,7,9,13,8,7,12,13,6,12,11,11,17,8,14,13,4,12,7,15,5,8,6,8,8,5,6,11,14,5]
ticks_per_episode_q_learning = 45000 # This is specific to the Q-learning run

# --- Function to convert ticks to episodes and get cumulative wheat ---
def process_data_for_episode_plot(run_data, ticks_per_episode_for_conversion):
    """
    Converts tick-based data to episode-based data.
    run_data is a list of (ticks, cumulative_wheat) tuples.
    Returns (episode_numbers, cumulative_wheat_values)
    """
    if not run_data:
        return np.array([]), np.array([])
    
    episode_numbers = [0] # Start with episode 0, wheat 0
    cumulative_wheat_values = [0]

    for ticks, wheat in run_data:
        # Ensure ticks_per_episode_for_conversion is not zero to avoid DivisionByZeroError
        if ticks_per_episode_for_conversion > 0:
            episode_num = ticks / float(ticks_per_episode_for_conversion)
            episode_numbers.append(episode_num)
            cumulative_wheat_values.append(wheat)
        elif ticks == 0 : # if ticks_per_episode is 0, only use the 0-tick data point if present
             episode_numbers.append(0)
             cumulative_wheat_values.append(wheat)


    # Sort by episode number in case the original tick data wasn't strictly ordered
    # in a way that translates to smooth episode progression after division
    combined = sorted(zip(episode_numbers, cumulative_wheat_values))
    ep_sorted = [item[0] for item in combined]
    w_sorted = [item[1] for item in combined]
    
    return np.array(ep_sorted), np.array(w_sorted)

# --- Process Q-learning data (already episodic) ---
q_episodes = np.arange(0, len(q_learning_wheat_per_episode) + 1) # 0 to N_episodes
q_cumulative_wheat = np.insert(np.cumsum(q_learning_wheat_per_episode), 0, 0)


# --- Process scripted run data for episode plot ---
# We use the Q-learning's ticks_per_episode as a reference unit of "effort"
eff_episodes, eff_cumulative_wheat = process_data_for_episode_plot(efficient_run1 + efficient_run2, ticks_per_episode_q_learning)
rnd_episodes, rnd_cumulative_wheat = process_data_for_episode_plot(random_run1 + random_run2, ticks_per_episode_q_learning)
wtt_episodes, wtt_cumulative_wheat = process_data_for_episode_plot(wait_run1 + wait_run2, ticks_per_episode_q_learning)


# --- Define the x-axis range for plotting all fits (now in episodes) ---
all_x_episodes = np.concatenate((eff_episodes, rnd_episodes, wtt_episodes, q_episodes))
if len(all_x_episodes) == 0 or np.max(all_x_episodes) == 0 :
    max_ep_plot = 100 # Fallback max episodes if no data
else:
    max_ep_plot = np.max(all_x_episodes)
x_vals_episodes_for_plot = np.linspace(0, max_ep_plot * 1.05, 500) # Extend slightly


# --- Fit lines (using episode numbers as x-axis) ---
# Helper function for fitting to avoid repetitive try-except for RankWarning
def fit_poly_robust(x, y, deg, fallback_deg=1):
    if len(np.unique(x)) < deg + 1 : # Not enough unique points for desired degree
        if len(np.unique(x)) < fallback_deg +1: # Not enough for fallback either
            print(f"Warning: Not enough unique points in x for even degree {fallback_deg} fit. Returning None for fit.")
            return None
        print(f"Warning: Not enough unique points for degree {deg} fit. Trying degree {fallback_deg}.")
        deg = fallback_deg
    
    try:
        coeffs = np.polyfit(x, y, deg)
        return np.poly1d(coeffs)
    except np.RankWarning:
        print(f"RankWarning for degree {deg} fit. Trying degree {fallback_deg} if different.")
        if deg != fallback_deg and len(np.unique(x)) >= fallback_deg + 1:
            try:
                coeffs = np.polyfit(x, y, fallback_deg)
                return np.poly1d(coeffs)
            except np.RankWarning:
                print(f"RankWarning even for degree {fallback_deg} fit. Returning None.")
                return None
        else: # Already tried fallback or fallback is not possible
            print(f"Cannot fit with degree {deg} or {fallback_deg}. Returning None.")
            return None
    except Exception as e:
        print(f"Error during polyfit: {e}. Returning None.")
        return None


eff_poly = fit_poly_robust(eff_episodes, eff_cumulative_wheat, 1) # Linear for scripted
rnd_poly = fit_poly_robust(rnd_episodes, rnd_cumulative_wheat, 1) # Linear for scripted
wtt_poly = fit_poly_robust(wtt_episodes, wtt_cumulative_wheat, 1) # Linear for scripted

# Q-learning: try quadratic then linear
q_poly = fit_poly_robust(q_episodes, q_cumulative_wheat, 2, fallback_deg=1)


# --- Create plot ---
plt.figure(figsize=(14, 9))

# Plot fitted lines ONLY
if eff_poly: plt.plot(x_vals_episodes_for_plot, eff_poly(x_vals_episodes_for_plot), 'g-', label='Efficient Trend')
if rnd_poly: plt.plot(x_vals_episodes_for_plot, rnd_poly(x_vals_episodes_for_plot), 'b-', label='Random Trend')
if wtt_poly: plt.plot(x_vals_episodes_for_plot, wtt_poly(x_vals_episodes_for_plot), 'r-', label='Wait Trend')
if q_poly:   plt.plot(x_vals_episodes_for_plot, q_poly(x_vals_episodes_for_plot), 'm-', label=f'Q-Learning Trend (Fit Deg {len(q_poly.coeffs)-1})')


plt.title("Trend Comparison: Cumulative Wheat vs. 'Effort Units' (Episodes)", fontsize=16)
plt.xlabel(f"Effort Units (1 unit = {ticks_per_episode_q_learning} ticks, approx. 1 QL Episode)", fontsize=14)
plt.ylabel("Cumulative Wheat Collected", fontsize=14)
plt.legend(fontsize=10)
plt.grid(True)
plt.tight_layout()

# Adjust y-axis limits
all_y_data_cumulative = np.concatenate((
    eff_cumulative_wheat if len(eff_cumulative_wheat)>0 else [0], 
    rnd_cumulative_wheat if len(rnd_cumulative_wheat)>0 else [0], 
    wtt_cumulative_wheat if len(wtt_cumulative_wheat)>0 else [0], 
    q_cumulative_wheat if len(q_cumulative_wheat)>0 else [0]
))
if len(all_y_data_cumulative) > 0:
    min_observed_y = np.min(all_y_data_cumulative)
    max_observed_y = np.max(all_y_data_cumulative)
    current_ax = plt.gca()
    current_ax.set_ylim(
        bottom=min(0, min_observed_y - 0.1 * abs(min_observed_y if min_observed_y !=0 else -1)), # Ensure a bit of space below 0 if data is around 0
        top=max_observed_y * 1.1 if max_observed_y > 0 else 10 # Ensure some positive range if max is 0
    )


# Save the plot
plot_filename_comparison = "wheat_collection_trends_by_episode_equivalent.png"
plt.savefig(plot_filename_comparison)
print(f"Trend comparison plot (by episode equivalent) saved to {plot_filename_comparison}")

plt.show()