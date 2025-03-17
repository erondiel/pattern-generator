# Circuit Pattern Generator

A Streamlit web application that generates SVG circuit-like patterns for use as masks in Substance Painter or other texture creation tools.

## Features

- Generate random circuit-like patterns with configurable parameters
- Adjust grid size, ball diameter, track width, and more
- Control pattern density and complexity
- View debug grid to understand pattern structure
- Download patterns as SVG files
- Reproducible patterns with seed control

## How It Works

The generator creates a grid of points and builds tracks between them, placing balls at the track endpoints. The result resembles electronic circuit patterns that can be used for sci-fi textures, tech panels, or other similar applications.

## Usage

1. Adjust the grid columns and rows to set the overall pattern dimensions
2. Set the ball diameter and track width percentages to control the appearance
3. Use the density slider to control how full the pattern is
4. Toggle the debug grid to see the underlying structure
5. Click "Generate New Pattern" for a different random pattern
6. Download the SVG when you're satisfied with the result

## Settings Explained

- **Grid Dimensions**: Controls how many grid cells are used for pattern generation
- **Ball Diameter**: The size of the balls that appear at line endpoints (as a percentage of maximum possible size)
- **Track Width**: The thickness of the tracks connecting points (as a percentage of ball diameter)
- **Min/Max Track Length**: Controls the range of possible track segment lengths
- **Density**: Percentage of grid points to fill with pattern elements
- **Overlap Probability**: Controls whether tracks can cross (0 = no crossings, 1 = always allow)

## Deployment

This app is deployed on Streamlit Cloud. You can also run it locally with:

```
pip install -r requirements.txt
streamlit run circuit_pattern_generator.py
```

## Converting to PNG

To use the generated patterns in Substance Painter:
1. Download the SVG file
2. Convert to PNG using an online converter or graphics software
3. Import the PNG as a mask in Substance Painter 