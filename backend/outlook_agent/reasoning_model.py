from typing import Dict, Any, List
import openai
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from openai import AzureOpenAI

class Action(BaseModel):
    action_type: str
    parameters: Dict[str, Any]
    confidence: float

class MeetingRequest(BaseModel):
    subject: str
    attendees: List[str]
    start_date: datetime
    end_date: datetime
    duration_minutes: int = 60

class ReasoningModel:
    def __init__(self):
        load_dotenv()
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_name = "o4-mini"

        subscription_key = os.getenv("AzureOpenAI_API_KEY")
        api_version = "2024-12-01-preview"

        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=subscription_key,
        )

        self.available_actions = {
            "find_meeting_slots": "Find available time slots for a meeting",
            "schedule_meeting": "Schedule a meeting in a specific time slot",
            "read_emails": "Read emails from a specified folder",
            "view_events": "View calendar events",
            "send_email": "Send an email"
        }
        # O3-mini specific configuration
        self.model_config = {
            "model": "o4-mini",
            "temperature": 0.3,
            "max_tokens": 500,
            "top_p": 0.95,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the reasoning model."""
        return f"""You are an Outlook agent reasoning model. Your job is to determine which action to take based on the user's query.
        Available actions:
        {json.dumps(self.available_actions, indent=2)}
        
        For each query, you should:
        1. Analyze the intent of the query
        2. Determine which action(s) to take
        3. Extract relevant parameters
        4. Provide confidence score for your decision
        
        For meeting scheduling:
        - First use 'find_meeting_slots' to get available slots
        - Then use 'schedule_meeting' to book the selected slot
        
        Respond in JSON format with the following structure:
        {{
            "action_type": "one of the available actions",
            "parameters": {{
                "subject": "meeting subject",
                "attendees": ["email1", "email2"],
                "start_date": "ISO datetime",
                "end_date": "ISO datetime",
                "duration_minutes": 60
            }},
            "confidence": 0.0 to 1.0
        }}
        """

    def _extract_meeting_details(self, query: str) -> MeetingRequest:
        """Extract meeting details from the query using O3-mini."""
        try:
            # Create a more focused prompt for O3-mini
            prompt = f"""Extract meeting details from this query: "{query}"
            Return a JSON object with:
            - subject: meeting subject
            - attendees: list of email addresses
            - start_date: ISO datetime for start of search range
            - end_date: ISO datetime for end of search range
            - duration_minutes: meeting duration in minutes (default 60)
            """

            response = self.client.chat.completions.create(
                model=self.model_config["model"],
                messages=[
                    {"role": "system", "content": "You are a precise meeting details extractor. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                # temperature=self.model_config["temperature"],
                max_completion_tokens=self.model_config["max_tokens"],
                # top_p=self.model_config["top_p"]
            )
            
            details = json.loads(response.choices[0].message.content)
            return MeetingRequest(**details)
        except Exception as e:
            print(f"Error extracting meeting details: {str(e)}")
            return None

    async def determine_action(self, query: str) -> Action:
        """Determine which action to take based on the user's query."""
        try:
            # First, check if this is a meeting scheduling request
            meeting_details = self._extract_meeting_details(query)
            
            if meeting_details:
                # If it's a meeting request, first find available slots
                return Action(
                    action_type="find_meeting_slots",
                    parameters=meeting_details.dict(),
                    confidence=0.9
                )
            
            # For other queries, use the standard reasoning with O3-mini
            response = self.client.chat.completions.create(
                model=self.model_config["model"],
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": query}
                ],
                # temperature=self.model_config["temperature"],
                max_completion_tokens=self.model_config["max_tokens"],
                # top_p=self.model_config["top_p"]
            )
            
            result = json.loads(response.choices[0].message.content)
            return Action(**result)
        except Exception as e:
            print(f"Error in reasoning model: {str(e)}")
            return Action(
                action_type="unknown",
                parameters={},
                confidence=0.0
            )

    def print_reasoning_steps(self, query: str, action: Action):
        """Print the reasoning steps for the determined action."""
        print("\nReasoning Steps:")
        print("1. User Query:", query)
        print("2. Determined Action:", action.action_type)
        print("3. Parameters:", json.dumps(action.parameters, indent=2))
        print("4. Confidence Score:", action.confidence)
        print("5. Available Actions:", json.dumps(self.available_actions, indent=2))
        print("\n") 