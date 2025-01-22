import os
import shutil

def organize_files(directory='.'):
    """
    Organize files in the given directory into subdirectories based on file extensions.
    
    Args:
        directory (str, optional): Path to the directory to organize. Defaults to current directory.
    """
    # Dictionary to map file extensions to folder names
    extension_map = {
        # Images
        '.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images', '.gif': 'Images', '.bmp': 'Images', '.tiff': 'Images', 
        '.webp': 'Images',
        
        # Documents
        '.pdf': 'Documents', '.doc': 'Documents', '.docx': 'Documents', '.txt': 'Documents', 
        '.rtf': 'Documents', '.odt': 'Documents', '.xlsx': 'Documents', '.xls': 'Documents', 
        '.ppt': 'Documents', '.pptx': 'Documents',
        
        # Videos
        '.mp4': 'Videos', '.avi': 'Videos', '.mkv': 'Videos', '.mov': 'Videos', '.wmv': 'Videos', 
        '.flv': 'Videos', '.webm': 'Videos',
        
        # Audio
        '.mp3': 'Audio', '.wav': 'Audio', '.flac': 'Audio', '.m4a': 'Audio', '.aac': 'Audio',
        
        # Archives
        '.zip': 'Archives', '.rar': 'Archives', '.7z': 'Archives', '.tar': 'Archives', 
        '.gz': 'Archives', '.bz2': 'Archives',
        
        # Code
        '.py': 'Code', '.js': 'Code', '.html': 'Code', '.css': 'Code', '.java': 'Code', 
        '.cpp': 'Code', '.c': 'Code', '.rb': 'Code', '.php': 'Code',
    }

    # Ensure we're working with the full path
    directory = os.path.abspath(directory)
    
    # Counter for moved files
    moved_files = 0

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        # Skip if it's a directory
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath):
            continue
        
        # Get the file extension
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Determine the destination folder
        dest_folder = extension_map.get(file_ext, 'Miscellaneous')
        
        # Create the destination folder if it doesn't exist
        dest_path = os.path.join(directory, dest_folder)
        os.makedirs(dest_path, exist_ok=True)
        
        # Move the file
        try:
            shutil.move(filepath, os.path.join(dest_path, filename))
            moved_files += 1
        except Exception as e:
            print(f"Error moving {filename}: {e}")
    
    print(f"Organized {moved_files} files into categorized folders.")

def main():
    print("Starting file organization...")
    organize_files()
    print("File organization complete!")

if __name__ == "__main__":
    main()