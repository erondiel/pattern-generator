import base64

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

def get_svg_download_link(svg_string, filename, text):
    """Generate a link to download SVG"""
    b64 = base64.b64encode(svg_string.encode()).decode()
    href = f'<a href="data:image/svg+xml;base64,{b64}" download="{filename}.svg">{text}</a>'
    return href 