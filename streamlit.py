import requests
import streamlit as st
from urllib.parse import urlencode
import time

# Strava client credentials (hardcoded for now)
CLIENT_ID = "33110"
CLIENT_SECRET = "ec90483bfa8994b3dc004eb914c7f50a59fc78f1"
REDIRECT_URI = "https://connect.posit.cloud/scubastevew/content/01930e23-a494-1aed-3ae7-1b3cc8c920a6"  # or your ngrok public URL for testing
BASE_URL = "https://www.strava.com/api/v3"

# OAuth endpoints
AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"

def get_strava_authorization_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "activity:read_all",
        "approval_prompt": "auto"
    }
    return f"{AUTH_URL}?{urlencode(params)}"

def exchange_code_for_tokens(code):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch tokens")
        return None

def refresh_access_token(refresh_token):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to refresh token")
        return None

def get_activities(access_token):
    url = f"{BASE_URL}/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch activities: {response.status_code}")
        return []

# Streamlit UI
def main():
    st.title("Strava Ride Data Visualization with OAuth")

    # Step 1: Authorization
    if "access_token" not in st.session_state:
        auth_url = get_strava_authorization_url()
        st.markdown(f"[Authorize with Strava]({auth_url})")
        
        # Step 2: Check if user has been redirected with authorization code
        if "code" in st.query_params:
            code = st.query_params["code"][0]
            token_data = exchange_code_for_tokens(code)
            if token_data:
                st.session_state["access_token"] = token_data["access_token"]
                st.session_state["refresh_token"] = token_data["refresh_token"]
                st.session_state["expires_at"] = token_data["expires_at"]
    else:
        # Step 3: Use access token to get activities
        access_token = st.session_state["access_token"]
        
        # Refresh the access token if expired
        if st.session_state["expires_at"] < int(time.time()):
            token_data = refresh_access_token(st.session_state["refresh_token"])
            if token_data:
                st.session_state["access_token"] = token_data["access_token"]
                st.session_state["refresh_token"] = token_data["refresh_token"]
                st.session_state["expires_at"] = token_data["expires_at"]

        # Fetch and display activities
        activities = get_activities(access_token)
        
        if activities:
            # Display a table with activity data
            activity_data = [
                {
                    "Date": activity.get("start_date_local", "N/A"),
                    "Distance (km)": activity.get("distance", 0) / 1000,
                    "Avg Power (W)": activity.get("average_watts", "N/A"),
                    "Elevation Gain (m)": activity.get("total_elevation_gain", "N/A"),
                    "Avg Heart Rate (bpm)": activity.get("average_heartrate", "N/A")
                }
                for activity in activities
            ]
            st.write(activity_data)  # Display the list of activities as a table

if __name__ == "__main__":
    main()
