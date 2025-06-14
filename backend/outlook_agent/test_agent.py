import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from main import OutlookAgentFramework
import json

class OutlookAgentTester:
    def __init__(self):
        load_dotenv()
        self.framework = OutlookAgentFramework()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    async def run_test(self, test_name: str, query: str, expected_action: str = None):
        """Run a single test case and record the results."""
        print(f"\n{'='*50}")
        print(f"Running test: {test_name}")
        print(f"Query: {query}")
        print(f"{'='*50}")

        try:
            # Get the action from the reasoning model
            action = await self.framework.reasoning_model.determine_action(query)
            
            # Print reasoning steps
            self.framework.reasoning_model.print_reasoning_steps(query, action)
            
            # Verify the action type if expected_action is provided
            if expected_action and action.action_type != expected_action:
                raise AssertionError(f"Expected action '{expected_action}' but got '{action.action_type}'")
            
            # Execute the action
            await self.framework.process_query(query)
            
            self.test_results["passed"] += 1
            print(f"✅ Test passed: {test_name}")
            
        except Exception as e:
            self.test_results["failed"] += 1
            error_msg = f"❌ Test failed: {test_name}\nError: {str(e)}"
            self.test_results["errors"].append(error_msg)
            print(error_msg)

    async def run_all_tests(self):
        """Run all test cases."""
        print("\nStarting Outlook Agent Tests...")
        
        # Test 1: Schedule a meeting
        await self.run_test(
            "Schedule Meeting",
            "Schedule a meeting with john@example.com and sarah@example.com tomorrow between 9 AM and 5 PM to discuss project updates",
            "find_meeting_slots"
        )

        # Test 2: Read emails
        await self.run_test(
            "Read Emails",
            "Show me my emails from the last 10 days",
            "read_emails"
        )

        # Test 3: View calendar events
        await self.run_test(
            "View Calendar Events",
            "What meetings do I have scheduled for next week?",
            "view_events"
        )

        # Test 4: Send email
        await self.run_test(
            "Send Email",
            "Send an email to sarah@example.com about the project deadline",
            "send_email"
        )

        # Test 5: Invalid query
        await self.run_test(
            "Invalid Query",
            "This is not a valid query for any action",
            "unknown"
        )

        # Test 6: Meeting with specific duration
        await self.run_test(
            "Meeting with Duration",
            "Schedule a 2-hour meeting with the team tomorrow afternoon to discuss the new features",
            "find_meeting_slots"
        )

        # Test 7: Multiple attendees
        await self.run_test(
            "Multiple Attendees",
            "Set up a meeting with john@example.com, sarah@example.com, and mike@example.com next Monday morning",
            "find_meeting_slots"
        )

        # Print test summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print a summary of all test results."""
        print("\n" + "="*50)
        print("Test Summary")
        print("="*50)
        print(f"Total Tests: {self.test_results['passed'] + self.test_results['failed']}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        
        if self.test_results["errors"]:
            print("\nErrors:")
            for error in self.test_results["errors"]:
                print(f"\n{error}")

async def main():
    load_dotenv()
    # Check if access token is available
    if not os.getenv("GRAPH_ACCESS_TOKEN"):
        print("Error: GRAPH_ACCESS_TOKEN not found in environment variables")
        print("Please set up your .env file with the required token")
        return
    # Run the tests
    tester = OutlookAgentTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 