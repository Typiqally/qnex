import json
import os
from typing import Optional, Dict, Any, List


class ProfileManager:
    def __init__(self, directory: str) -> None:
        self.directory = directory
        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)

    def load_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Load a profile from a JSON file."""
        file_name = profile_name + ".json"
        file_path = os.path.join(self.directory, file_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {file_name}.")
            except Exception as e:
                print(f"An error occurred while loading {file_name}: {e}")
        else:
            print(f"Profile {file_name} does not exist.")
        return None

    def save_profile(self, profile_name: str, data: Dict[str, Any]) -> None:
        """Save a profile to a JSON file."""
        file_name = profile_name + ".json"
        file_path = os.path.join(self.directory, file_name)
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Profile saved to {file_name}")
        except Exception as e:
            print(f"An error occurred while saving {file_name}: {e}")

    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile JSON file."""
        file_name = profile_name + ".json"
        file_path = os.path.join(self.directory, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Profile {file_name} has been deleted.")
                return True
            except Exception as e:
                print(f"An error occurred while deleting {file_name}: {e}")
        else:
            print(f"Profile {file_name} does not exist.")
        return False

    def list_profiles(self) -> List[str]:
        """List all profile filenames in the directory with value and label."""
        try:
            # Get all files in the directory that have a .json extension
            files = [f for f in os.listdir(self.directory) if f.endswith('.json')]
            # Create a list of dictionaries with "value" and "label"
            return [os.path.splitext(f)[0] for f in files]
        except Exception as e:
            print(f"An error occurred while listing profiles: {e}")
            return []
