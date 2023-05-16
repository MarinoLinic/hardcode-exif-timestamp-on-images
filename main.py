from PIL import Image, ImageDraw, ImageFont, ExifTags
import os
import random
import string
from datetime import datetime

# Input and output directories
input_dir = "Input"
output_dir = "Output"

# Text color
text_color = (255, 255, 255)  # White


def get_image_date(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    if exif_data is not None:
        for tag, value in exif_data.items():
            if tag in ExifTags.TAGS and ExifTags.TAGS[tag] == 'DateTimeOriginal':
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    return None


def generate_random_filename():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{random_string}.jpg"


def add_timestamp(image_path):
    image = Image.open(image_path)
    width, height = image.size

    # Get the image date taken from metadata
    image_date = get_image_date(image_path)
    if image_date is None:
        # Rename the file randomly
        random_filename = generate_random_filename()
        output_path = os.path.join(output_dir, random_filename)
        image.save(output_path)
        return

    # Check the image orientation
    orientation = None
    for tag, value in image._getexif().items():
        if tag in ExifTags.TAGS and ExifTags.TAGS[tag] == 'Orientation':
            orientation = value
            break

    # Rotate and transpose the image based on the orientation tag
    if orientation == 3:
        image = image.rotate(180, expand=True)
    elif orientation == 6:
        image = image.rotate(-90, expand=True)
        width, height = height, width
    elif orientation == 8:
        image = image.rotate(90, expand=True)
        width, height = height, width

    # Calculate the desired text size based on the width of the image
    text_size = int(width * 0.2 * 0.2)  # around 40% of the image width

    # Load the font
    font = ImageFont.truetype("arial.ttf", text_size)

    # Create a new image with black background
    timestamped_image = Image.new("RGB", (width, height))
    timestamped_image.paste(image)

    # Convert the image date to string format
    timestamp = image_date.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate the position for the timestamp text
    text_width, text_height = font.getlength(timestamp), font.getbbox(timestamp)[3]
    text_position = (width - text_width - 10, height - text_height - 10)

    # Add black outline to the text
    outline_size = 2
    outline_box = (
        text_position[0] - outline_size - (text_width * 0.02),
        text_position[1] - outline_size,
        text_position[0] + text_width + outline_size + (text_width * 0.02),
        text_position[1] + text_height + outline_size + (text_height * 0.1),
    )
    draw = ImageDraw.Draw(timestamped_image)
    draw.rectangle(outline_box, fill=(0, 0, 0))  # Black outline

    # Add the timestamp text to the image
    draw.text(text_position, timestamp, font=font, fill=text_color)

    # Save the timestamped image with the timestamp as the filename
    timestamp_filename = f"{timestamp.replace(':', '-')}.jpg"
    output_path = os.path.join(output_dir, timestamp_filename)
    timestamped_image.save(output_path)


# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process each image in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(input_dir, filename)
        add_timestamp(image_path)
