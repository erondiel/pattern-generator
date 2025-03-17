# Pattern Generator

A Streamlit web application that generates SVG patterns for use as masks, textures, or design elements. The generator supports two pattern types:

1. **Circuit Pattern**: Electronic circuit-like patterns with tracks and balls
2. **Bottom-Up Pattern**: Vertical lines with 45-degree turns and balls at endpoints

## Features

- Generate two different types of patterns with customizable parameters
- Adjust dimensions, colors, spacing, and complexity
- Control pattern density and segment properties
- View debug grid to understand pattern structure
- Download patterns as SVG files with seed information for reproducibility
- Responsive interface with intuitive controls

## Pattern Types

### Circuit Pattern
Creates a grid-based pattern that resembles electronic circuits with tracks connecting points and balls at track endpoints. Perfect for sci-fi textures, tech panels, or circuit board designs.

### Bottom-Up Pattern
Generates vertical lines starting from the bottom with optional 45-degree turns. Each line consists of 1-3 segments with balls at endpoints. Great for creating abstract, modern patterns with balanced angles.

## Usage

1. Select the desired pattern type from the radio buttons
2. Adjust the grid dimensions and pattern-specific parameters
3. Choose colors for tracks and background
4. Use the sliders to control density, ball size, and track width
5. Click "Generate New Pattern" for a different random pattern
6. Download the SVG when satisfied with the result

## Settings Explained

### Common Settings
- **Grid Dimensions**: Sets the overall pattern size based on grid cells
- **Colors**: Track and background color selection
- **Ball Diameter**: Size of balls at line endpoints
- **Track Width**: Thickness of the lines/tracks
- **Density**: Controls how many elements are included in the pattern
- **Debug Grid**: Toggles visualization of underlying grid and borders

### Circuit Pattern Settings
- **Min/Max Track Length**: Controls the range of possible track segment lengths

### Bottom-Up Pattern Settings
- **Segment 1/2/3 Min/Max %**: Controls the length ranges for each segment
- **Segment Complexity**: Controls how many segments are used (0=only first segment, 1=maximum segments)
- **Spacing Variation**: Controls how evenly spaced the vertical lines are
- **Minimum Line Spacing**: Sets the minimum distance between adjacent lines

## Deployment

This app can be run locally with:

```
pip install -r requirements.txt
streamlit run app.py
```

## Converting to Other Formats

To use the generated patterns in other applications:
1. Download the SVG file
2. Convert to other formats (PNG, JPG) using an online converter or graphics software
3. Import as needed into your design or 3D application 