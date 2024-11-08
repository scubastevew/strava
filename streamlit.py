import requests
import streamlit as st
import matplotlib.pyplot as plt
from urllib.parse import urlencode, urlparse, parse_qs

# Strava client credentials (hardcoded for now)
CLIENT_ID = "33110"
CLIENT_SECRET = "ec90483bfa8994b3dc004eb914c7f50a59fc78f1"
REDIRECT_URI = "https://connect.posit.cloud/scubastevew/content/01930e23-a494-1aed-3ae7-1b3cc8c920a6"  # e.g., "http://localhost:8501"
BASE_URL = "https://www.strava.com/api/v3"

# OAuth endpoint
AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/api/v3/oauth/token"

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

def plot_data(distances, avg_powers, elevations, avg_hrs):
    fig, ax = plt.subplots(2, 2, figsize=(10, 8))
    
    ax[0, 0].plot(distances, avg_powers, marker='o', color='b')
    ax[0, 0].set_title("Distance vs Average Power (W)")
    ax[0, 0].set_xlabel("Distance (km)")
    ax[0, 0].set_ylabel("Average Power (W)")

    ax[0, 1].plot(distances, elevations, marker='o', color='g')
    ax[0, 1].set_title("Distance vs Elevation Gain (m)")
    ax[0, 1].set_xlabel("Distance (km)")
    ax[0, 1].set_ylabel("Elevation Gain (m)")

    ax[1, 0].plot(distances, avg_hrs, marker='o', color='r')
    ax[1, 0].set_title("Distance vs Average Heart Rate (bpm)")
    ax[1, 0].set_xlabel("Distance (km)")
    ax[1, 0].set_ylabel("Average Heart Rate (bpm)")

    fig.tight_layout()
    st.pyplot(fig)

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

        activities = get_activities(access_token)
        
        if activities:
            distances = [activity.get("distance", 0) / 1000 for activity in activities]  # in km
            avg_powers = [activity.get("average_watts", 0) for activity in activities]
            elevations = [activity.get("total_elevation_gain", 0) for activity in activities]
            avg_hrs = [activity.get("average_heartrate", 0) for activity in activities]

            # Plot the data
            plot_data(distances, avg_powers, elevations, avg_hrs)

if __name__ == "__main__":
    main()
