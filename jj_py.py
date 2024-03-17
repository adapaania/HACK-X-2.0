# -*- coding: utf-8 -*-
"""jj.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kiafNeMg-BmlQGhoEUzWIdsjeCmB6oXq
"""

import streamlit as st
import threading
import queue
from datetime import datetime
import openai
from ably import AblyRealtime

# Set up OpenAI API key and model engine
openai.api_key = "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"
model_engine = "gpt-3.5-turbo"

# Define chatbot prompt
chatbot_prompt = """
As an advanced chatbot, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions.
<conversation_history>
User: <user input>
Chatbot:"""

# Function to get chatbot response
def get_chatbot_response(conversation_history, user_input):
    prompt = chatbot_prompt.replace(
        "<conversation_history>", conversation_history).replace("<user input>", user_input)

    # Get the response from GPT-3 using the chat completions endpoint
    response = openai.ChatCompletion.create(
        model=model_engine, messages=[{"role": "system", "content": prompt}], max_tokens=2048, temperature=0.5)

    # Extract the response from the response object
    response_text = response["choices"][0]["message"]["content"]

    return response_text.strip()

# Function to handle incoming messages from Ably
def ably_message_handler(message_queue):
    ably = AblyRealtime('71pnxw.ezOUYA:EqCgjzfPo34Mep85N8t9a8wJwjkwp6JO6p6Uwwv_qMc')
    channel = ably.channels.get('get-started')

    for message in channel.subscribe():
        message_queue.put(message.data)

# Function to generate quiz questions with options
def generate_quiz_questions(video_title):
    # Define video titles, question types, questions, and options
    video_questions = {
        'ChuChu TV Numbers Song - NEW Short Version - Number Rhymes For Children': {
            'number': [
                "What is the first number mentioned in the video?",
                "How many rhymes are included in the song?",
                "What color is the background in the video?"
            ]
        },
        'Phonics Song with TWO Words - A For Apple': {
            'alphabet': [
                "What letter comes after 'B'?",
                "Which letter is your favorite in the alphabet song? Why?",
                "Can you think of words that start with the letter 'A'?"
            ]
        },
        'Wheels on the Bus Go Round and Round': {
            'rhymes': [
                "What characters were in the nursery rhyme?",
                "What lesson did you learn from the nursery rhyme?"
            ]
        },
        'Identify Animals': {
            'animal': [
                "Can you remember the names of all the animals shown in the video?",
                "Which animal made the loudest noise in the video?",
                "Did you learn any new animal names from the video?"
            ]
        }
    }

    # Retrieve questions based on the video title
    video_questions_data = video_questions.get(video_title, {})
    if not video_questions_data:
        print("Chatbot: Unable to generate quiz questions for the video.")
        return []

    # Generate quiz questions with options
    quiz_questions_with_options = []
    for question_type, questions in video_questions_data.items():
        options_mapping = {
            'number': [
                ["One", "Two", "Three", "Four"],
                ["Five", "Six", "Seven", "Eight"],
                ["Red", "Blue", "Green", "Yellow"]
            ],
            'alphabet': [
                ["C", "D", "E", "F"],
                ["B", "C", "D", "E"],
                ["Apple", "Ball", "Cat", "Dog"]
            ],
            'rhymes': [
                ["Humpty Dumpty", "Jack and Jill", "Twinkle Twinkle", "Baa Baa Black Sheep"],
                ["Sharing", "Kindness", "Friendship", "Persistence"]
            ],
            'animal': [
                ["Lion", "Elephant", "Monkey", "Giraffe"],
                ["Elephant", "Lion", "Monkey", "Giraffe"],
                ["Yes", "No", "Maybe", "Not sure"]
            ]
        }
        options = options_mapping.get(question_type, [])
        for i, question in enumerate(questions):
            question_options = options[i] if i < len(options) else []  # Ensure options are available
            quiz_questions_with_options.append((question, question_options))

    return quiz_questions_with_options

# Function for kids' chatbot
def kids_chatbot(input_text):
    conversation_history = ""
    message_queue = queue.Queue()

    # Start a thread to handle incoming messages from Ably
    ably_thread = threading.Thread(target=ably_message_handler, args=(message_queue,))
    ably_thread.start()

    # Get user input
    user_input = input_text

    # Check if there are any messages from Ably
    while not message_queue.empty():
        ably_message = message_queue.get()
        # Process the Ably message (e.g., pass it to the chatbot and print the response)
        chatbot_response = get_chatbot_response(conversation_history, ably_message)
        conversation_history += f"User: {ably_message}\nChatbot: {chatbot_response}\n"

    # Process user input and get chatbot response
    chatbot_response = get_chatbot_response(conversation_history, user_input)
    return chatbot_response

# Function for normal chatbot
def normal_chatbot(input_text):
    conversation_history = ""
    message_queue = queue.Queue()

    # Start a thread to handle incoming messages from Ably
    ably_thread = threading.Thread(target=ably_message_handler, args=(message_queue,))
    ably_thread.start()

    # Get user input
    user_input = input_text

    # Check if there are any messages from Ably
    while not message_queue.empty():
        ably_message = message_queue.get()
        # Process the Ably message (e.g., pass it to the chatbot and print the response)
        chatbot_response = get_chatbot_response(conversation_history, ably_message)
        conversation_history += f"User: {ably_message}\nChatbot: {chatbot_response}\n"

    # Process user input and get chatbot response
    chatbot_response = get_chatbot_response(conversation_history, user_input)
    return chatbot_response

# Streamlit app
def main():
    st.title("Chatbot Website")

    st.write("Welcome! Please select a chatbot.")

    # Sidebar to select chatbot type
    chatbot_type = st.sidebar.radio("Select Chatbot:", ("Normal", "Kids"))

    # Text input for user messages
    user_input = st.text_input("You:", "")

    # Display chatbot response based on selected type