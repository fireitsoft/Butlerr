import requests
import random
import string
import re
from datetime import datetime

def add_user(emby_url, emby_api_key, username, password, emby_libs):
    try:
        url = f"{emby_url}/Users/New"

        querystring = {"api_key":emby_api_key}
        payload = {
            "Name": username,
            "Password": password,
            "ConnectUsername": username
        }
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
        userId = response.json()["Id"]
        
        
        if response.status_code != 200:
            print(f"Error creating new emby user: {response.text}")
            return False

        # Set the user password
        url = f"{emby_url}/Users/{userId}/Password"
        
        querystring = {"api_key":emby_api_key}
        
        payload = {
            "Id": userId,
            "CurrentPw": "",
            "NewPw": password,
            "ResetPassword": False
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

        if response.status_code != 204:
            print(f"Error setting user password: {response.text}")
            return False


        #if email was set then we set an emby account
        if is_valid_email(username):
            url = f"{emby_url}/Users/{userId}/Connect/Link"
            #url = f"{emby_url}/Users/{userId}"
            querystring = {"api_key":emby_api_key}
            payload = {
                #"Id": userId,
                "ConnectUsername": username
            }

            headers = {"Content-Type": "application/json"}
            response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

            if response.text == None:
                print(f"Error setting user connect account: {response.text}")
  

        # Grant access to User
        url = f"{emby_url}/Users/{userId}/Policy"

        querystring = {"api_key":emby_api_key}

        enabled_folders = []
        server_libs = get_libraries(emby_url, emby_api_key)
        
        if emby_libs[0] != "all":
            for lib in emby_libs:
                found = False
                for server_lib in server_libs:
                    if lib == server_lib['Name']:
                        enabled_folders.append(server_lib['Guid'])
                        found = True
                if not found:
                    print(f"Couldn't find emby Library: {lib}")
                    
        payload = {
            "IsAdministrator": False,
            "IsHidden": True,
            "IsDisabled": False,
            "BlockedTags": [],
            "EnableUserPreferenceAccess": True,
            "AccessSchedules": [],
            "BlockUnratedItems": [],
            "EnableRemoteControlOfOtherUsers": False,
            "EnableSharedDeviceControl": False,
            "EnableRemoteAccess": True,
            "EnableLiveTvManagement": False,
            "EnableLiveTvAccess": False,
            "EnableMediaPlayback": True,
            "EnableAudioPlaybackTranscoding": True,
            "EnableVideoPlaybackTranscoding": True,
            "EnablePlaybackRemuxing": True,
            "EnableSubtitleDownloading": False,
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
            "EnableAllFolders": emby_libs[0] == "all",
            "InvalidLoginAttemptCount": 0,
            "LoginAttemptsBeforeLockout": -1,
            "MaxActiveSessions": 0,
            "EnablePublicSharing": True,
            "BlockedMediaFolders": [],
            "BlockedChannels": [],
            "EnablePublicSharing": False,
            "RemoteClientBitrateLimit": 0,
            "SimultaneousStreamLimit": 1,
            "AuthenticationProviderId": "emby.Server.Implementations.Users.DefaultAuthenticationProvider",
            "PasswordResetProviderId": "emby.Server.Implementations.Users.DefaultPasswordResetProvider",
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

def get_libraries(emby_url, emby_api_key):
    url = f"{emby_url}/Library/VirtualFolders"
    querystring = {"api_key":emby_api_key}
    response = requests.request("GET", url, params=querystring)

    return  response.json()
    

def verify_username(emby_url, emby_api_key, username):
    users = get_users(emby_url, emby_api_key)
    valid = True
    for user in users:
        if user['Name'] == username:
            valid = False
            break

    return valid

def remove_user(emby_url, emby_api_key, emby_username):
    try:
        # Get User ID
        users = get_users(emby_url, emby_api_key)
        userId = None
        for user in users:
            if user['Name'].lower() == emby_username.lower():
                userId = user['Id']
        
        if userId is None:
            # User not found
            print(f"Error removing user {emby_username} from emby: Could not find user.")
            return False
        
        # Delete User
        url = f"{emby_url}/Users/{userId}"

        querystring = {"api_key":emby_api_key}
        response = requests.request("DELETE", url, params=querystring)

        if response.status_code == 204 or response.status_code == 200:
            return True
        else:
            print(f"Error deleting emby user: {response.text}")
    except Exception as e:
        print(e)
        return False

def get_users(emby_url, emby_api_key):
    url = f"{emby_url}/Users"

    querystring = {"api_key":emby_api_key}
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

def get_config(emby_url, emby_api_key):
    url = f"{emby_url}/System/Configuration"

    querystring = {"api_key":emby_api_key}
    response = requests.request("GET", url, params=querystring, timeout=5)
    return response.json()

def get_status(emby_url, emby_api_key):
    url = f"{emby_url}/System/Configuration"

    querystring = {"api_key":emby_api_key}
    response = requests.request("GET", url, params=querystring, timeout=5)
    return response.status_code

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(regex, email):
        return True
    else:
        return False

def get_lastactivity(emby_url, emby_api_key, emby_username):

    # Get User ID
    users = get_users(emby_url, emby_api_key)
    userId = None
    for user in users:
        if user['Name'].lower() == emby_username.lower():
            userId = user['Id']
        
    if userId is None:
        # User not found
        print(f"Error finding user {emby_username} from Emby: Could not find user.")
        return False
        

    url = f"{emby_url}/Users/{userId}"

    querystring = {"api_key":emby_api_key}
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
  
