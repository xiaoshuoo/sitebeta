import os
import glob
from convert_to_utf8 import convert_to_utf8

def convert_all_lectures(output_dir='utf8_converted'):
    """Convert all .txt files in the current directory to UTF-8."""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Find all .txt files in the current directory
    txt_files = glob.glob('*.txt')
    
    print(f"Found {len(txt_files)} .txt files")
    
    # Convert each file
    success_count = 0
    for file_path in txt_files:
        if convert_to_utf8(file_path, output_dir):
            success_count += 1
    
    print(f"Successfully converted {success_count} out of {len(txt_files)} files")

if __name__ == "__main__":
    convert_all_lectures() 