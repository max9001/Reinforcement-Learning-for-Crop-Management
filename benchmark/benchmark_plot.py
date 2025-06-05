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




# ==========================================================================================

# COPY AND PASTE OUTPUT FROM SCRIPT HERE

# New data for the "new_method" (Q-learning or other)
new_method_wheat_per_episode = [1, 21, 14, 25, 20, 25, 18]
ticks_per_episode_new_method = 45000

# --- Function to process episodic data into (ticks, cumulative_wheat) ---
def process_episodic_data_to_cumulative_ticks(wheat_per_episode, ticks_per_episode_val):
    """
    Converts list of wheat collected per episode into (ticks, cumulative_wheat) data.
    """
    if not wheat_per_episode: # Handle empty list
        return np.array([0]), np.array([0])

    cumulative_wheat = np.cumsum(wheat_per_episode)
    # Tick values: Episode 1 ends at ticks_per_episode_val, Ep 2 at 2*ticks_per_episode_val, etc.
    # Start with (0 ticks, 0 wheat)
    tick_values = [0] + [ (i + 1) * ticks_per_episode_val for i in range(len(wheat_per_episode)) ]
    cumulative_wheat_for_plot = np.insert(cumulative_wheat, 0, 0) # Add 0 at the beginning for (0,0) point
    return np.array(tick_values), cumulative_wheat_for_plot

# Process the new method's data
nm_x_ticks, nm_y_cumulative_wheat = process_episodic_data_to_cumulative_ticks(
    new_method_wheat_per_episode, ticks_per_episode_new_method
)

# --- Combine runs by category (existing code) ---
def combine_runs(*runs):
    x = []
    y = []
    for run in runs:
        for xi, yi in run:
            x.append(xi)
            y.append(yi)
    # Sort by x values to ensure line plot is drawn correctly
    if not x: # Handle case where runs might be empty
        return np.array([]), np.array([])
    combined = sorted(zip(x,y))
    x_sorted = [item[0] for item in combined]
    y_sorted = [item[1] for item in combined]
    return np.array(x_sorted), np.array(y_sorted)

# Combine all existing data
eff_x, eff_y = combine_runs(efficient_run1, efficient_run2)
rnd_x, rnd_y = combine_runs(random_run1, random_run2)
wtt_x, wtt_y = combine_runs(wait_run1, wait_run2)


# --- Fit lines ---
# Helper function for fitting to avoid repetitive try-except for RankWarning
def fit_poly_robust(x_data, y_data, target_deg, fallback_deg=1):
    if len(x_data) == 0 or len(y_data) == 0: # Cannot fit empty data
        print(f"Warning: Empty data provided for fitting. Returning None.")
        return None
    
    unique_x = np.unique(x_data)
    
    current_deg = target_deg
    if len(unique_x) < current_deg + 1:
        print(f"Warning: Not enough unique points for degree {current_deg} fit. Trying degree {fallback_deg}.")
        current_deg = fallback_deg
        if len(unique_x) < current_deg + 1:
            print(f"Warning: Not enough unique points for even degree {current_deg} fit. Returning None.")
            return None
    try:
        coeffs = np.polyfit(x_data, y_data, current_deg)
        return np.poly1d(coeffs)
    except (np.RankWarning, np.linalg.LinAlgError) as e: # Catch RankWarning and other linalg errors
        print(f"Fitting error (e.g., RankWarning or LinAlgError) for degree {current_deg} fit: {e}.")
        if current_deg != fallback_deg and len(unique_x) >= fallback_deg + 1:
            print(f"Trying fallback degree {fallback_deg}.")
            try:
                coeffs = np.polyfit(x_data, y_data, fallback_deg)
                return np.poly1d(coeffs)
            except (np.RankWarning, np.linalg.LinAlgError) as e2:
                print(f"Fitting error even for fallback degree {fallback_deg}: {e2}. Returning None.")
                return None
        else:
            print(f"Cannot fit with degree {current_deg} or fallback is not viable. Returning None.")
            return None
    except Exception as e_gen:
        print(f"General error during polyfit: {e_gen}. Returning None.")
        return None

# Fit existing data (using quadratic as before, robust fit will handle if linear is better)
eff_poly = fit_poly_robust(eff_x, eff_y, 2)
rnd_poly = fit_poly_robust(rnd_x, rnd_y, 2)
wtt_poly = fit_poly_robust(wtt_x, wtt_y, 2)

# Fit new method data (try quadratic, fallback to linear)
nm_poly = fit_poly_robust(nm_x_ticks, nm_y_cumulative_wheat, 2)


# --- Create plot ---
plt.figure(figsize=(12, 8))

# Scatter plots for all data series
if len(eff_x) > 0: plt.scatter(eff_x, eff_y, color='green', label='Efficient', alpha=0.6, s=30)
if len(rnd_x) > 0: plt.scatter(rnd_x, rnd_y, color='blue', label='Random', alpha=0.6, s=30)
if len(wtt_x) > 0: plt.scatter(wtt_x, wtt_y, color='red', label='Wait', alpha=0.6, s=30)
if len(nm_x_ticks) > 0: plt.scatter(nm_x_ticks, nm_y_cumulative_wheat, color='purple', label='New Method', alpha=0.7, s=40, marker='x')


# Define x_vals for plotting fitted lines, encompassing all data
all_x_for_plot_range = np.concatenate((eff_x, rnd_x, wtt_x, nm_x_ticks))
if len(all_x_for_plot_range) > 0:
    min_plot_x, max_plot_x = 0, np.max(all_x_for_plot_range)
    x_vals_plot = np.linspace(min_plot_x, max_plot_x * 1.05, 500) # Extend slightly
else:
    x_vals_plot = np.linspace(0, 600000, 500) # Fallback if no data

# Plot fitted lines
if eff_poly: plt.plot(x_vals_plot, eff_poly(x_vals_plot), 'g--', label=f'Efficient Fit (Deg {len(eff_poly.coeffs)-1})')
if rnd_poly: plt.plot(x_vals_plot, rnd_poly(x_vals_plot), 'b--', label=f'Random Fit (Deg {len(rnd_poly.coeffs)-1})')
if wtt_poly: plt.plot(x_vals_plot, wtt_poly(x_vals_plot), 'r--', label=f'Wait Fit (Deg {len(wtt_poly.coeffs)-1})')
if nm_poly:  plt.plot(x_vals_plot, nm_poly(x_vals_plot), 'm--', label=f'New Method Fit (Deg {len(nm_poly.coeffs)-1})')


plt.title("Wheat Collected vs Time Elapsed (Ticks)", fontsize=16)
plt.xlabel("Time Elapsed (ticks)", fontsize=14)
plt.ylabel("Cumulative Wheat Collected", fontsize=14)
plt.legend(fontsize=10)
plt.grid(True)
plt.tight_layout()

# Adjust y-axis limits for better visualization
all_y_for_plot_range = np.concatenate((eff_y, rnd_y, wtt_y, nm_y_cumulative_wheat))
if len(all_y_for_plot_range) > 0:
    min_plot_y = np.min(all_y_for_plot_range)
    max_plot_y = np.max(all_y_for_plot_range)
    plt.ylim(min(0, min_plot_y - 0.1 * abs(min_plot_y if min_plot_y !=0 else -1)), 
             max_plot_y * 1.1 if max_plot_y > 0 else 10)


# Save the plot
plot_filename_comparison = "wheat_collection_comparison_with_new_method.png"
plt.savefig(plot_filename_comparison)
print(f"Comparison plot saved to {plot_filename_comparison}")

plt.show()