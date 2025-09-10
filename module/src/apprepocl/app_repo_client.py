import requests
from pathlib import Path
from typing import Union


class AppRepoClient:
    """
    A client for interacting with the Application Repository API.
    """

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip("/")


    def list_applications(self):
        """
        Get a list of all applications and their versions.
        """
        url = f"{self.base_url}/applications"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


    def upload_application(self, application_name: str, version: str, file_path: str, 
        clobber: bool = False, auto_increment: bool = False):
        """
        Upload a new application or a new version of an existing application.

        Args:
            application_name (str): Name of the application
            version (str): Version string (e.g., "1.0.0")
            file_path (str): Path to the file being uploaded

        Returns:
            dict: JSON response from the API
        """
        api_url = f"{self.base_url}/upload"
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            data = {
                "application_name": application_name,
                "version": version,
                "clobber": clobber,
                "auto_increment": auto_increment,
            }
            response = requests.post(api_url, data=data, files=files)

        response.raise_for_status()  # raises error if request failed
        return response.json()


    def download_application(self, name: str, version: str, save_path: Union[str, Path]):
        """
        Download an application by name and version.
        save_path can be either a directory (file will be saved with its original name)
        or a full file path (directory + filename).
        """
        api_url = f"{self.base_url}/download-app/{name}/{version}"
        response = requests.get(api_url, stream=True)
        response.raise_for_status()

        save_path = Path(save_path)

        # If save_path is a directory, figure out filename
        if save_path.is_dir() or save_path.suffix == "":
            # Try Content-Disposition header first
            cd = response.headers.get("Content-Disposition")
            if cd and "filename=" in cd:
                filename = cd.split("filename=")[-1].strip('"')
            else:
                # Fallback: use the last part of the URL
                filename = api_url.rstrip("/").split("/")[-1]

            save_path = save_path / filename

        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return save_path
