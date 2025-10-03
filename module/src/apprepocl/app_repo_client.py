import requests
from pathlib import Path
from typing import Union, Optional, List
from .change_log import Log


class AppRepoClient:
    """
    A client for interacting with the Application Repository API.
    """

    def __init__(self, base_url=None):
        self.base_url = base_url.rstrip("/") if base_url else "http://localhost:8000"

    def list_applications(self):
        """
        Get a list of all applications and their versions.
        """
        url = f"{self.base_url}/applications"

        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()

    def upload_application(
        self,
        application_name: str,
        version: str,
        file_path: str,
        clobber: bool = False,
        auto_increment_index: Optional[int] = None
    ):
        """
        Uploads an application to the API.

        Args:
            application_name (str): Name of the application
            version (str): Version string (e.g., '1.0.0')
            file_path (str): Path to the file being uploaded
            clobber (bool): Replace existing version if it exists
            auto_increment_index (Optional[int]): Version index to auto-increment (0=major, 1=minor, 2=patch).
                                                None means no auto-increment
        """
        file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        files = {"file": (file_path.name, open(file_path, "rb"))}
        data = {
            "application_name": application_name,
            "version": version,
            "clobber": str(clobber).lower(),  # FastAPI expects 'true'/'false' as form values
        }

        # Only include auto_increment if it is not None
        if auto_increment_index is not None:
            data["auto_increment_index"] = str(auto_increment_index)

        response = requests.post(f"{self.base_url}/upload", data=data, files=files)

        # Close the opened file
        files["file"][1].close()

        try:
            response.raise_for_status()
        except requests.HTTPError:
            # Return API error message
            try:
                return response.json()
            except Exception:
                raise

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

    def add_log(self, app_name: str, log: Log) -> Log:
        """
        Add a log for a given app and version.
        """
        api_url = f"{self.base_url}/apps/{app_name}/logs"
        response = requests.post(api_url, json={
            "version": log.version,
            "ticket": log.ticket,
            "description": log.description,
            "visible": log.visible
        })

        response.raise_for_status()
        data = response.json()

        return Log(
            version=data["version"],
            description=data["description"],
            ticket=data.get("ticket"),
            visible=data.get("visible", True)
        )

    def get_logs(self, app_name: str, version: Optional[str] = None) -> List[Log]:
        """
        Get logs for an app. If version is specified, only logs for that version.
        """
        if version:
            api_url = f"{self.base_url}/apps/{app_name}/versions/{version}/logs"
        else:
            api_url = f"{self.base_url}/apps/{app_name}/logs"

        response = requests.get(api_url)

        response.raise_for_status()
        data = response.json()

        return [
            Log(
                version=item["version"],
                description=item["description"],
                ticket=item.get("ticket"),
                visible=item.get("visible", True)
            )
            for item in data
        ]
