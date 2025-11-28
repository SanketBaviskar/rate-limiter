"""
utils.py - Utility Functions

This module contains helper functions used across the application.

Functions:
- generate_placeholder_svg: Creates an SVG image with custom dimensions and color
"""

def generate_placeholder_svg(width: int, height: int, color: str = "#3b82f6") -> str:
    """
    Generates a simple SVG placeholder image.
    """
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="{color}"/>
    <text x="50%" y="50%" font-family="Arial" font-size="24" fill="white" dominant-baseline="middle" text-anchor="middle">
        {width}x{height}
    </text>
</svg>'''
    return svg
