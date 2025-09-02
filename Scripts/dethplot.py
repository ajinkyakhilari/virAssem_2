import matplotlib.pyplot as plt
import argparse
import numpy as np  # Import numpy for logarithmic scaling

# Set up argument parser
parser = argparse.ArgumentParser(description='Plot depth of coverage from a depth file on a logarithmic scale.')
parser.add_argument('input_file', help='Input depth file')
parser.add_argument('output_file', help='Output file for the plot (e.g., plot.pdf)')
args = parser.parse_args()

# Reading the depth file
positions = []
depths = []
low_depth_positions = []
low_depths = []

with open(args.input_file, "r") as file:
    for line in file:
        parts = line.split()
        pos = int(parts[1])
        depth = int(parts[2]) + 1  # Add 1 to avoid log(0)
        positions.append(pos)
        depths.append(depth)

        # Check if depth is less than 20x
        if depth < 21:  # Adjusted for the added 1
            low_depth_positions.append(pos)
            low_depths.append(depth)

# Convert depths to log scale
log_depths = np.log(depths)
log_low_depths = np.log(low_depths)

# Plotting
plt.figure(figsize=(10, 4))
plt.fill_between(positions, log_depths, color='grey', label='Depth ≥ 20x', step='mid')  # Area plot for depth ≥ 20x
plt.scatter(low_depth_positions, log_low_depths, color='red', label='Depth < 20x', s=1)  # Mark low depth points in red
plt.title("Depth of Coverage (Log Scale)", fontweight='bold')
plt.xlabel("Position", fontweight='bold')
plt.ylabel("Log Depth", fontweight='bold')

# Position the legend below the x-axis
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=2)

plt.savefig(args.output_file, format='pdf')
plt.close()

