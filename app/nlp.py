from typing import List, Dict, Any
import random
import datetime

# Intent definitions with keywords
INTENT_DEFINITIONS = {
    "Weather": ["weather", "rain", "sunny", "forecast", "temperature", "climate", "cold", "hot"],
    "Greeting": ["hello", "hi", "greetings", "hey", "howdy", "good morning", "good afternoon", "good evening"],
    "Time": ["time", "clock", "hour", "minute", "what time", "current time"],
    "Date": ["date", "day", "month", "year", "today", "tomorrow", "yesterday", "calendar"],
    "Music": ["music", "song", "play", "listen", "spotify", "track", "artist", "album"],
    "News": ["news", "headlines", "current events", "breaking", "report"],
    "Joke": ["joke", "funny", "humor", "laugh", "tell me a joke"],
    "Reminder": ["remind", "reminder", "remember", "don't forget", "schedule"],
    "Search": ["search", "find", "look up", "google", "information about"],
    "Help": ["help", "assist", "support", "guide", "how to", "what can you do"]
}

# Response templates for each intent
RESPONSE_TEMPLATES = {
    "Weather": [
        "The weather today is {weather_condition} with a temperature of {temperature}°C.",
        "Currently it's {weather_condition} outside, with temperatures around {temperature}°C.",
        "Today's forecast shows {weather_condition} weather with {temperature}°C."
    ],
    "Greeting": [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "Greetings! How may I assist you?"
    ],
    "Time": [
        "The current time is {time}.",
        "It's {time} right now.",
        "The time is {time}."
    ],
    "Date": [
        "Today is {date}.",
        "It's {date} today.",
        "The date today is {date}."
    ],
    "Music": [
        "I'd play '{song}' for you if I could!",
        "Would you like to hear '{song}'?",
        "I can recommend '{song}' based on your request."
    ],
    "News": [
        "Here's the latest headline: {headline}",
        "Today's top story: {headline}",
        "Breaking news: {headline}"
    ],
    "Joke": [
        "Here's a joke: {joke}",
        "Let me make you laugh: {joke}",
        "How about this one? {joke}"
    ],
    "Reminder": [
        "I'll remind you to {task} at {reminder_time}.",
        "Reminder set for {task} at {reminder_time}.",
        "I'll make sure to remind you about {task} at {reminder_time}."
    ],
    "Search": [
        "Here's what I found about {query}: {result}",
        "I searched for {query} and found: {result}",
        "The top result for {query} is: {result}"
    ],
    "Help": [
        "I can help with weather, time, date, music, news, jokes, reminders, and searches. What would you like to know?",
        "I'm your virtual assistant. I can tell you the weather, time, date, play music, get news, tell jokes, set reminders, or search for information.",
        "Need help? I can assist with various tasks like checking weather, time, setting reminders, and more."
    ],
    "Unknown": [
        "I'm not sure I understand. Could you rephrase that?",
        "I didn't catch that. Can you say it differently?",
        "I'm still learning and don't understand that request yet."
    ]
}

# Sample data for responses
SAMPLE_DATA = {
    "weather_conditions": ["sunny", "cloudy", "rainy", "snowy", "windy", "foggy", "partly cloudy"],
    "temperatures": list(range(0, 35)),
    "songs": ["Shape of You by Ed Sheeran", "Blinding Lights by The Weeknd", "Dance Monkey by Tones and I", 
              "Someone You Loved by Lewis Capaldi", "Bad Guy by Billie Eilish"],
    "headlines": ["Scientists Discover New Species in Amazon Rainforest", 
                 "Tech Company Launches Revolutionary AI Assistant",
                 "Global Leaders Meet to Discuss Climate Change",
                 "New Study Shows Benefits of Mediterranean Diet",
                 "Space Mission Successfully Lands on Mars"],
    "jokes": ["Why don't scientists trust atoms? Because they make up everything!",
             "What did the ocean say to the beach? Nothing, it just waved.",
             "Why did the scarecrow win an award? Because he was outstanding in his field!",
             "How does a penguin build its house? Igloos it together!",
             "Why don't eggs tell jokes? They'd crack each other up!"],
    "search_results": ["According to Wikipedia, this is a fascinating topic with many aspects to explore.",
                      "The most reliable sources suggest that this is still an evolving field of study.",
                      "Recent research has shown promising developments in this area.",
                      "Experts generally agree that this requires further investigation.",
                      "There are multiple perspectives on this topic, each with supporting evidence."]
}

def recognize_intent(text: str) -> str:
    """
    Recognize the intent from user input text
    """
    text_lower = text.lower()
    
    # Check each intent's keywords
    for intent, keywords in INTENT_DEFINITIONS.items():
        if any(keyword in text_lower for keyword in keywords):
            return intent
    
    return "Unknown"

def generate_response(intent: str, text: str) -> Dict[str, Any]:
    """
    Generate a response based on the recognized intent
    """
    # Select a random response template for the intent
    templates = RESPONSE_TEMPLATES.get(intent, RESPONSE_TEMPLATES["Unknown"])
    template = random.choice(templates)
    
    # Fill in the template with appropriate data
    response_data = {}
    
    if intent == "Weather":
        response_data = {
            "weather_condition": random.choice(SAMPLE_DATA["weather_conditions"]),
            "temperature": random.choice(SAMPLE_DATA["temperatures"])
        }
    elif intent == "Time":
        current_time = datetime.datetime.now().strftime("%H:%M")
        response_data = {"time": current_time}
    elif intent == "Date":
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        response_data = {"date": current_date}
    elif intent == "Music":
        response_data = {"song": random.choice(SAMPLE_DATA["songs"])}
    elif intent == "News":
        response_data = {"headline": random.choice(SAMPLE_DATA["headlines"])}
    elif intent == "Joke":
        response_data = {"joke": random.choice(SAMPLE_DATA["jokes"])}
    elif intent == "Reminder":
        # For demonstration, set a reminder for 1 hour from now
        reminder_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M")
        response_data = {
            "task": "your task",  # This could be extracted from the user input
            "reminder_time": reminder_time
        }
    elif intent == "Search":
        # Extract a query from the text or use a default
        query = text.replace("search", "").replace("find", "").replace("look up", "").strip()
        if not query:
            query = "your search query"
        response_data = {
            "query": query,
            "result": random.choice(SAMPLE_DATA["search_results"])
        }
    
    # Format the response text using the template and data
    try:
        response_text = template.format(**response_data)
    except KeyError:
        # Fallback if template formatting fails
        response_text = random.choice(RESPONSE_TEMPLATES["Unknown"])
    
    # Return a structured response
    return {
        "intent": intent,
        "text": response_text,
        "data": response_data
    }