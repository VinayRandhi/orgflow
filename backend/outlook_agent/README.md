# Outlook Agent Framework

This framework provides an intelligent agent for interacting with Microsoft Outlook using the Microsoft Graph API. The agent can schedule meetings, read emails, view events, and send emails, all powered by an AI reasoning model that determines the appropriate actions based on natural language queries.

## Features

- Schedule meetings
- Read emails
- View calendar events
- Send emails
- AI-powered reasoning for natural language queries
- Detailed reasoning steps for each action

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. For testing with direct access token:
   - Go to [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
   - Sign in with your Microsoft account
   - Request the following permissions:
     - Mail.Read
     - Mail.Send
     - Calendars.ReadWrite
     - User.Read
   - Copy the access token from the "Access token" field
   - Note: This token is temporary and will expire

3. Create a `.env` file in the `outlook_agent` directory with the following variables:
```
GRAPH_ACCESS_TOKEN=your_microsoft_graph_access_token
OPENAI_API_KEY=your_openai_api_key
```

## Usage

```python
from main import OutlookAgentFramework
import asyncio

async def example():
    framework = OutlookAgentFramework()
    
    # Example queries
    await framework.process_query("Schedule a meeting with john@example.com tomorrow at 2 PM")
    await framework.process_query("Show me my emails from the last 10 days")
    await framework.process_query("What meetings do I have scheduled for next week?")

asyncio.run(example())
```

## How It Works

1. The framework uses a direct access token for Microsoft Graph API authentication
2. The reasoning model powered by O3-mini analyzes natural language queries
3. For each query, the model:
   - Analyzes the intent
   - Determines the appropriate action
   - Extracts relevant parameters
   - Provides a confidence score
4. If the confidence score is high enough (> 0.7), the action is executed
5. The reasoning steps are printed for transparency

## Error Handling

The framework includes comprehensive error handling for:
- Authentication issues
- Invalid parameters
- Network errors
- Low confidence actions

## Testing

To run the test suite:
```bash
python test_agent.py
```

The test suite includes:
- Meeting scheduling tests
- Email reading tests
- Calendar event tests
- Email sending tests
- Invalid query handling

## Notes

- The access token is temporary and will expire (usually after 1 hour)
- You'll need to get a new token when it expires
- Keep your token secure and never commit it to version control

## Contributing

Feel free to submit issues and enhancement requests! 