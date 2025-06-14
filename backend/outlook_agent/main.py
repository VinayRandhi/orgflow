import asyncio
from outlook_agent import OutlookAgent, TimeSlot
from reasoning_model import ReasoningModel
from datetime import datetime, timedelta
import json

class OutlookAgentFramework:
    def __init__(self):
        self.agent = OutlookAgent()
        self.reasoning_model = ReasoningModel()

    async def process_query(self, query: str):
        """Process a user query using the reasoning model and execute the appropriate action."""
        # Step 1: Determine the action using the reasoning model
        action = await self.reasoning_model.determine_action(query)
        
        # Step 2: Print reasoning steps
        self.reasoning_model.print_reasoning_steps(query, action)
        
        # Step 3: Execute the determined action
        if action.confidence < 0.7:
            print("Confidence too low to execute action")
            return
        
        try:
            if action.action_type == "find_meeting_slots":
                # Find available slots for the meeting
                free_slots = await self.agent.find_free_slots(
                    attendees=action.parameters["attendees"],
                    start_date=datetime.fromisoformat(action.parameters["start_date"]),
                    end_date=datetime.fromisoformat(action.parameters["end_date"]),
                    duration_minutes=action.parameters.get("duration_minutes", 60)
                )
                
                if not free_slots:
                    print("No suitable time slots found for all attendees.")
                    return
                
                # Display available slots to user
                print("\nAvailable time slots:")
                for i, slot in enumerate(free_slots, 1):
                    print(f"{i}. {slot.start_time.strftime('%Y-%m-%d %H:%M')} - {slot.end_time.strftime('%H:%M')}")
                
                # Get user's choice
                choice = input("\nSelect a time slot (enter number) or 'q' to quit: ")
                if choice.lower() == 'q':
                    return
                
                try:
                    slot_index = int(choice) - 1
                    if 0 <= slot_index < len(free_slots):
                        selected_slot = free_slots[slot_index]
                        # Schedule the meeting with the selected slot
                        result = await self.agent.schedule_meeting_with_slot(
                            subject=action.parameters["subject"],
                            slot=selected_slot
                        )
                        print(f"\nMeeting scheduled successfully: {result.get('subject', 'Unknown')}")
                    else:
                        print("Invalid slot selection.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                
            elif action.action_type == "read_emails":
                result = await self.agent.read_emails(**action.parameters)
                print("Emails retrieved:", len(result))
                
            elif action.action_type == "view_events":
                result = await self.agent.view_events(**action.parameters)
                print("Events retrieved:", len(result))
                
            elif action.action_type == "send_email":
                result = await self.agent.send_email(**action.parameters)
                print("Email sent successfully" if result else "Failed to send email")
                
            else:
                print("Unknown action type:", action.action_type)
                
        except Exception as e:
            print(f"Error executing action: {str(e)}")

async def main():
    # Example usage
    framework = OutlookAgentFramework()
    
    # Example queries
    queries = [
        "Schedule a meeting with john@example.com and sarah@example.com tomorrow between 9 AM and 5 PM to discuss project updates",
        "Show me my emails from the last 10 days",
        "What meetings do I have scheduled for next week?",
        "Send an email to sarah@example.com about the project deadline"
    ]
    
    for query in queries:
        print("\nProcessing query:", query)
        await framework.process_query(query)
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 