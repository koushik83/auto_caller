# AI Phone Assistant

An AI-powered phone assistant that can make calls and have natural conversations using Twilio and OpenAI.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-phone-assistant.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.template` to `.env`
   - Fill in your credentials in `.env`

4. Run the application:
```bash
python app.py
```

## Environment Variables

The following environment variables are required:

- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
- `TWILIO_PHONE_NUMBER`: Your Twilio Phone Number
- `VERIFIED_PHONE_NUMBER`: Your Verified Phone Number
- `OPENAI_API_KEY`: Your OpenAI API Key

## Security Notes

- Never commit the `.env` file
- Keep your API keys secure
- Use environment variables for all sensitive data

## Features

- Natural conversation flow
- Speech recognition
- AI-powered responses
- Conversation state tracking
- Detailed logging