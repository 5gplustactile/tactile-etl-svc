import requests
import json

# Function to make a GET request
def make_get_request(url, params=None, headers=None):
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()  # Assuming the response is in JSON format
    except requests.exceptions.RequestException as e:
        print(f"Error making GET request: {e}")
        return None

# Function to make a POST request
def make_post_request(url, data=None, json=None, headers=None):
    try:

        #response = requests.post(url, data=data, json=json, headers=headers)
        response = requests.request("POST", url, headers=headers, data=data, json=json)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error making POST request: {e}")
        return None

# Function to make a PUT request
def make_put_request(url, data=None, json=None, headers=None):
    try:
        response = requests.put(url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making PUT request: {e}")
        return None

# Function to make a DELETE request
def make_delete_request(url, headers=None):
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making DELETE request: {e}")
        return None

# Example usage of the functions
if __name__ == "__main__":
    url = "https://api.example.com/resource"

    # GET request example
    response = make_get_request(url, params={"key": "value"})
    print("GET response:", response)

    # POST request example
    response = make_post_request(url, json={"key": "value"})
    print("POST response:", response)

    # PUT request example
    response = make_put_request(url, json={"key": "new_value"})
    print("PUT response:", response)

    # DELETE request example
    response = make_delete_request(url)
    print("DELETE response:", response)
