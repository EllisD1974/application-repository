from apprepocl import AppRepoClient

client = AppRepoClient("http://localhost:8000")

# List applications
apps = client.list_applications()
print("Available applications:", apps)

# Upload a new app
resp = client.upload_application(
    application_name="MyApp",
    version="1.0.0",
    file_path=r"C:\developers\repos\application-repository\module\tests\test_myapp.test",
    clobber=False,
    auto_increment_index=None,
)
print("Upload response:", resp)

# # Download an app to downloads directory
# file_path = client.download_application("MyApp", "1.0.0", "downloads/")
# print(f"Downloaded to {file_path}")

# # Download an app to downloads directory with new name
# file_path = client.download_application("MyApp", "1.0.0", "downloads/new_name.txt")
# print(f"Downloaded to {file_path}")

# List applications
apps = client.list_applications()
print("Available applications:", apps)
