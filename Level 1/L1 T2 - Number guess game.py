import random

def guess_the_number():
    target_number = random.randint(1, 100)
    max_attempts = 7
    attempts = 0

    print("Welcome to the Number Guessing Game!")
    print(f"I'm thinking of a number between 1 and 100.")
    print(f"You have {max_attempts} attempts to guess it.\n")

    while attempts < max_attempts:
        try:
            guess = int(input(f"Attempt {attempts + 1}/{max_attempts} - Enter your guess: "))
        except ValueError:
            print("Invalid input! Please enter a valid integer.\n")
            continue

        attempts += 1

        if guess < target_number:
            print("Too low!\n")
        elif guess > target_number:
            print("Too high!\n")
        else:
            print(f"Congratulations! You guessed the number in {attempts} attempt(s)!")
            return

    print(f"Game over! You've used all {max_attempts} attempts. The number was {target_number}.")

if __name__ == "__main__":
    guess_the_number()