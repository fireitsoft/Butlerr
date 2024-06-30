import requests
import random
import string

def add_user(jellyfin_url, jellyfin_api_key, username, password, jellyfin_libs):
    try:
        url = f"{jellyfin_url}/Users/New"

        querystring = {"api_key":jellyfin_api_key}
        payload = {
            "Name": username,
            "Password": password
        }
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
        userId = response.json()["Id"]

        if response.status_code != 200:
            print(f"Error creating new Jellyfin user: {response.text}")
            return False
        
        # Grant access to User
        url = f"{jellyfin_url}/Users/{userId}/Policy"

        querystring = {"api_key":jellyfin_api_key}

        enabled_folders = []
        server_libs = get_libraries(jellyfin_url, jellyfin_api_key)
        
        if jellyfin_libs[0] != "all":
            for lib in jellyfin_libs:
                found = False
                for server_lib in server_libs:
                    if lib == server_lib['Name']:
                        enabled_folders.append(server_lib['ItemId'])
                        found = True
                if not found:
                    print(f"Couldn't find Jellyfin Library: {lib}")

        payload = {
            "IsAdministrator": False,
            "IsHidden": True,
            "IsDisabled": False,
            "BlockedTags": [],
            "EnableUserPreferenceAccess": True,
            "AccessSchedules": [],
            "BlockUnratedItems": [],
            "EnableRemoteControlOfOtherUsers": False,
            "EnableSharedDeviceControl": True,
            "EnableRemoteAccess": True,
            "EnableSharedDeviceControl": False,            
            "EnableLiveTvManagement": False,
            "EnableLiveTvAccess": False,
            "EnableMediaPlayback": True,
            "EnableAudioPlaybackTranscoding": True,
            "EnableVideoPlaybackTranscoding": True,
            "EnablePlaybackRemuxing": True,
            "ForceRemoteSourceTranscoding": False,
            "EnableContentDeletion": False,
            "EnableContentDeletionFromFolders": [],
            "EnableContentDownloading": False,
            "EnableSyncTranscoding": False,
            "EnableMediaConversion": False,
            "EnabledDevices": [],
            "EnableAllDevices": True,
            "EnabledChannels": [],
            "EnableAllChannels": False,
            "EnabledFolders": enabled_folders,
            "EnableAllFolders": jellyfin_libs[0] == "all",
            "InvalidLoginAttemptCount": 0,
            "LoginAttemptsBeforeLockout": -1,
            "MaxActiveSessions": 3,
            "EnablePublicSharing": False,
            "BlockedMediaFolders": [],
            "BlockedChannels": [],
            "RemoteClientBitrateLimit": 0,
            "AuthenticationProviderId": "Jellyfin.Server.Implementations.Users.DefaultAuthenticationProvider",
            "PasswordResetProviderId": "Jellyfin.Server.Implementations.Users.DefaultPasswordResetProvider",
           #"SyncPlayAccess": "CreateAndJoinGroups"
            "SyncPlayAccess": "None"
        }
        headers = {"content-type": "application/json"}

        response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            print(f"Error setting user permissions: {response.text}")

    except Exception as e:
        print(e)
        return False

def get_libraries(jellyfin_url, jellyfin_api_key):
    url = f"{jellyfin_url}/Library/VirtualFolders"
    querystring = {"api_key":jellyfin_api_key}
    response = requests.request("GET", url, params=querystring)

    return  response.json()
    

def verify_username(jellyfin_url, jellyfin_api_key, username):
    users = get_users(jellyfin_url, jellyfin_api_key)
    valid = True
    for user in users:
        if user['Name'] == username:
            valid = False
            break

    return valid

def remove_user(jellyfin_url, jellyfin_api_key, jellyfin_username):
    try:
        # Get User ID
        users = get_users(jellyfin_url, jellyfin_api_key)
        userId = None
        for user in users:
            if user['Name'].lower() == jellyfin_username.lower():
                userId = user['Id']
        
        if userId is None:
            # User not found
            print(f"Error removing user {jellyfin_username} from Jellyfin: Could not find user.")
            return False
        
        # Delete User
        url = f"{jellyfin_url}/Users/{userId}"

        querystring = {"api_key":jellyfin_api_key}
        response = requests.request("DELETE", url, params=querystring)

        if response.status_code == 204 or response.status_code == 200:
            return True
        else:
            print(f"Error deleting Jellyfin user: {response.text}")
    except Exception as e:
        print(e)
        return False

def get_users(jellyfin_url, jellyfin_api_key):
    url = f"{jellyfin_url}/Users"

    querystring = {"api_key":jellyfin_api_key}
    response = requests.request("GET", url, params=querystring)

    return response.json()

def generate_password(length, lower=True, upper=True, numbers=True, symbols=False):
    character_list = []
    if not (lower or upper or numbers or symbols):
        raise ValueError("At least one character type must be provided")
        
    if lower:
        character_list += string.ascii_lowercase
    if upper:
        character_list += string.ascii_uppercase
    if numbers:
        character_list += string.digits
    if symbols:
        character_list += string.punctuation

    return "".join(random.choice(character_list) for i in range(length))

def get_config(jellyfin_url, jellyfin_api_key):
    url = f"{jellyfin_url}/System/Configuration"

    querystring = {"api_key":jellyfin_api_key}
    response = requests.request("GET", url, params=querystring, timeout=5)
    return response.json()

def get_status(jellyfin_url, jellyfin_api_key):
    url = f"{jellyfin_url}/System/Configuration"

    querystring = {"api_key":jellyfin_api_key}
    response = requests.request("GET", url, params=querystring, timeout=5)
    return response.status_code

def get_lastactivity(jellyfin_url, jellyfin_api_key, jellyfin_username):

    # Get User ID
    users = get_users(jellyfin_url, jellyfin_api_key)
    userId = None
    for user in users:
        if user['Name'].lower() == jellyfin_username:
            userId = user['Id']
        
    if userId is None:
        # User not found
        print(f"Error finding user {jellyfin_username} from Jellyfin: Could not find user.")
        return False
        

    url = f"{jellyfin_url}/Users/{userId}"

    querystring = {"api_key":jellyfin_api_key}
    response = requests.request("GET", url, params=querystring, timeout=5)
    text = response.json()
    if "LastActivityDate" in text:
        target_date_str = text["LastActivityDate"] 
        target_date_str = target_date_str.split('.')[0] + 'Z'
        target_date = datetime.strptime(target_date_str, "%Y-%m-%dT%H:%M:%SZ")
        current_date = datetime.utcnow()
        time_difference = current_date - target_date
        days_difference = time_difference.days
        return days_difference
    else:
        return False
