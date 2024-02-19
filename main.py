import speech_recognition as sr
import pyttsx3
import requests
import sqlite3
import datetime
from dotenv import load_dotenv
import os

load_dotenv(".env")



conn = sqlite3.connect("to-dos.db")


# Initialize the speech recognition engine
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()


#all keys and variables 
api_key = "AIzaSyDe-3FlNWpBPKVgaGGZop1ESAoYXgQdGAE"
weather_api = 'c96978793dc7a15fc0669ebde348422b'
cx = '16040a07ddc5b4cb2'
city = 'hong kong'




def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        speak(f"You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        speak("Sorry, I could not understand you.")
    except sr.RequestError as e:
        speak(f"Sorry, an error occurred: {e}")

    return ""


def speak(text):
    engine.say(text)
    engine.runAndWait()


def create_reminder_base(conn):
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Reminders (
            id INTEGER PRIMARY KEY,
            text TEXT,
            Time INTEGER
        )
        """
    )

    conn.commit()


def create_to_do_table(conn):
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY,
            text TEXT,
            completed INTEGER
        )
        """
    )

    conn.commit


def retrieve_remind():
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Reminders")
    todos = cursor.fetchall()

    conn.commit
    return todos


#functions 
create_reminder_base(conn)
create_to_do_table(conn)



def store_todos(conn, todos_text):
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO todos (text, completed)
        VALUES (?, ?)
        """,
        (todos_text, 0),  # Assuming the initial completion status is 0 (not completed)
    )

    conn.commit()


def retrieve_todos():
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()

    conn.commit
    return todos



def update_todo_status(conn, todo_id, completed):
    cursor = conn.cursor()

    # Update the completed status of the specified to-do item
    cursor.execute("UPDATE todos SET completed = ? WHERE id = ? ",
                   (completed, todo_id))

    conn.commit()


def delete_todo(conn):
    cursor = conn.cursor()

    cursor.execute("DELETE FROM todos")

    conn.commit()


def set_reminder():
    # Get the current date and time
    current_datetime = datetime.datetime.now()

    cursor = conn.cursor()

    # Set the reminder time (e.g., 10 minutes from the current time)
    reminder_time = current_datetime + datetime.timedelta(minutes=10)

    # Format the reminder time
    formatted_time = reminder_time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO Reminders (text, time)
        VALUES (?, ?)
        """,
        (reminder_time), 
    )

    conn.commit()

    # Return the formatted reminder time
    return formatted_time


def store_reminder(conn, reminder_text):
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO Reminders (text, Time)
        VALUES (?, ?, ?)
        """,
        (reminder_text, 0),  # Assuming the initial completion status is 0 (not completed)
    )

    conn.commit()


def perform_task(command, api_key, cx, weather_api, city):
    if "set a reminder" in command:
        speak("Sure, what would you like me to remind you?")
        with sr.Microphone() as source:
         print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        reminder_text = recognizer.recognize_google(audio)

        reminder_time = set_reminder(conn, reminder_text)
        speak(f"Reminder set for {reminder_time}.")
        speak("Reminder set successfully.")

    elif "show reminder" in command:
        remind = retrieve_remind()
        if remind:
            speak("Here are your Reminders:")
            for remind in remind:
                reminder_id, reminder_text, completed = remind
                print(f"ID: {reminder_id}")
                print(f"Text: {reminder_text}")
                print(f"Time: {reminder_time}")
                print("---")
        else:
            speak("You don't have any Reminders.")

    # Creating a TO DO list
    elif "create command" in command: 
        speak("Sure, what would you like to add?")
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        todo_text = recognizer.recognize_google(audio)
        store_todos(conn, todo_text)
        speak("To-do created successfully.")

    # Showing the database
    elif "show base" in command:
        todos = retrieve_todos()
        if todos:
            speak("Here are your to-do items:")
            for todo in todos:
                todo_id, todo_text, completed = todo
                print(f"ID: {todo_id}")
                print(f"Text: {todo_text}")
                print(f"Completed: {'Yes' if completed else 'No'}")
                print("---")
        else:
            speak("You don't have any to-do items.")

    # Updating the Status of the todo list
    elif "update status" in command:
        speak("Please provide the ID of the to-do item you want to update.")
        todo_id = input("To-do ID: ")  # Get the ID from user input
        speak("Please specify the completed status of the to-do item.")
        # Get the completed status from user input
        completed = input("Completed (0 for not completed, 1 for completed): ")
        update_todo_status(conn, todo_id, completed)
        speak("To-do item status updated successfully.")

    # Deleting all Commands in the TO-do
    elif "delete all" in command:
        # Code to delete all items
        delete_todo(conn)
        speak("All to-do items have been deleted.")

    # Searching the web for information
    elif "search" in command:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": api_key, "cx": cx, "q": command}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract and process search results
            if "items" in data:
                for item in data["items"]:
                    title = item["title"]
                    link = item["link"]
                    print(f"Title: {title}")
                    print(f"Link: {link}")
                    print("---")

        except requests.exceptions.HTTPError as e:
            print(f"An error occurred: {e}")
            speak("Searching the web...")

    # Weather information
    elif "the weather" in command:
        # Code to get weather information
        speak("Fetching weather information...")
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
        "q": city,
        "appid": weather_api,
        "units": "metric"
        }

        city_name = input("Enter a city name")

        try:
            response.get(base_url, params=params)
            response_data = response.json()

            location = response_data["name"]
            temperature = response_data["main"]["temp"]
            condition = response_data["weather"][0]["description"]

            speak(f"weather in {location}:")
            speak(f"Temperature is {temperature}")
            speak(f"condition is {condition}")
        except requests.exceptions.RequestException as e:
            print("An error has occured while making the API requests:", str(e))

        
        

    # playing some music
    elif "play music" in command:
        # Code to play music
        speak("Playing music...")
        # Add your code here to play music using a suitable library or player

    # Getting u pdates
    elif "get news updates" in command:
        # Code to get news updates
        speak("Fetching news updates...")
        # Add your code here to fetch and read news headlines


# Main loop
while True:
    command = listen()
    if "stop" in command:
        speak("Stopping Algorithim")
        break
    perform_task(command, api_key=api_key, cx=cx, weather_api=weather_api, city=city)
