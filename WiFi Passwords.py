import subprocess

data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
profiles = [i.split(":")[1].strip() for i in data if "All User Profile" in i]
for profile in profiles:
    try:
        results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('utf-8').split('\n')
        password = [i.split(":")[1].strip() for i in results if "Key Content" in i]
        print(f"Profile: {profile}\nPassword: {password[0]}\n")
    except Exception as e:
        print(f"Error occurred for profile {profile}: {e}")