import random
import math
import argparse
from svgwrite import Drawing

def generate_mask_pattern(filename, width=800, height=600, 
                         track_width=4, min_track_length=2, max_track_length=8,
                         density=0.7, allow_overlaps=False,
                         rotation=0):
    """
    Generate circuit pattern SVG optimized for Substance Painter masking
    
    Args:
        filename: Output SVG filename
        width, height: Dimensions of the SVG
        track_width: Width of circuit tracks
        min_track_length: Minimum number of segments in a track
        max_track_length: Maximum number of segments in a track
        density: How many tracks to generate (0-1)
        allow_overlaps: Whether tracks can overlap each other
        rotation: Rotate the entire pattern by degrees
    """
    # Create SVG drawing
    dwg = Drawing(filename, size=(width, height), profile='tiny')
    
    # Add black background
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill="#000000"))
    
    # Create a group for the entire pattern that we'll rotate
    pattern_group = dwg.g()
    
    # Calculate grid size and number of possible start points
    grid_size = 40  # Fixed grid size for simplicity
    num_tracks = int((width * height) / (grid_size * grid_size) * density)
    
    # Possible directions in 45 degree increments
    directions = [
        (1, 0),    # 0 degrees
        (1, 1),    # 45 degrees
        (0, 1),    # 90 degrees
        (-1, 1),   # 135 degrees
        (-1, 0),   # 180 degrees
        (-1, -1),  # 225 degrees
        (0, -1),   # 270 degrees
        (1, -1)    # 315 degrees
    ]
    
    # Track all occupied points to avoid overlaps (if not allowed)
    occupied_points = set() if not allow_overlaps else None
    
    # Generate circuit tracks
    for _ in range(num_tracks):
        # Random starting point
        start_x = int(random.uniform(grid_size, width - grid_size) / grid_size) * grid_size
        start_y = int(random.uniform(grid_size, height - grid_size) / grid_size) * grid_size
        
        # Skip if starting point is already occupied and overlaps not allowed
        if not allow_overlaps and (start_x, start_y) in occupied_points:
            continue
            
        # Create track
        current_x, current_y = start_x, start_y
        if not allow_overlaps:
            occupied_points.add((current_x, current_y))
        
        # Random initial direction
        dir_idx = random.randint(0, 7)
        dx, dy = directions[dir_idx]
        
        # Track length based on min/max parameters
        track_length = random.randint(min_track_length, max_track_length)
        
        # Initialize path
        path_points = [(current_x, current_y)]
        
        # Generate path segments
        for _ in range(track_length):
            # Move in current direction
            next_x = current_x + dx * grid_size
            next_y = current_y + dy * grid_size
            
            # Stop if we hit the edge or an occupied point (if overlaps not allowed)
            if (next_x < grid_size or next_x > width - grid_size or
                next_y < grid_size or next_y > height - grid_size or
                (not allow_overlaps and (next_x, next_y) in occupied_points)):
                break
                
            # Add point to path
            current_x, current_y = next_x, next_y
            path_points.append((current_x, current_y))
            if not allow_overlaps:
                occupied_points.add((current_x, current_y))
            
            # Possibly change direction (with 45-degree constraint)
            if random.random() < 0.4:
                # Change direction by +/- 45 or 90 degrees
                turn_amount = random.choice([-2, -1, 1, 2])
                dir_idx = (dir_idx + turn_amount) % 8
                dx, dy = directions[dir_idx]
        
        # Draw the path if it has at least 2 points
        if len(path_points) >= 2:
            # Draw track lines
            for i in range(len(path_points) - 1):
                x1, y1 = path_points[i]
                x2, y2 = path_points[i + 1]
                pattern_group.add(dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke="#ffffff",
                    stroke_width=track_width,
                    stroke_linecap="round"
                ))
            
            # Draw endpoint pads/balls
            pattern_group.add(dwg.circle(
                center=path_points[0], 
                r=track_width * 1.5,
                fill="#ffffff"
            ))
            
            pattern_group.add(dwg.circle(
                center=path_points[-1], 
                r=track_width * 1.5,
                fill="#ffffff"
            ))
    
    # Apply rotation to the entire pattern group if specified
    if rotation != 0:
        pattern_group.rotate(rotation, center=(width/2, height/2))
    
    # Add the pattern group to the drawing
    dwg.add(pattern_group)
    
    # Save the SVG file
    dwg.save()
    print(f"Mask pattern generated and saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Generate Substance Painter mask pattern SVG')
    parser.add_argument('-o', '--output', default='substance_mask.svg', help='Output SVG file')
    parser.add_argument('-W', '--width', type=int, default=800, help='Width of SVG')
    parser.add_argument('-H', '--height', type=int, default=600, help='Height of SVG')
    parser.add_argument('--track-width', type=int, default=4, help='Width of circuit tracks')
    parser.add_argument('--min-track-length', type=int, default=2, help='Minimum track length segments')
    parser.add_argument('--max-track-length', type=int, default=8, help='Maximum track length segments')
    parser.add_argument('--density', type=float, default=0.7, help='Track density from 0-1')
    parser.add_argument('--allow-overlaps', action='store_true', help='Allow tracks to overlap')
    parser.add_argument('--rotation', type=float, default=0, help='Pattern rotation in degrees')
    
    args = parser.parse_args()
    
    generate_mask_pattern(
        args.output,
        width=args.width,
        height=args.height,
        track_width=args.track_width,
        min_track_length=args.min_track_length,
        max_track_length=args.max_track_length,
        density=args.density,
        allow_overlaps=args.allow_overlaps,
        rotation=args.rotation
    )

if __name__ == "__main__":
    main() 