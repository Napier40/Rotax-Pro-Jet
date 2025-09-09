"""
Create placeholder images for Rotax Pro Jet.

This script generates placeholder images for development purposes.
It requires Pillow to be installed.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_placeholder_image(path, width, height, bg_color, text, text_color=(255, 255, 255)):
    """Create a placeholder image with text."""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_width, text_height = draw.textsize(text, font=font)
    position = ((width - text_width) // 2, (height - text_height) // 2)
    
    # Draw text
    draw.text(position, text, font=font, fill=text_color)
    
    # Save the image
    img.save(path)
    print(f"Created image: {path}")

def main():
    """Create all placeholder images."""
    # Create directories
    static_dir = "static"
    images_dir = os.path.join(static_dir, "images")
    create_directory(static_dir)
    create_directory(images_dir)
    
    # Create logo
    create_placeholder_image(
        os.path.join(images_dir, "logo.png"),
        200, 60,
        (29, 53, 87),  # Dark blue
        "Rotax Pro Jet",
        (255, 255, 255)  # White text
    )
    
    # Create hero image
    create_placeholder_image(
        os.path.join(images_dir, "hero-image.jpg"),
        800, 400,
        (69, 123, 157),  # Blue
        "Rotax Kart Racing",
        (255, 255, 255)  # White text
    )
    
    # Create about images
    create_placeholder_image(
        os.path.join(images_dir, "about-hero.jpg"),
        800, 400,
        (29, 53, 87),  # Dark blue
        "About Rotax Pro Jet",
        (255, 255, 255)  # White text
    )
    
    create_placeholder_image(
        os.path.join(images_dir, "our-story.jpg"),
        600, 400,
        (69, 123, 157),  # Blue
        "Our Story",
        (255, 255, 255)  # White text
    )
    
    # Create features image
    create_placeholder_image(
        os.path.join(images_dir, "features-hero.jpg"),
        800, 400,
        (168, 218, 220),  # Light blue
        "Rotax Pro Jet Features",
        (29, 53, 87)  # Dark blue text
    )
    
    # Create engine images
    for engine in ["senior-max", "junior-max", "mini-max"]:
        create_placeholder_image(
            os.path.join(images_dir, f"{engine}.jpg"),
            400, 300,
            (230, 57, 70),  # Red
            f"{engine.replace('-', ' ').title()}",
            (255, 255, 255)  # White text
        )
    
    # Create team images
    for i in range(1, 5):
        create_placeholder_image(
            os.path.join(images_dir, f"team-{i}.jpg"),
            200, 200,
            (69, 123, 157),  # Blue
            f"Team Member {i}",
            (255, 255, 255)  # White text
        )
    
    # Create testimonial images
    for i in range(1, 4):
        create_placeholder_image(
            os.path.join(images_dir, f"testimonial-{i}.jpg"),
            100, 100,
            (230, 57, 70),  # Red
            f"User {i}",
            (255, 255, 255)  # White text
        )
    
    # Create partner logos
    for i in range(1, 5):
        create_placeholder_image(
            os.path.join(images_dir, f"partner-{i}.png"),
            200, 80,
            (255, 255, 255),  # White
            f"Partner {i}",
            (29, 53, 87)  # Dark blue text
        )
    
    print("All placeholder images created successfully!")

if __name__ == "__main__":
    main()