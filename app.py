import streamlit as st
import random
from pattern_types import PatternType
from circuit_pattern import generate_circuit_pattern
from bottom_up_pattern import generate_bottom_up_pattern
from utils import get_svg_download_link

def generate_mask_pattern(pattern_type=PatternType.CIRCUIT, **kwargs):
    """
    Generate a pattern based on the selected pattern type
    """
    if pattern_type == PatternType.CIRCUIT:
        return generate_circuit_pattern(**kwargs)
    elif pattern_type == PatternType.BOTTOM_UP:
        return generate_bottom_up_pattern(**kwargs)
    else:
        raise ValueError(f"Unknown pattern type: {pattern_type}")

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
    
    # Pattern type selection
    pattern_type = st.sidebar.radio(
        "Pattern Type",
        [PatternType.CIRCUIT.value, PatternType.BOTTOM_UP.value]
    )
    pattern_type = PatternType.CIRCUIT if pattern_type == PatternType.CIRCUIT.value else PatternType.BOTTOM_UP
    
    # Fixed grid size
    grid_size = 40  # pixels
    
    # Grid-based dimension controls
    st.sidebar.subheader("Grid Dimensions")
    grid_cols = st.sidebar.number_input("Grid Columns", min_value=3, max_value=100, value=20)
    # Calculate grid rows based on 4:3 vertical aspect ratio (height:width = 4:3)
    grid_rows = int((4/3) * grid_cols)
    
    # Calculate actual pixel dimensions
    width = (grid_cols + 1) * grid_size
    height = (grid_rows + 1) * grid_size
    
    # Show actual pixel dimensions
    st.sidebar.text(f"Canvas: {width}px × {height}px (4:3 vertical ratio)")
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
    
    # Pattern-specific controls
    if pattern_type == PatternType.CIRCUIT:
        # Circuit Pattern specific controls
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
        
    else: # Bottom-up pattern
        # Bottom-up Pattern specific controls
        st.sidebar.subheader("Segment Properties")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            segment1_min_percent = st.number_input("Segment 1 Min %", min_value=15, max_value=80, value=20,
                                                help="Min percentage of max total length (80% of vertical size)")
        with col2:
            segment1_max_percent = st.number_input("Segment 1 Max %", min_value=40, max_value=90, value=70,
                                                help="Max percentage of max total length")
        
        if segment1_min_percent > segment1_max_percent:
            segment1_max_percent = segment1_min_percent
            st.sidebar.warning("Min segment 1 % cannot be greater than max segment 1 %")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            segment2_min_percent = st.number_input("Segment 2 Min %", min_value=1, max_value=30, value=1,
                                                help="Min percentage of max total length")
        with col2:
            segment2_max_percent = st.number_input("Segment 2 Max %", min_value=1, max_value=50, value=30,
                                                help="Max percentage of max total length")
        
        if segment2_min_percent > segment2_max_percent:
            segment2_max_percent = segment2_min_percent
            st.sidebar.warning("Min segment 2 % cannot be greater than max segment 2 %")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            segment3_min_percent = st.number_input("Segment 3 Min %", min_value=5, max_value=40, value=15,
                                                help="Min percentage of first segment length")
        with col2:
            segment3_max_percent = st.number_input("Segment 3 Max %", min_value=10, max_value=100, value=30,
                                                help="Max percentage of first segment length")
        
        if segment3_min_percent > segment3_max_percent:
            segment3_max_percent = segment3_min_percent
            st.sidebar.warning("Min segment 3 % cannot be greater than max segment 3 %")
        
        # Segment complexity slider replaces the number of segments controls
        segment_complexity = st.sidebar.slider("Segment Complexity", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                                            help="0 = only first segment, 1 = maximum number of segments")
        
        # Density control
        st.sidebar.subheader("Pattern Properties")
        density_percent = st.sidebar.slider("Density (%)", min_value=1, max_value=100, value=70, 
                                          help="Percentage of available space to fill with lines")
        
        # Line spacing controls
        spacing_variation_percent = st.sidebar.slider("Spacing Variation (%)", min_value=0, max_value=100, value=50,
                                                   help="How much line spacing can vary (0% = even spacing, 100% = maximum variation)")
        
        min_spacing_pixels = st.sidebar.number_input("Minimum Line Spacing (px)", min_value=2, max_value=20, value=5,
                                                  help="Minimum empty space between adjacent lines in pixels")
    
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
        if pattern_type == PatternType.CIRCUIT:
            # Generate the circuit pattern
            dwg, svg_string = generate_mask_pattern(
                pattern_type=PatternType.CIRCUIT,
                width=width, 
                height=height,
                track_color=track_color,
                background_color=background_color,
                track_width_percent=track_width_percent,
                min_track_length=min_track_length,
                max_track_length=max_track_length,
                ball_diameter_percent=ball_diameter_percent,
                density_percent=density_percent,
                show_grid=show_grid,
                grid_color=grid_color
            )
        else:
            # Generate the bottom-up pattern
            dwg, svg_string = generate_mask_pattern(
                pattern_type=PatternType.BOTTOM_UP,
                width=width, 
                height=height,
                track_color=track_color,
                background_color=background_color,
                track_width_percent=track_width_percent,
                segment1_min_percent=segment1_min_percent,
                segment1_max_percent=segment1_max_percent,
                segment2_min_percent=segment2_min_percent,
                segment2_max_percent=segment2_max_percent,
                segment3_min_percent=segment3_min_percent,
                segment3_max_percent=segment3_max_percent,
                segment_complexity=segment_complexity,
                ball_diameter_percent=ball_diameter_percent,
                density_percent=density_percent,
                spacing_variation_percent=spacing_variation_percent,
                min_spacing_pixels=min_spacing_pixels,
                show_grid=show_grid,
                grid_color=grid_color
            )
        
        # Display current seed
        st.sidebar.text(f"Current Seed: {st.session_state.seed}")
        
        # Show info about the grid
        if pattern_type == PatternType.CIRCUIT:
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
        pattern_type_text = "circuit" if pattern_type == PatternType.CIRCUIT else "bottom_up"
        download_filename = f"{pattern_type_text}_pattern_seed_{st.session_state.seed}"
        st.markdown(get_svg_download_link(svg_string, download_filename, f"Download {pattern_type.value} SVG"), unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error generating pattern: {e}")

if __name__ == "__main__":
    main() 