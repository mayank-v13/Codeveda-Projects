# Functions for basic arithmetic operations
def add(x, y):
    return x + y


def subtract(x, y):
    return x - y


def multiply(x, y):
    return x * y


def divide(x, y):
    if y == 0:
        return "Error: Division by zero is not allowed."
    return x / y


def calculator():
    print("Select operation:")
    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")

    while True:
        # Take choice input from the user
        choice = input("\nEnter choice (1/2/3/4) or 'q' to quit: ").strip()

        if choice.lower() == "q":
            print("Exiting calculator. Goodbye!")
            break

        if choice in ("1", "2", "3", "4"):
            try:
                # Take two numeric inputs from the user
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))
            except ValueError:
                print("Invalid input! Please enter valid numeric values.")
                continue

            # Perform the chosen operation
            if choice == "1":
                print(f"Result: {num1} + {num2} = {add(num1, num2)}")

            elif choice == "2":
                print(f"Result: {num1} - {num2} = {subtract(num1, num2)}")

            elif choice == "3":
                print(f"Result: {num1} * {num2} = {multiply(num1, num2)}")

            elif choice == "4":
                result = divide(num1, num2)
                if isinstance(result, str):
                    print(result)  # Prints the error message
                else:
                    print(f"Result: {num1} / {num2} = {result}")

        else:
            print("Invalid choice! Please select a valid operation (1-4).")


# Run the calculator
if __name__ == "__main__":
    calculator()