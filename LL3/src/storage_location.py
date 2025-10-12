# Check CrewAI storage location
import os
from pathlib import Path

# Set our custom storage directory
project_root = Path(__file__).parent.parent
storage_dir = project_root / "storage"
os.makedirs(storage_dir, exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir)

print(f"🔧 Custom storage directory set to: {os.environ.get('CREWAI_STORAGE_DIR')}")

# Now import CrewAI to check where it's actually storing files
from crewai.utilities.paths import db_storage_path

# Get the base storage path
storage_path = db_storage_path()
print(f"CrewAI storage location: {storage_path}")

# List all CrewAI storage directories
if os.path.exists(storage_path):
    print("\nStored files and directories:")
    for item in os.listdir(storage_path):
        item_path = os.path.join(storage_path, item)
        if os.path.isdir(item_path):
            print(f"📁 {item}/")
            # Show ChromaDB collections
            if os.path.exists(item_path):
                for subitem in os.listdir(item_path):
                    print(f"   └── {subitem}")
        else:
            print(f"📄 {item}")
else:
    print("No CrewAI storage directory found yet.")

# Also check our custom directory
print(f"\n🔍 Checking custom directory: {storage_dir}")
if os.path.exists(storage_dir):
    print("Custom directory contents:")
    for item in os.listdir(storage_dir):
        item_path = os.path.join(storage_dir, item)
        if os.path.isdir(item_path):
            print(f"📁 {item}/")
            for subitem in os.listdir(item_path):
                print(f"   └── {subitem}")
        else:
            print(f"📄 {item}")
else:
    print("Custom directory is empty or doesn't exist.")

