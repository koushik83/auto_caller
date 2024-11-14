from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
VERIFIED_PHONE_NUMBER = os.getenv('VERIFIED_PHONE_NUMBER')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Verify all required environment variables are present
required_env_vars = [
    'TWILIO_ACCOUNT_SID',
    'TWILIO_AUTH_TOKEN',
    'TWILIO_PHONE_NUMBER',
    'VERIFIED_PHONE_NUMBER',
    'OPENAI_API_KEY'
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation state
conversation_state = {
    'has_agreed': False,
    'has_time': False,
    'has_address': False,
    'discussed_items': False,
    'confirmed_details': False,
    'history': [],
    'turn_count': 0
}

def log_conversation(prompt, response, user_input=None):
    """Log detailed conversation information"""
    print("\n" + "="*70)
    print(f"CONVERSATION TURN {conversation_state['turn_count']}")
    print("="*70)
    print(f"\nTIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if user_input:
        print(f"\n👤 USER SAID: {user_input}")
        
    print(f"\n🤖 PROMPT TO GPT:\n{prompt}")
    print(f"\n🤖 GPT RESPONDS: {response}")
    
    print("\n📊 CONVERSATION STATE:")
    for key, value in conversation_state.items():
        if key != 'history':
            print(f"  {key}: {value}")
    
    print("\n🗣️ CONVERSATION HISTORY:")
    for entry in conversation_state['history'][-3:]:  # Show last 3 turns
        role = "👤" if entry['role'] == 'user' else "🤖"
        print(f"  {role} {entry['role']}: {entry['content']}")
    
    print("="*70)

@app.route("/", methods=['GET', 'POST'])
def index():
    # Reset state for new call
    for key in conversation_state:
        conversation_state[key] = False if isinstance(conversation_state[key], bool) else []
    conversation_state['turn_count'] = 0
    
    print("\n" + "="*50)
    print("NEW CONVERSATION STARTED")
    print("="*50)
    
    response = VoiceResponse()
    gather = Gather(
        input='speech',
        action='/handle-speech',
        timeout=3,
        language='en-US'
    )
    
    initial_message = "Hi! I need help moving some furniture today. It's just a couch and couple of chairs. Could you help?"
    conversation_state['history'].append({"role": "assistant", "content": initial_message})
    print(f"\nAI SPEAKS: {initial_message}")
    
    gather.say(initial_message, voice='alice')
    response.append(gather)
    
    return str(response)

@app.route("/handle-speech", methods=['GET', 'POST'])
def handle_speech():
    speech_result = request.values.get('SpeechResult', '')
    confidence = request.values.get('Confidence', 'N/A')
    
    conversation_state['turn_count'] += 1
    conversation_state['history'].append({"role": "user", "content": speech_result})
    
    # Update state based on user input
    if any(word in speech_result.lower() for word in ['yes', 'sure', 'okay', 'fine', 'can']):
        conversation_state['has_agreed'] = True
    if any(word in speech_result.lower() for word in ['morning', 'afternoon', 'evening', 'pm', 'am', 'oclock', "o'clock"]):
        conversation_state['has_time'] = True
    if any(word in speech_result.lower() for word in ['street', 'avenue', 'road', 'drive', 'lane']):
        conversation_state['has_address'] = True
    
    response = VoiceResponse()
    
    try:
        system_prompt = f"""You are making a friendly call to ask for help moving furniture.
        Current conversation state:
        - Turn: {conversation_state['turn_count']}
        - Agreement: {conversation_state['has_agreed']}
        - Time set: {conversation_state['has_time']}
        - Address known: {conversation_state['has_address']}

        CONVERSATION STAGE BASED ON TURN {conversation_state['turn_count']}:
        Turns 1-2: Get agreement and check availability
        Turns 3-4: Get specific time
        Turns 5-6: Confirm furniture details (couch and two chairs) and get address
        Turns 7+: Wrap up and confirm all details

        RULES:
        1. Keep responses under 15 words
        2. Be conversational and natural
        3. Don't repeat questions already answered
        4. Show appreciation
        5. If they agree but no time, ask about timing
        6. If they give time, confirm and ask about address
        7. After turn 6, start wrapping up

        Last user response: {speech_result}"""

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + conversation_state['history']
        )
        
        ai_response = chat_completion.choices[0].message.content
        log_conversation(system_prompt, ai_response, speech_result)
        
        conversation_state['history'].append({"role": "assistant", "content": ai_response})
        
        gather = Gather(
            input='speech',
            action='/handle-speech',
            timeout=3,
            language='en-US'
        )
        
        # Add natural pause for longer conversations
        if conversation_state['turn_count'] > 1:
            response.pause(length=1)
        
        gather.say(ai_response, voice='alice')
        response.append(gather)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        gather = Gather(
            input='speech',
            action='/handle-speech',
            timeout=3,
            language='en-US'
        )
        gather.say("I'm sorry, could you repeat that? When would be a good time?", voice='alice')
        response.append(gather)
    
    return str(response)

if __name__ == "__main__":
    print("\n=== AI CONVERSATION SYSTEM STARTING ===")
    print("Ready for natural, extended conversations...")
    app.run(debug=True, port=5000)