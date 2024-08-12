import re
from datetime import datetime, timedelta

def chatbox():
    print("Welcome back! How was your day at work?")
    input("User: ")

    print("Great to hear! What tasks would you like to accomplish today?")
    tasks_input = input("User: ")

    # Split tasks by both commas and the word "and"
    tasks = re.split(r',\s*|\s+and\s+', tasks_input)

    print("Could you please prioritize these tasks? Which one is the most important?")
    important_task = input("User: ")

    task_time = {}
    for task in tasks:
        print(f"Approximately how much time will {task.strip()} take? (Please enter in hours, e.g., '1.5' for 1 hour and 30 minutes)")
        time = input("User: ")
        task_time[task.strip()] = time

    print("When would you like to start your first task? (Use 'HH:MM' for 24-hour format or 'HH AM/PM' for 12-hour format)")
    start_time = input("User: ")

    # Attempt to parse start time in multiple formats
    try:
        # Try parsing 24-hour format
        start_time_obj = datetime.strptime(start_time, "%H:%M")
    except ValueError:
        try:
            # Try parsing 12-hour format
            start_time_obj = datetime.strptime(start_time, "%I %p")
        except ValueError:
            print("Invalid time format. Please use 'HH:MM' for 24-hour format or 'HH AM/PM' for 12-hour format.")
            return

    planner = []
    for task in tasks:
        # Convert task duration to float to handle decimal hours
        try:
            task_duration = float(task_time[task.strip()])  # Assuming input like '1.5' for 1.5 hours
            end_time_obj = start_time_obj + timedelta(hours=task_duration)
            planner.append(f"{start_time_obj.strftime('%I:%M %p')} - {end_time_obj.strftime('%I:%M %p')}: {task.strip()}")
            start_time_obj = end_time_obj
        except ValueError:
            print(f"Invalid duration format for task '{task.strip()}'. Please enter the duration in hours (e.g., '1.5').")
            return

    print("Here’s your planner for the evening:")
    for item in planner:
        print(item)

chatbox()
