import random
import math
from svgwrite import Drawing
from utils import line_segments_intersect

def generate_bottom_up_pattern(width, height, 
                              track_color="#FFFFFF", background_color="#000000", 
                              track_width_percent=60, 
                              segment1_min_percent=50, segment1_max_percent=70,
                              segment2_min_percent=1, segment2_max_percent=30,
                              segment3_min_percent=15, segment3_max_percent=30,
                              segment_complexity=0.7,
                              ball_diameter_percent=60, density_percent=70, 
                              spacing_variation_percent=50,
                              min_spacing_pixels=5,
                              show_grid=False, grid_color="#FF0000"):
    """
    Generate bottom-up pattern SVG with the specified parameters.
    Lines start from the bottom with 1-3 segments, turning at 45-degree angles.
    First segment is always vertical, second segment only turns 45 degrees.
    When 3 segments are present, the 3rd is parallel to the 1st.
    
    Returns the SVG drawing object and the SVG string
    """
    # For balancing left/right turns
    max_attempts = 5  # Maximum attempts to achieve balance
    for attempt in range(max_attempts):
        # If this isn't the first attempt, reset the seed to get a new pattern
        if attempt > 0:
            random.seed(random.randint(0, 1000000))
            
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
        
        # Calculate maximum total length (80% of vertical size)
        max_total_length = int(height * 0.8)
        
        # Calculate minimum required distance between elements to avoid visual overlapping
        min_element_distance = ball_diameter + 4  # Increased buffer for better collision avoidance
        
        # Calculate border areas (15% of width on each side)
        left_border = int(width * 0.15)
        right_border = width - int(width * 0.15)
        
        # Draw debug grid if requested
        if show_grid:
            grid_group = dwg.g(stroke=grid_color, stroke_width=1, stroke_opacity=0.5)
            # Draw vertical grid lines
            for x in range(grid_size, width, grid_size):
                grid_group.add(dwg.line(start=(x, 0), end=(x, height)))
            # Draw horizontal grid lines
            for y in range(grid_size, height, grid_size):
                grid_group.add(dwg.line(start=(0, y), end=(width, y)))
            # Draw border lines
            grid_group.add(dwg.line(start=(left_border, 0), end=(left_border, height), stroke="#00FF00", stroke_opacity=0.7))
            grid_group.add(dwg.line(start=(right_border, 0), end=(right_border, height), stroke="#00FF00", stroke_opacity=0.7))
            # Draw max total length reference line (80% of height)
            max_y = height - int(height * 0.8)
            grid_group.add(dwg.line(start=(0, max_y), end=(width, max_y), stroke="#0088FF", stroke_opacity=0.7))
            dwg.add(grid_group)
        
        # Possible directions in 45 degree increments
        directions = [
            (1, 0),    # 0 degrees - right
            (1, -1),   # 45 degrees - up-right
            (0, -1),   # 90 degrees - up
            (-1, -1),  # 135 degrees - up-left
            (-1, 0),   # 180 degrees - left
            (-1, 1),   # 225 degrees - down-left
            (0, 1),    # 270 degrees - down
            (1, 1)     # 315 degrees - down-right
        ]
        
        # Track segments and balls list to avoid overlaps
        track_segments = []
        balls = []
        
        # Counters for left and right turns
        left_turns = 0
        right_turns = 0
        
        # Calculate minimum spacing between lines (hardcoded minimum 5px + track width)
        min_spacing = min_spacing_pixels + track_width
        
        # Usable width after accounting for borders
        available_width = right_border - left_border
        
        # Calculate number of lines based on density (at 100% density we want maximum number of lines)
        # Maximum number of lines is determined by available width and minimum spacing
        max_possible_lines = int(available_width / min_spacing) + 1
        
        # Adjust target number of lines based on density percentage
        num_lines = max(2, int(max_possible_lines * (density_percent / 100)))
        
        # Calculate base spacing (the average spacing if lines were evenly distributed)
        base_spacing = available_width / (num_lines - 1) if num_lines > 1 else available_width
        
        # Calculate maximum variation based on variation percentage
        # At 0% variation, all lines are evenly spaced; at 100%, spacing can vary from min_spacing to 2*base_spacing
        max_variation = base_spacing * (spacing_variation_percent / 100)
        
        # Generate the x-coordinates for all lines
        x_positions = []
        
        # First line always at left border
        x_positions.append(left_border)
        
        # Generate positions for middle lines with variation
        current_x = left_border
        for i in range(1, num_lines - 1):
            # Standard position if evenly spaced
            even_x = left_border + i * base_spacing
            
            # Add variation (can be positive or negative)
            variation = random.uniform(-max_variation, max_variation)
            
            # Ensure we don't go below minimum spacing from previous line
            proposed_x = even_x + variation
            if proposed_x - current_x < min_spacing:
                proposed_x = current_x + min_spacing
            
            # Add position if it's within borders
            if proposed_x < right_border - min_spacing:
                x_positions.append(proposed_x)
                current_x = proposed_x
        
        # Last line always at right border
        x_positions.append(right_border)
        
        # Shuffle lines to randomize generation order (helps with overlap handling)
        random_indices = list(range(len(x_positions)))
        random.shuffle(random_indices)
        
        # Generate lines at calculated positions
        for i in random_indices:
            current_x = x_positions[i]
            
            # Determine number of segments based on segment_complexity (0-1 slider)
            # 0 = always 1 segment, 1 = up to 3 segments based on probability
            max_possible_segments = 3
            
            # Calculate segment probabilities based on complexity
            if segment_complexity <= 0:
                # Always just 1 segment
                num_segments = 1
            else:
                # Use probabilistic approach based on complexity
                segment_probs = [
                    1.0,  # Probability of at least 1 segment (always 100%)
                    segment_complexity,  # Probability of at least 2 segments
                    segment_complexity * 0.7  # Probability of 3 segments (70% of complexity)
                ]
                
                # Determine the maximum number of segments for this line
                threshold = random.random()
                num_segments = 1
                for idx in range(1, max_possible_segments):
                    if threshold <= segment_probs[idx]:
                        num_segments = idx + 1
            
            # Starting point at the bottom
            start_y = height - grid_size
            
            # Initialize path
            path_points = [(current_x, start_y)]
            pos_x, pos_y = current_x, start_y
            
            # List to hold all segments for this path
            path_segments = []
            
            # First segment - always vertical (up direction)
            first_dir_idx = 2  # Index for (0, -1) - upward direction
            dx, dy = directions[first_dir_idx]
            
            # Calculate segment lengths based on percentages of max_total_length
            # For the first segment, use the specified min/max percentages
            segment1_percent = random.randint(segment1_min_percent, segment1_max_percent)
            segment1_length = int(max_total_length * (segment1_percent / 100))
            
            # Ensure length is at least 10 pixels
            segment1_length = max(10, segment1_length)
            
            # Calculate end point of first segment
            next_x = pos_x + dx * segment1_length
            next_y = pos_y + dy * segment1_length
            
            # Ensure we stay within bounds
            if next_y < grid_size:
                next_y = grid_size
                segment1_length = pos_y - next_y  # Recalculate actual length after bounds check
            
            # Add first segment
            path_points.append((next_x, next_y))
            first_segment = (pos_x, pos_y, next_x, next_y)
            
            # Check if first segment would overlap with any existing element
            segment_collision = check_segment_collision(
                first_segment, 
                track_segments, 
                balls, 
                track_width, 
                min_element_distance
            )
            
            if segment_collision:
                # Skip this line if it would collide
                continue
            
            # First segment is valid, add it
            path_segments.append(first_segment)
            pos_x, pos_y = next_x, next_y
            
            # Track remaining length for the path (max_total_length - segment1_length)
            remaining_length = max_total_length - segment1_length
            
            # If we need more than one segment
            if num_segments > 1 and remaining_length > 10:  # Only add more segments if enough length remains
                # Check both possible 45-degree turns (-1 for left, 1 for right)
                turn_directions = [-1, 1]
                random.shuffle(turn_directions)  # Randomize which direction to try first
                
                second_segment_added = False
                
                # Try each direction until one works
                for turn_amount in turn_directions:
                    if second_segment_added:
                        break
                        
                    second_dir_idx = (first_dir_idx + turn_amount) % 8
                    dx, dy = directions[second_dir_idx]
                    
                    # Calculate second segment length based on percentage of max_total_length
                    segment2_percent = random.randint(segment2_min_percent, segment2_max_percent)
                    segment2_target_length = int(max_total_length * (segment2_percent / 100))
                    
                    # Ensure we don't exceed remaining length
                    segment2_length = min(segment2_target_length, remaining_length)
                    
                    # Ensure minimum length for second segment is at least 10 pixels
                    segment2_length = max(10, segment2_length)
                    
                    # Calculate end point of second segment
                    next_x = pos_x + dx * segment2_length
                    next_y = pos_y + dy * segment2_length
                    
                    # Ensure we don't go outside the canvas bounds
                    if next_x < 0:
                        next_x = 0
                    elif next_x > width:
                        next_x = width
                        
                    if next_y < grid_size:
                        next_y = grid_size
                    elif next_y > height - grid_size:
                        next_y = height - grid_size
                    
                    # Potential second segment
                    second_segment = (pos_x, pos_y, next_x, next_y)
                    
                    # Check if second segment would collide with any existing element
                    # We need to check against all segments except those in the current path
                    existing_segments = [seg for seg in track_segments if seg != first_segment]
                    segment_collision = check_segment_collision(
                        second_segment, 
                        existing_segments, 
                        balls, 
                        track_width, 
                        min_element_distance
                    )
                    
                    if not segment_collision:
                        # This direction works, add the segment
                        path_points.append((next_x, next_y))
                        path_segments.append(second_segment)
                        pos_x, pos_y = next_x, next_y
                        second_segment_added = True
                        
                        # Track turn direction for balance check
                        if turn_amount < 0:  # Left turn
                            left_turns += 1
                        else:  # Right turn
                            right_turns += 1
                        
                        # Recalculate actual segment length after bounds check
                        actual_segment2_length = math.sqrt((second_segment[2] - second_segment[0])**2 + 
                                                        (second_segment[3] - second_segment[1])**2)
                        remaining_length -= actual_segment2_length
            
                # If we added a second segment and need a third
                if second_segment_added and num_segments > 2 and remaining_length > 10:
                    # Third segment is parallel to first (same direction)
                    dx, dy = directions[first_dir_idx]
                    
                    # Calculate third segment length based on percentage of segment1 length
                    segment3_percent = random.randint(segment3_min_percent, segment3_max_percent)
                    segment3_target_length = int(segment1_length * (segment3_percent / 100))
                    
                    # Ensure we don't exceed remaining length
                    segment3_length = min(segment3_target_length, remaining_length)
                    
                    # Ensure minimum length for third segment is at least 10 pixels
                    segment3_length = max(10, segment3_length)
                    
                    # Try decreasing lengths until we find one that doesn't intersect
                    segment_attempts = 5
                    third_segment_added = False
                    
                    for seg_attempt in range(segment_attempts):
                        # Calculate percentage for this attempt (decrease by 20% each time)
                        percent_factor = 1.0 - (seg_attempt * 0.2)
                        current_length = int(segment3_length * percent_factor)
                        
                        # Ensure minimum length
                        current_length = max(10, current_length)
                        
                        # Calculate end point of third segment
                        next_x = pos_x + dx * current_length
                        next_y = pos_y + dy * current_length
                        
                        # Ensure we don't go outside the canvas bounds
                        if next_x < 0:
                            next_x = 0
                        elif next_x > width:
                            next_x = width
                            
                        if next_y < grid_size:
                            next_y = grid_size
                        elif next_y > height - grid_size:
                            next_y = height - grid_size
                        
                        # Potential third segment
                        third_segment = (pos_x, pos_y, next_x, next_y)
                        
                        # Check if third segment would collide with any existing element
                        # We need to check against all segments except those in the current path
                        existing_segments = [seg for seg in track_segments if seg != first_segment and seg != second_segment]
                        segment_collision = check_segment_collision(
                            third_segment, 
                            existing_segments, 
                            balls, 
                            track_width, 
                            min_element_distance
                        )
                        
                        if not segment_collision:
                            # This length works, add the segment
                            path_points.append((next_x, next_y))
                            path_segments.append(third_segment)
                            third_segment_added = True
                            break
                    
                    # If we couldn't add a third segment after multiple attempts, that's fine
                    # We'll just use what we have
            
            # Draw all valid segments
            for x1, y1, x2, y2 in path_segments:
                # Skip segments with identical start and end points
                if x1 == x2 and y1 == y2:
                    continue
                    
                pattern_group.add(dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=track_color,
                    stroke_width=track_width,
                    stroke_linecap="round"
                ))
            
            # Check if adding a ball at the end would cause an overlap
            if path_segments:
                end_x, end_y = path_points[-1]
                
                # Check for ball-to-ball overlaps with a minimum distance
                ball_placement_valid = True
                for ball_x, ball_y, r in balls:
                    # Measure center-to-center distance
                    dist = math.sqrt((end_x - ball_x)**2 + (end_y - ball_y)**2)
                    if dist < (ball_radius + r + 6):  # Increased buffer between balls
                        ball_placement_valid = False
                        break
                
                if ball_placement_valid:
                    # Add ball at the end of the path
                    pattern_group.add(dwg.circle(
                        center=(end_x, end_y), 
                        r=ball_radius,
                        fill=track_color
                    ))
                    
                    # Add ball to list of balls (for collision detection)
                    balls.append((end_x, end_y, ball_radius))
            
            # Add segments to the tracking list to prevent overlaps
            track_segments.extend(path_segments)
        
        # Add the pattern group to the drawing
        dwg.add(pattern_group)
        
        # Check for left/right turn balance (not more than 5% difference)
        total_turns = left_turns + right_turns
        if total_turns > 0:
            left_percent = (left_turns / total_turns) * 100
            right_percent = (right_turns / total_turns) * 100
            
            # If the difference is less than 5%, we have a balanced pattern
            if abs(left_percent - right_percent) <= 5:
                # Return the balanced pattern
                svg_string = dwg.tostring()
                return dwg, svg_string
        elif segment_complexity <= 0:
            # If complexity is 0, we expect no turns, so that's fine
            svg_string = dwg.tostring()
            return dwg, svg_string
    
    # If we reach here, we couldn't achieve balance after max_attempts
    # Return the last pattern we generated
    svg_string = dwg.tostring()
    return dwg, svg_string

def check_segment_collision(segment, existing_segments, balls, track_width, min_distance):
    """
    Comprehensive check for collisions between a segment and:
    1. All existing segments
    2. All existing balls
    
    Returns True if a collision is detected, False otherwise
    """
    # Check for collisions with existing segments
    for other_segment in existing_segments:
        if line_segments_intersect(segment, other_segment):
            return True
    
    # Check for collisions with existing balls
    segment_x1, segment_y1, segment_x2, segment_y2 = segment
    for ball_x, ball_y, ball_radius in balls:
        # Distance from ball center to line segment
        dist = point_to_line_segment_distance(
            ball_x, ball_y, 
            segment_x1, segment_y1, 
            segment_x2, segment_y2
        )
        
        # Check if ball is too close to the segment
        # We need track_width/2 + ball_radius + buffer
        required_clearance = track_width/2 + ball_radius + 4
        if dist < required_clearance:
            return True
    
    # No collisions detected
    return False

def point_to_line_segment_distance(px, py, x1, y1, x2, y2):
    """Calculate the shortest distance from a point to a line segment"""
    # Calculate line length squared
    line_length_sq = (x2 - x1)**2 + (y2 - y1)**2
    
    # If line is a point, return distance to the point
    if line_length_sq == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2)
    
    # Calculate projection of point onto line
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length_sq))
    
    # Calculate closest point on line
    closest_x = x1 + t * (x2 - x1)
    closest_y = y1 + t * (y2 - y1)
    
    # Return distance to closest point
    return math.sqrt((px - closest_x)**2 + (py - closest_y)**2) 