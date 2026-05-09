import os
import sys
from datetime import datetime
import piexif
from mutagen.mp4 import MP4
from mutagen.png import PNG

def validate_date(date_str):
    """Checks if the date is in the correct YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def handle_jpeg(file_path, expiry_date):
    """Writes expiry date to EXIF UserComment for JPEGs."""
    # Load existing exif data or create new if empty
    exif_dict = piexif.load(file_path)
    
    # UserComment needs to be encoded in bytes
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = f"Expiry:{expiry_date}".encode('utf-8')
    
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_path)
    
    # Read back to confirm
    new_exif = piexif.load(file_path)
    comment = new_exif["Exif"].get(piexif.ExifIFD.UserComment, b"").decode('utf-8')
    print(f"Successfully verified JPEG metadata: {comment}")

def handle_png(file_path, expiry_date):
    """Writes expiry date to a custom text chunk for PNGs."""
    audio = PNG(file_path)
    audio["ExpiryDate"] = expiry_date
    audio.save()
    
    # Read back to confirm
    verification = PNG(file_path)
    print(f"Successfully verified PNG metadata: {verification.get('ExpiryDate')}")

def handle_mp4(file_path, expiry_date):
    """Writes expiry date to a custom metadata tag for MP4s."""
    video = MP4(file_path)
    # MP4 tags usually use four-letter keys; we'll use a custom one
    video["----:com.apple.metadata:Expiry"] = expiry_date.encode('utf-8')
    video.save()
    
    # Read back to confirm
    verification = MP4(file_path)
    val = verification.get("----:com.apple.metadata:Expiry", [b""])[0].decode('utf-8')
    print(f"Successfully verified MP4 metadata: {val}")

def main():
    # Simple CLI input handling
    if len(sys.argv) != 3:
        print("Usage: python expire_tool.py <file_path> <YYYY-MM-DD>")
        return

    path = sys.argv[1]
    expiry_date = sys.argv[2]

    # 1. Check if file exists
    if not os.path.exists(path):
        print(f"Error: File '{path}' not found.")
        return

    # 2. Validate date format
    if not validate_date(expiry_date):
        print("Error: Date must be in YYYY-MM-DD format.")
        return

    # 3. Determine file type and process
    extension = os.path.splitext(path)[1].lower()
    
    try:
        if extension in ['.jpg', '.jpeg']:
            handle_jpeg(path, expiry_date)
        elif extension == '.png':
            handle_png(path, expiry_date)
        elif extension == '.mp4':
            handle_mp4(path, expiry_date)
        else:
            print(f"Error: Unsupported file format '{extension}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()