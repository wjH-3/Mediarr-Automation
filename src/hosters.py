import requests
import sys
import os
import json

def hosters_status(api_token):
    url = 'https://api.real-debrid.com/rest/1.0/hosts/status'
    headers = {
        'Authorization': f'Bearer {api_token}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()  # Return the JSON directly
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"

def filter_hosters(hosters_data):
    filtered_hosters = []
    
    # Check if hosters_data is a dictionary
    if isinstance(hosters_data, dict):
        for url, hoster in hosters_data.items():
            # Only include hosters with supported: 1
            if hoster.get('supported') == 1:
                filtered_hosters.append({
                    'name': hoster.get('name', 'Unknown'),
                    'url': url,
                    'status': hoster.get('status', 'unknown')
                })
    
    return filtered_hosters

def main():
    # Get the API token from the token.json file
    token_data = None
    if getattr(sys, 'frozen', False):
        token_path = os.path.join(os.path.dirname(sys.executable), 'token.json')
    else:
        token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
    except FileNotFoundError:
        print("API token not found. Please run the main script to set up your token.")
        input("Press Enter to Exit...")
        return
    
    api_token = token_data.get('token')
    if not api_token:
        print("Invalid token data. Please run the main script to set up your token.")
        input("Press Enter to Exit...")
        return
    
    # Get hosters data
    hosters_data = hosters_status(api_token)
    
    # Filter and format hosters
    if isinstance(hosters_data, str):  # Check if it's an error message
        print(hosters_data)
        input("\nPress Enter to Exit...")
        return
        
    filtered_hosters = filter_hosters(hosters_data)
    
    # Print formatted list
    print("\nSupported Hosters' Current Status:\n")
    for hoster in filtered_hosters:
        print(f"- {hoster['name']} ({hoster['url']}) - {hoster['status']}")

    input("\nPress Enter to Exit...")
    return

if __name__ == "__main__":
    main()
