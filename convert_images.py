import base64
import os
import json
import re
from PIL import Image
import io
import requests

# Function to resize and convert an image file to base64
def image_to_base64(image_path, max_width=720):
    try:
        # Open the image with PIL
        img = Image.open(image_path)
        
        # Calculate new dimensions while maintaining aspect ratio
        width_percent = max_width / float(img.size[0])
        new_height = int(float(img.size[1]) * width_percent)
        
        # Resize the image
        img = img.resize((max_width, new_height), Image.LANCZOS)
        
        # Save to a bytes buffer with compression
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True, quality=85)
        buffer.seek(0)
        
        # Convert to base64
        encoded_string = base64.b64encode(buffer.read()).decode('utf-8')
        
        print(f"Resized {image_path}: {img.size[0]}x{img.size[1]} pixels")
        
        # Return the data URL format
        return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

# Function to download, resize and convert URL to base64
def url_to_base64(url, max_width=720):
    import requests
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Open the image with PIL
            img = Image.open(io.BytesIO(response.content))
            
            # Calculate new dimensions while maintaining aspect ratio
            width_percent = max_width / float(img.size[0])
            new_height = int(float(img.size[1]) * width_percent)
            
            # Resize the image
            img = img.resize((max_width, new_height), Image.LANCZOS)
            
            # Save to a bytes buffer with compression
            buffer = io.BytesIO()
            img.save(buffer, format='PNG', optimize=True, quality=85)
            buffer.seek(0)
            
            # Convert to base64
            encoded_string = base64.b64encode(buffer.read()).decode('utf-8')
            
            print(f"Resized icon from URL: {img.size[0]}x{img.size[1]} pixels")
            
            return f"data:image/png;base64,{encoded_string}"
        else:
            print(f"Failed to download {url}: HTTP {response.status_code}")
            return url
    except Exception as e:
        print(f"Error downloading/processing {url}: {e}")
        return url

# Path to your HTML file
html_path = "index.html"

# Read the HTML file
with open(html_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# Process local images in locations array
base_dir = os.path.dirname(os.path.abspath(html_path))

# Find and convert each image in the locations array
locations_pattern = r'const locations = \[([\s\S]*?)\];'
locations_match = re.search(locations_pattern, html_content)

if locations_match:
    locations_text = locations_match.group(1)
    
    # Find image entries
    image_pattern = r'image: "(assets/[^"]+)"'
    
    # Process each image
    def replace_image(match):
        image_path = match.group(1)
        full_path = os.path.join(base_dir, image_path)
        
        # Convert image to base64
        base64_data = image_to_base64(full_path, max_width=720)
        if base64_data:
            return f'image: "{base64_data}"'
        else:
            return match.group(0)  # Keep original if conversion fails
    
    # Replace all image references with base64 data
    new_locations_text = re.sub(image_pattern, replace_image, locations_text)
    
    # Update the HTML content
    html_content = html_content.replace(locations_match.group(1), new_locations_text)

# Convert icon URL to base64
icon_pattern = r'iconUrl: \'([^\']+)\''
icon_match = re.search(icon_pattern, html_content)

if icon_match:
    icon_url = icon_match.group(1)
    if icon_url.startswith('http'):
        # It's a remote URL
        base64_icon = url_to_base64(icon_url, max_width=32)  # Icon is 32x32
        if base64_icon:
            html_content = html_content.replace(f"iconUrl: '{icon_url}'", f"iconUrl: '{base64_icon}'")

# Save the modified HTML file
output_path = "index_embedded.html"
with open(output_path, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"Embedded resized images saved to {output_path}")
print("You can now distribute this single HTML file with all images embedded at lower resolution.")