from apprepocl import AppRepoClient, Log, Changelog

client = AppRepoClient("http://localhost:8000")


pause = 1

# List applications
apps = client.list_applications()
print(f"Available applications: {apps}")

# Upload a new app
resp = client.upload_application(
    application_name="MyApp",
    version="1.0.0",
    file_path=r"C:\developer\repos\application-repository\module\tests\test_myapp.test",
    clobber=False,
    auto_increment_index=-1,
)
print(f"Upload response: {resp}")
# from pprint import pprint
# Download an app to downloads directory
file_path = client.download_application("MyApp", "1.0.0", "downloads/")
print(f"Downloaded to {file_path}")

# # Download an app to downloads directory with new name
# file_path = client.download_application("MyApp", "1.0.0", "downloads/new_name.txt")
# print(f"Downloaded to {file_path}")

# List applications
apps = client.list_applications()
print(f"Available applications: {apps}")

# Add some change logs
client.add_log("MyApp", Log("1.0.0", "Changed thing number 1", ticket="MT-1234"))
client.add_log("MyApp", Log("1.0.0", "Changed thing number 2", ticket="MT-5678"))

logs = client.get_logs("MyApp", "1.0.0")
print(f"Change logs for that app/version: {logs}")