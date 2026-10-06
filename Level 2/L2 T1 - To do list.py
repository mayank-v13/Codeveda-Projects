import json
import os

FILENAME = "todo_list.json"

def load_tasks():
    """Load tasks from the JSON file."""
    if not os.path.exists(FILENAME):
        return []
    try:
        with open(FILENAME, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        print("\n[Warning] Error loading file. Starting with an empty task list.")
        return []

def save_tasks(tasks):
    """Save tasks to the JSON file."""
    try:
        with open(FILENAME, "w") as file:
            json.dump(tasks, file, indent=4)
    except IOError:
        print("\n[Error] Failed to save tasks to file.")

def display_tasks(tasks):
    """List all tasks with their status."""
    if not tasks:
        print("\nYour to-do list is empty!")
        return

    print("\n--- YOUR TO-DO LIST ---")
    for index, task in enumerate(tasks, start=1):
        status = "[X]" if task["completed"] else "[ ]"
        print(f"{index}. {status} {task['title']}")
    print("-----------------------")

def add_task(tasks):
    """Add a new task."""
    title = input("\nEnter task description: ").strip()
    if not title:
        print("[Error] Task description cannot be empty.")
        return
    
    tasks.append({"title": title, "completed": False})
    save_tasks(tasks)
    print(f"[Success] Added: '{title}'")

def mark_completed(tasks):
    """Mark a task as completed."""
    display_tasks(tasks)
    if not tasks:
        return

    try:
        task_num = int(input("\nEnter task number to mark as done: "))
        if 1 <= task_num <= len(tasks):
            tasks[task_num - 1]["completed"] = True
            save_tasks(tasks)
            print(f"[Success] Task {task_num} marked as completed!")
        else:
            print(f"[Error] Task number must be between 1 and {len(tasks)}.")
    except ValueError:
        print("[Error] Please enter a valid number.")

def delete_task(tasks):
    """Delete a task."""
    display_tasks(tasks)
    if not tasks:
        return

    try:
        task_num = int(input("\nEnter task number to delete: "))
        if 1 <= task_num <= len(tasks):
            removed = tasks.pop(task_num - 1)
            save_tasks(tasks)
            print(f"[Success] Deleted: '{removed['title']}'")
        else:
            print(f"[Error] Task number does not exist.")
    except ValueError:
        print("[Error] Please enter a valid number.")

def main():
    tasks = load_tasks()

    while True:
        print("\n=== TO-DO LIST MENU ===")
        print("1. View Tasks")
        print("2. Add Task")
        print("3. Mark Task as Done")
        print("4. Delete Task")
        print("5. Exit")
        
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            display_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            mark_completed(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("[Error] Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()