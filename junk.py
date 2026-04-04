from PIL import Image

def convert_png_to_ico(png_path, ico_path, sizes=[(16, 16), (32, 32), (64, 64), (128, 128)]):
    # Open the PNG image
    img = Image.open(png_path)
    
    # Ensure the image is in RGBA mode (for transparency support)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Save the image as ICO with specified sizes
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f"ICO file saved as {ico_path}")
