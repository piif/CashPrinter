#!/usr/bin/python3

from PIL import Image
import sys, os

def dump_pixel_map_to_bin(png_file: str, output_file: str = None):
    # Open the image file
    with Image.open(png_file) as img:
        # Convert the image to grayscale ('L') if it's not already
        bw_image = img.convert('L')
        
        # Get the pixel data
        pixels = bw_image.load()
        width, height = bw_image.size
        
        # Generate the pixel map
        pixel_map = []
        for y in range(height):
            row = []
            for x in range(width):
                # Pixel value: 0 is black, 255 is white
                row.append(0 if pixels[x, y] < 128 else 1)
            pixel_map.append(row)
        
        # Dump the pixel map
        if output_file:
            with open(output_file, 'w') as f:
                for row in pixel_map:
                    f.write(''.join(map(str, row)) + '\n')
        else:
            for row in pixel_map:
                print(''.join(map(str, row)))

def dump_pixel_map_to_hex(png_file: str, output_file: str = None, name: str = "IMAGE"):
    # Open the image file
    if output_file is not None:
        output = open(output_file, 'w')
    else:
        output = sys.stdout

    with Image.open(png_file) as img:
        # Convert the image to grayscale ('L') if it's not already
        bw_image = img.convert('L')
        
        # Get the pixel data
        pixels = bw_image.load()
        width, height = bw_image.size

        print(f"{name}_WIDTH = {width}", file=output)
        print(f"{name}_HEIGHT = {height}", file=output)
        print(f"{name}_DATA = [", file=output)

        for y in range(0, height, 8):
            print("  [ ", end='', file=output)
            lines = min(8, height - y)
            for x in range(width):
                value = 0
                for yy in range(y, y+lines):
                    value <<= 1
                    if pixels[x, yy] < 128:
                        value += 1
                value <<= 8-lines
                print(f"0x{value:02X}, ", end='', file=output)
            print("],", file=output)
        print("]", file=output)

    if output_file is not None:
        output.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : {sys.argv[0]} input_file_name", file=sys.err)
    input_path = sys.argv[1]
    split_path = os.path.splitext(input_path)
    dump_pixel_map_to_bin(input_path, f'{split_path[0]}.txt')
    dump_pixel_map_to_hex(input_path, f'{split_path[0]}.py')
