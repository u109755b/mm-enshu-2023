def get_current_progress(min_value, max_value):
    while True:
        try:
            user_input = int(
                input(f"Enter a page number between {min_value} and {max_value}: ")
            )
            if min_value <= user_input <= max_value:
                print(f"Your current progress is {user_input}/{max_value} pages.")
                return user_input
            else:
                print(
                    f"##Invalid Input##\nPlease enter a number within the range {min_value}-{max_value}."
                )
        except ValueError:
            print("Invalid input. Please enter an integer.")
