import matplotlib.pyplot as plt
import numpy as np

# Data points
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

# Combine runs by category
def combine_runs(*runs):
    x = []
    y = []
    for run in runs:
        for xi, yi in run:
            x.append(xi)
            y.append(yi)
    return np.array(x), np.array(y)

# Combine all data
eff_x, eff_y = combine_runs(efficient_run1, efficient_run2)
rnd_x, rnd_y = combine_runs(random_run1, random_run2)
wtt_x, wtt_y = combine_runs(wait_run1, wait_run2)

# Fit lines (quadratic if fits better)
eff_fit = np.polyfit(eff_x, eff_y, 2)
rnd_fit = np.polyfit(rnd_x, rnd_y, 2)
wtt_fit = np.polyfit(wtt_x, wtt_y, 2)

eff_poly = np.poly1d(eff_fit)
rnd_poly = np.poly1d(rnd_fit)
wtt_poly = np.poly1d(wtt_fit)

# Create plot
plt.figure(figsize=(12, 8))
plt.scatter(eff_x, eff_y, color='green', label='Efficient', alpha=0.6)
plt.scatter(rnd_x, rnd_y, color='blue', label='Random', alpha=0.6)
plt.scatter(wtt_x, wtt_y, color='red', label='Wait', alpha=0.6)

x_vals = np.linspace(0, 600000, 500)
plt.plot(x_vals, eff_poly(x_vals), 'g--', label='Efficient Fit')
plt.plot(x_vals, rnd_poly(x_vals), 'b--', label='Random Fit')
plt.plot(x_vals, wtt_poly(x_vals), 'r--', label='Wait Fit')

plt.title("Wheat Collected vs Time Elapsed")
plt.xlabel("Time Elapsed (ticks)")
plt.ylabel("Wheat Collected")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
