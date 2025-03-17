import streamlit as st
import random
import base64
import math
from svgwrite import Drawing

def line_segments_intersect(line1, line2):
    """Check if two line segments intersect"""
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    
    # Calculate determinants
    den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    
    # If den is zero, lines are parallel
    if den == 0:
        return False
        
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
    
    # If ua and ub are between 0 and 1, segments intersect
    return 0 <= ua <= 1 and 0 <= ub <= 1

def generate_mask_pattern(width=800, height=600, 
                         track_color="#FFFFFF", background_color="#000000", 
                         track_width_percent=10, min_track_length=2, max_track_length=8,
                         ball_diameter_percent=15, density_percent=70, overlap_probability=0.0,
                         show_grid=False, grid_color="#FF0000"):
    """
    Generate circuit pattern SVG with the specified parameters
    
    Returns the SVG drawing object and the SVG string
    """
    # Create SVG drawing
    dwg = Drawing(size=(width, height), profile='tiny')
    
    # Add background
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=background_color))
    
    # Create a group for the pattern
    pattern_group = dwg.g()
    
    # Calculate grid size and actual sizes in pixels
    grid_size = 40  # Fixed grid size
    # Make sure the max ball diameter is 95% of grid_size
    max_ball_diameter = int(grid_size * 0.95)
    ball_diameter = int(max_ball_diameter * (ball_diameter_percent / 100))
    track_width = int(ball_diameter * (track_width_percent / 100))
    
    # Calculate ball radius for drawing (half of diameter)
    ball_radius = ball_diameter / 2
    
    # Enforce minimum sizes
    ball_radius = max(1, ball_radius)
    track_width = max(1, track_width)
    
    # Draw debug grid if requested
    if show_grid:
        grid_group = dwg.g(stroke=grid_color, stroke_width=1, stroke_opacity=0.5)
        # Draw vertical grid lines
        for x in range(grid_size, width, grid_size):
            grid_group.add(dwg.line(start=(x, 0), end=(x, height)))
        # Draw horizontal grid lines
        for y in range(grid_size, height, grid_size):
            grid_group.add(dwg.line(start=(0, y), end=(width, y)))
        dwg.add(grid_group)
    
    # Create a grid of potential points
    grid_points = []
    for x in range(grid_size, width - grid_size + 1, grid_size):
        for y in range(grid_size, height - grid_size + 1, grid_size):
            grid_points.append((x, y))
    
    # Shuffle the grid points to ensure random distribution
    random.shuffle(grid_points)
    
    # Calculate target number of points to use based on density percentage
    target_filled = int(len(grid_points) * (density_percent / 100))
    
    # Track all occupied grid points and line endpoints
    occupied_points = set()
    endpoint_positions = []  # Changed to list to avoid duplicate endpoints too close together
    
    # Track line segments to check for crossings
    track_segments = []
    
    # Track failed points to re-attempt with different directions
    failed_points = set()
    
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
    
    # Process all grid points, attempting to fill up to the target density
    remaining_points = list(grid_points)
    
    # Add failsafe to prevent infinite loops
    max_attempts = len(grid_points) * 2
    attempts = 0
    
    # Continue until we've reached our target density or tried all possible points
    while remaining_points and len(occupied_points) < target_filled and attempts < max_attempts:
        attempts += 1
        
        # Choose a point that's not already occupied
        available_points = [pt for pt in remaining_points if pt not in occupied_points]
        if not available_points:
            # If no more unoccupied points, try previously failed points again
            if not failed_points:
                break
            available_points = list(failed_points)
            failed_points.clear()
            
        # Get a random starting point
        start_point = random.choice(available_points)
        start_x, start_y = start_point
        
        # Fix for "list.remove(x): x not in list" error
        if start_point in remaining_points:
            remaining_points.remove(start_point)
        
        # Create track
        current_x, current_y = start_x, start_y
        
        # Calculate appropriate minimum distance between ball centers based on ball diameter
        # For smaller balls, we need more space (relative to ball size) to ensure visual separation
        # For larger balls, we need less relative space to avoid getting stuck
        if ball_diameter < grid_size * 0.25:  # Small balls
            distance_factor = 1.1
        elif ball_diameter < grid_size * 0.5:  # Medium balls
            distance_factor = 1.0
        else:  # Large balls
            distance_factor = 0.95
            
        min_distance_between_balls = ball_diameter * distance_factor
        
        # Check if this point is too close to an existing endpoint for a ball
        too_close_to_endpoint = False
        
        for ex, ey in endpoint_positions:
            distance = math.sqrt((start_x - ex)**2 + (start_y - ey)**2)
            if distance < min_distance_between_balls:
                too_close_to_endpoint = True
                break
                
        if too_close_to_endpoint:
            # Skip this point and mark it as failed
            failed_points.add(start_point)
            continue
        
        # Try all possible directions for this starting point
        random_directions = list(directions)
        random.shuffle(random_directions)
        
        track_created = False
        
        for dx, dy in random_directions:
            if track_created:
                break
                
            # Reset to starting point for each direction attempt
            current_x, current_y = start_x, start_y
            
            # Mark starting point as occupied
            occupied_points.add((current_x, current_y))
            
            # Track length based on min/max parameters
            track_length = random.randint(min_track_length, max_track_length)
            
            # Initialize path
            path_points = [(current_x, current_y)]
            this_track_segments = []
            
            # Generate path segments
            segment_created = False
            
            for _ in range(track_length):
                # Move in current direction
                next_x = current_x + dx * grid_size
                next_y = current_y + dy * grid_size
                
                # Stop if we hit the edge
                if (next_x < grid_size or next_x > width - grid_size or
                    next_y < grid_size or next_y > height - grid_size):
                    break
                    
                # Skip if next point is already occupied (besides the starting point)
                if (next_x, next_y) in occupied_points and (next_x, next_y) != (start_x, start_y):
                    if overlap_probability == 0.0 or random.random() > overlap_probability:
                        break
                
                # For zero overlap probability, check for line segment intersections
                if overlap_probability == 0.0:
                    new_segment = (current_x, current_y, next_x, next_y)
                    segment_intersection = False
                    
                    for segment in track_segments:
                        if line_segments_intersect(new_segment, segment):
                            segment_intersection = True
                            break
                            
                    if segment_intersection:
                        break
                
                # Check if endpoint would be too close to existing balls
                too_close = False
                for ex, ey in endpoint_positions:
                    distance = math.sqrt((next_x - ex)**2 + (next_y - ey)**2)
                    if distance < min_distance_between_balls:
                        too_close = True
                        break
                
                if too_close:
                    break
                            
                # Add point to path
                this_segment = (current_x, current_y, next_x, next_y)
                this_track_segments.append(this_segment)
                
                current_x, current_y = next_x, next_y
                path_points.append((current_x, current_y))
                occupied_points.add((current_x, current_y))
                
                # We've created at least one segment
                segment_created = True
                
                # Possibly change direction (with 45-degree constraint)
                if random.random() < 0.4:
                    # Change direction by +/- 45 or 90 degrees
                    turn_amount = random.choice([-2, -1, 1, 2])
                    dir_idx = directions.index((dx, dy))
                    dir_idx = (dir_idx + turn_amount) % 8
                    dx, dy = directions[dir_idx]
            
            # Draw the path if it has at least 2 points (meaning we created at least 1 segment)
            if len(path_points) >= 2 and segment_created:
                # Add this track's segments to all segments
                track_segments.extend(this_track_segments)
                
                # Draw track lines
                for i in range(len(path_points) - 1):
                    x1, y1 = path_points[i]
                    x2, y2 = path_points[i + 1]
                    pattern_group.add(dwg.line(
                        start=(x1, y1),
                        end=(x2, y2),
                        stroke=track_color,
                        stroke_width=track_width,
                        stroke_linecap="round"
                    ))
                
                # Add both endpoints to the list of positions where balls should be placed
                # Note: We need to check for duplicates or near-duplicates
                for point in [path_points[0], path_points[-1]]:
                    px, py = point
                    # Only add if not too close to existing endpoints
                    should_add = True
                    for ex, ey in endpoint_positions:
                        distance = math.sqrt((px - ex)**2 + (py - ey)**2)
                        if distance < min_distance_between_balls:
                            should_add = False
                            break
                    
                    if should_add:
                        endpoint_positions.append((px, py))
                
                # Mark that we've created a track from this starting point
                track_created = True
            else:
                # If we couldn't create a track in this direction, remove the starting point
                # from occupied points to allow it to be used for another attempt
                occupied_points.remove((start_x, start_y))
        
        # If we couldn't create a track from this point in any direction, add it to failed points
        if not track_created:
            failed_points.add(start_point)
    
    # Now place balls at all line endpoints
    for x, y in endpoint_positions:
        pattern_group.add(dwg.circle(
            center=(x, y), 
            r=ball_radius,  # Use the radius for SVG circles
            fill=track_color
        ))
    
    # Add the pattern group to the drawing
    dwg.add(pattern_group)
    
    # Return the drawing object and SVG string
    svg_string = dwg.tostring()
    return dwg, svg_string

def get_svg_download_link(svg_string, filename, text):
    """Generate a link to download SVG"""
    b64 = base64.b64encode(svg_string.encode()).decode()
    href = f'<a href="data:image/svg+xml;base64,{b64}" download="{filename}.svg">{text}</a>'
    return href

def main():
    st.title("Circuit Pattern Generator")
    
    # Add custom CSS for color pickers
    st.markdown("""
    <style>
    .stColorPicker {
        width: 100% !important;
    }
    .stColorPicker > label {
        min-height: 40px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.header("Pattern Parameters")
    
    # Fixed grid size
    grid_size = 40  # pixels
    
    # Grid-based dimension controls
    st.sidebar.subheader("Grid Dimensions")
    grid_cols = st.sidebar.number_input("Grid Columns", min_value=3, max_value=100, value=20)
    grid_rows = st.sidebar.number_input("Grid Rows", min_value=3, max_value=100, value=15)
    
    # Calculate actual pixel dimensions
    width = (grid_cols + 1) * grid_size
    height = (grid_rows + 1) * grid_size
    
    # Show actual pixel dimensions
    st.sidebar.text(f"Canvas: {width}px × {height}px")
    st.sidebar.text(f"Grid: {grid_cols}×{grid_rows} = {grid_cols * grid_rows} cells")
    
    # Color controls side by side with fixed layout
    st.sidebar.subheader("Colors")
    
    # Use equal width columns
    col1, col2 = st.sidebar.columns([1, 1])
    
    # Place color pickers in columns with fixed heights
    with col1:
        track_color = st.color_picker("Track Color", "#FFFFFF")
    with col2:
        background_color = st.color_picker("Background Color", "#000000")
    
    # Ball size control
    st.sidebar.subheader("Ball Properties")
    ball_diameter_percent = st.sidebar.slider("Ball Diameter (%)", min_value=5, max_value=100, value=60,
                                     help="Percentage of maximum ball diameter (95% of grid)")
    
    # Calculate actual ball diameter for display
    max_ball_diameter = int(grid_size * 0.95)
    actual_ball_diameter = int(max_ball_diameter * (ball_diameter_percent / 100))
    st.sidebar.text(f"Ball diameter: {actual_ball_diameter}px (max: {max_ball_diameter}px)")
    
    # Track controls
    st.sidebar.subheader("Track Properties")
    track_width_percent = st.sidebar.slider("Track Width (%)", min_value=5, max_value=90, value=60,
                                         help="Percentage of ball diameter")
    
    # Calculate actual track width for display
    actual_track_width = int(actual_ball_diameter * (track_width_percent / 100))
    st.sidebar.text(f"Track width: {actual_track_width}px")
    
    col1, col2 = st.sidebar.columns(2)
    min_track_length = col1.number_input("Min Track Length", min_value=1, max_value=10, value=2)
    max_track_length = col2.number_input("Max Track Length", min_value=2, max_value=20, value=8)
    
    # Ensure min_track_length <= max_track_length
    if min_track_length > max_track_length:
        max_track_length = min_track_length
        st.sidebar.warning("Min track length cannot be greater than max track length")
    
    # Density and pattern controls
    st.sidebar.subheader("Pattern Properties")
    density_percent = st.sidebar.slider("Density (%)", min_value=1, max_value=100, value=70, 
                                      help="Percentage of grid slots to fill with tracks")
    
    overlap_probability = st.sidebar.slider("Overlap Probability", min_value=0.0, max_value=1.0, value=0.0, step=0.05, 
                                          help="0 = No overlaps, 1 = Always allow overlaps")
    
    # Generate button
    if st.sidebar.button("Generate New Pattern"):
        st.session_state.seed = random.randint(0, 1000000)
    
    # Set random seed for reproducible patterns
    if 'seed' not in st.session_state:
        st.session_state.seed = random.randint(0, 1000000)
    
    random.seed(st.session_state.seed)
    
    # Debug grid option moved to bottom of UI
    st.sidebar.subheader("Debug Options")
    show_grid = st.sidebar.checkbox("Show Debug Grid", value=False)
    grid_color = "#FF0000"  # Red grid
    
    # Generate the pattern
    try:
        dwg, svg_string = generate_mask_pattern(
            width=width, 
            height=height,
            track_color=track_color,
            background_color=background_color,
            track_width_percent=track_width_percent,
            min_track_length=min_track_length,
            max_track_length=max_track_length,
            ball_diameter_percent=ball_diameter_percent,
            density_percent=density_percent,
            overlap_probability=overlap_probability,
            show_grid=show_grid,
            grid_color=grid_color
        )
        
        # Display current seed
        st.sidebar.text(f"Current Seed: {st.session_state.seed}")
        
        # Show info about the grid and target filled
        st.sidebar.text(f"Target filled: {int(grid_cols * grid_rows * density_percent/100)} cells")
        
        # Calculate preview size based on available width
        # Get available width from streamlit container (approximate)
        available_width = 700  # Approximate default content width in pixels
        
        # Calculate a height that maintains the aspect ratio
        aspect_ratio = height / width
        display_width = min(available_width, width)
        display_height = int(display_width * aspect_ratio)
        
        # Ensure height is reasonable (not too tall or too short)
        display_height = min(800, max(300, display_height))
        
        # Create container with properly sized SVG
        st.markdown(f"""
        <div style="background-color: {background_color}; padding: 10px; border-radius: 5px; 
                    width: {display_width}px; height: {display_height}px; margin: 0 auto; 
                    overflow: auto; text-align: center;">
            <svg width="{display_width}" height="{display_height}" viewBox="0 0 {width} {height}" 
                 preserveAspectRatio="xMidYMid meet">
                {svg_string[svg_string.find('>')+1:]}
            </svg>
        </div>
        """, unsafe_allow_html=True)
        
        # Download SVG
        st.markdown(get_svg_download_link(svg_string, "circuit_pattern", "Download SVG"), unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error generating pattern: {e}")

if __name__ == "__main__":
    main() 