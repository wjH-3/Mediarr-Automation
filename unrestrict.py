import requests
import sys
import os
import json

def unrestrict_link(api_token, link):
    url = 'https://api.real-debrid.com/rest/1.0/unrestrict/link'
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'link': link
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"

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
        return
    
    api_token = token_data.get('token')
    if not api_token:
        print("Invalid token data. Please run the main script to set up your token.")
        return
    
    link = input("Enter Hoster Link: ")

    # Call the function to unrestrict the link
    result = unrestrict_link(api_token, link)

    # Output the result in a formatted way
    if isinstance(result, dict):
        print("\nDownload Link:", result.get('download', 'No link found'))
    else:
        print(result)

if __name__ == "__main__":
    main()
