from typing import List, Dict, Any, Optional
from msgraph.core import GraphClient
from azure.identity import ClientSecretCredential
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
import msal
import requests
from openai import AzureOpenAI
from flask import Flask, request, jsonify

class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    attendees: List[str]

class OutlookAgent:
    def __init__(self, access_token: str = None, client_id: str = None, 
                 client_secret: str = None, tenant_id: str = None):
        load_dotenv()
        self.client_id = client_id or os.getenv("AZURE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("AZURE_CLIENT_SECRET")
        self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
        self.graph_url = "https://graph.microsoft.com/v1.0"
        self.scopes = ["https://graph.microsoft.com/Calendars.ReadWrite"]
        self.access_token = access_token or os.getenv("GRAPH_ACCESS_TOKEN")
        
        # Initialize Azure OpenAI client
        self.openai_client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AzureOpenAI_API_KEY"),
        )
        
        if not self.authenticate():
            raise ValueError("Failed to authenticate with Microsoft Graph API")

    def authenticate(self):
        """Authenticate using MSAL and get access token"""
        if self.access_token:
            return True
            
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            print("Either provide access_token directly or all of: client_id, client_secret, tenant_id")
            return False
            
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )
        
        result = app.acquire_token_silent(self.scopes, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=self.scopes)
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            return True
        else:
            print(f"Authentication failed: {result.get('error_description')}")
            return False
    
    def _make_graph_request(self, endpoint: str, method: str = "GET", data: Dict = None):
        """Make authenticated request to Microsoft Graph API"""
        if not self.access_token:
            if not self.authenticate():
                return None
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.graph_url}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 401:  # Token expired
            if self.authenticate():
                headers["Authorization"] = f"Bearer {self.access_token}"
                if method == "GET":
                    response = requests.get(url, headers=headers)
                elif method == "POST":
                    response = requests.post(url, headers=headers, json=data)
        
        # return response.json() if response.status_code < 400 else None
        if response.status_code < 400:
            return response.json()
        else:
            print(f"[ERROR] Graph API {method} {url} failed with status {response.status_code}")
            print(f"[ERROR] Response body: {response.text}")
            return None

    async def get_attendee_availability(self, attendees: List[str], 
                                      start_time: datetime, 
                                      end_time: datetime,
                                      duration_minutes: int = 60) -> Dict[str, List[Dict[str, Any]]]:
        """Get availability for all attendees within a time range."""
        try:
            request_body = {
                "attendees": [{"emailAddress": {"address": email}} for email in attendees],
                "timeConstraint": {
                    "timeslots": [{
                        "start": {
                            "dateTime": start_time.isoformat(),
                            "timeZone": "UTC"
                        },
                        "end": {
                            "dateTime": end_time.isoformat(),
                            "timeZone": "UTC"
                        }
                    }]
                },
                "meetingDuration": f"PT{duration_minutes}M",
                "returnSuggestionReasons": True,
                "minimumAttendeePercentage": 100
            }
            
            response = self._make_graph_request(
                "/users/me/findMeetingTimes",
                method="POST",
                data=request_body
            )
            print("[DEBUG] Graph API response for findMeetingTimes:", response)
            return response if response else {}
                
        except Exception as e:
            print(f"Error getting attendee availability: {str(e)}")
            return {}

    async def find_free_slots(self, attendees: List[str], 
                            start_date: datetime, 
                            end_date: datetime,
                            duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """Find free time slots where all attendees are available."""
        try:
            availability = await self.get_attendee_availability(
                attendees, start_date, end_date, duration_minutes
            )
            
            suggestions = availability.get("meetingTimeSuggestions", [])
            
            free_slots = []
            for suggestion in suggestions:
                if suggestion.get("confidence", 0) >= 0.8:
                    slot = {
                        "start": suggestion["meetingTimeSlot"]["start"]["dateTime"],
                        "end": suggestion["meetingTimeSlot"]["end"]["dateTime"],
                        "attendees": attendees
                    }
                    free_slots.append(slot)
            
            return free_slots
        except Exception as e:
            print(f"Error finding free slots: {str(e)}")
            return []

    async def schedule_meeting(self, subject: str, start_time: str, duration_minutes: int, 
                             attendees: List[str] = None, location: str = ""):
        """Schedule a new meeting, but first check if all attendees are available. If not, suggest alternative slots."""
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = start_dt + timedelta(minutes=duration_minutes)

            # Step 1: Check attendee availability for the requested slot
            if attendees:
                # Check for conflicts in the requested slot
                availability = await self.get_attendee_availability(
                    attendees, start_dt, end_dt, duration_minutes
                )
                suggestions = availability.get("meetingTimeSuggestions", [])
                # If there is a suggestion with high confidence that matches the requested slot, proceed
                slot_ok = False
                for suggestion in suggestions:
                    slot = suggestion.get("meetingTimeSlot", {})
                    if (
                        suggestion.get("confidence", 0) >= 0.8 and
                        slot.get("start", {}).get("dateTime") == start_dt.isoformat() and
                        slot.get("end", {}).get("dateTime") == end_dt.isoformat()
                    ):
                        slot_ok = True
                        break
                if not slot_ok:
                    # Not all attendees are available, suggest alternatives
                    # Find free slots within the same day
                    alt_start = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
                    alt_end = alt_start + timedelta(days=1)
                    alt_slots = await self.find_free_slots(
                        attendees=attendees,
                        start_date=alt_start,
                        end_date=alt_end,
                        duration_minutes=duration_minutes
                    )
                    # Only suggest slots within 2 hours before or after the requested start time
                    two_hours = timedelta(hours=2)
                    filtered_slots = []
                    for slot in alt_slots:
                        slot_start = datetime.fromisoformat(slot["start"])
                        if abs((slot_start - start_dt).total_seconds()) <= two_hours.total_seconds():
                            filtered_slots.append(slot)
                    return {
                        "status": "conflict",
                        "message": "Not all attendees are available at the requested time. Here are some alternative slots within 2 hours of your requested time.",
                        "suggested_slots": filtered_slots
                    }
            # Step 2: Proceed to schedule if available
            meeting_data = {
                "subject": subject,
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "UTC"
                },
                "location": {
                    "displayName": location
                }
            }
            if attendees:
                meeting_data["attendees"] = [
                    {
                        "emailAddress": {
                            "address": email,
                            "name": email.split("@")[0]
                        },
                        "type": "required"
                    }
                    for email in attendees
                ]
            response = self._make_graph_request("/me/calendar/events", "POST", meeting_data)
            return {"status": "success", "meeting": response}
        except Exception as e:
            print(f"Error scheduling meeting: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_calendar_events(self, days: int = 1, start_date: str = None):
        """Get calendar events for specified number of days"""
        try:
            if start_date:
                start = datetime.fromisoformat(start_date)
            else:
                start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            end = start + timedelta(days=days)
            
            endpoint = f"/me/calendar/events?$filter=start/dateTime ge '{start.isoformat()}' and end/dateTime le '{end.isoformat()}'&$orderby=start/dateTime"
            
            response = self._make_graph_request(endpoint)
            
            if response and "value" in response:
                events = []
                for event in response["value"]:
                    events.append({
                        "id": event["id"],
                        "subject": event["subject"],
                        "start": event["start"]["dateTime"],
                        "end": event["end"]["dateTime"],
                        "location": event.get("location", {}).get("displayName", ""),
                        "attendees": [att["emailAddress"]["address"] for att in event.get("attendees", [])]
                    })
                return events
            return []
        except Exception as e:
            print(f"Error getting calendar events: {str(e)}")
            return []

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language queries using Azure OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": """
                            You are an AI assistant that helps users interact with their Outlook calendar and email. 
                            Analyze the user's query and determine the appropriate action to take. 
                            The available actions are:
                            - find_meeting_slots: For scheduling meetings
                            - read_emails: For reading emails
                            - view_events: For viewing calendar events
                            - send_email: For sending emails
                            
                            Return your response in JSON format with the following structure:
                            {
                                "action": "action_name",
                                "parameters": {
                                    // action-specific parameters
                                },
                                "confidence": 0.0 to 1.0
                            }
                        """
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                # temperature=0.7,
                max_completion_tokens=500,
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "o4-mini")
            )
            
            reasoning = response.choices[0].message.content
            print("\nReasoning:")
            print(reasoning)
            
            try:
                result = json.loads(reasoning)
                action = result.get("action")
                parameters = result.get("parameters", {})
                confidence = result.get("confidence", 0.0)
                
                if confidence < 0.7:
                    return {"action": "unknown", "error": "Low confidence"}
                
                if action == "find_meeting_slots":
                    attendees = parameters.get("attendees", [])
                    start_date = datetime.now() + timedelta(days=1)
                    end_date = start_date + timedelta(days=7)
                    duration = parameters.get("duration_minutes", 60)
                    
                    slots = await self.find_free_slots(
                        attendees=attendees,
                        start_date=start_date,
                        end_date=end_date,
                        duration_minutes=duration
                    )
                    
                    return {
                        "action": "find_meeting_slots",
                        "slots": slots
                    }
                    
                elif action == "view_events":
                    start_date = datetime.now()
                    end_date = start_date + timedelta(days=7)
                    events = await self.get_calendar_events(7)
                    return {"action": "view_events", "events": events}
                    
                else:
                    return {"action": "unknown", "error": "Unsupported action"}
                    
            except json.JSONDecodeError:
                print("Failed to parse model response as JSON")
                return {"action": "unknown", "error": "Invalid response format"}
                
        except Exception as e:
            print(f"Error in process_query: {str(e)}")
            return {"action": "unknown", "error": str(e)}

# Flask web service
app = Flask(__name__)
agent = None

@app.route('/setup', methods=['POST'])
def setup_agent():
    """Initialize the agent with credentials or access token"""
    global agent
    data = request.json
    
    try:
        if 'access_token' in data:
            agent = OutlookAgent(access_token=data['access_token'])
            return jsonify({"status": "success", "message": "Agent initialized with access token"})
        
        elif all(k in data for k in ['client_id', 'client_secret', 'tenant_id']):
            agent = OutlookAgent(
                client_id=data['client_id'],
                client_secret=data['client_secret'],
                tenant_id=data['tenant_id']
            )
            return jsonify({"status": "success", "message": "Agent initialized with Azure AD credentials"})
        else:
            return jsonify({
                "status": "error", 
                "message": "Provide either 'access_token' OR all of: 'client_id', 'client_secret', 'tenant_id'"
            }), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/query', methods=['POST'])
async def handle_query():
    """Handle natural language queries"""
    global agent
    
    if not agent:
        return jsonify({"status": "error", "message": "Agent not initialized"}), 400
    
    data = request.json
    query = data.get('query', '')
    
    try:
        response = await agent.process_query(query)
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/schedule', methods=['POST'])
async def schedule_meeting():
    """Schedule a new meeting"""
    global agent
    
    if not agent:
        return jsonify({"status": "error", "message": "Agent not initialized"}), 400
    
    data = request.json
    
    try:
        result = await agent.schedule_meeting(
            subject=data['subject'],
            start_time=data['start_time'],
            duration_minutes=data.get('duration', 60),
            attendees=data.get('attendees', []),
            location=data.get('location', '')
        )
        
        if result.get("status") == "success":
            return jsonify({"status": "success", "meeting": result["meeting"]})
        elif result.get("status") == "conflict":
            return jsonify({
                "status": "conflict",
                "message": result["message"],
                "suggested_slots": result["suggested_slots"]
            }), 409
        else:
            return jsonify({"status": "error", "message": result.get("message", "Failed to create meeting")}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Outlook Calendar Agent Server")
    print("Endpoints:")
    print("POST /setup - Initialize with Azure AD credentials")
    print("POST /query - Ask natural language questions")
    print("POST /schedule - Schedule meetings")
    print("\nStarting server on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 