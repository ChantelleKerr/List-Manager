import sys
import sqlite3


class ListManager(object):
    def __init__(self):
        self.connection = sqlite3.connect("Movies.db")
        self.cursor = self.connection.cursor()
        self.empty_list = True
        self.saved = True
        self.items = []
        self.file_changes = 0
        self.current_user = None

    def create_user_table(self):
        try:
            sql_command = "CREATE TABLE IF NOT EXISTS Users (ID INTEGER NOT NULL PRIMARY KEY, Name VARCHAR(64));"
            self.cursor.execute(sql_command)
        except:
            print("Error Creating User Table")

    def create_movie_table(self):
        """ Creates a new table """
        try:
            sql_command = "CREATE TABLE IF NOT EXISTS Movies (Name VARCHAR(64), User_ID INTEGER);"
            self.cursor.execute(sql_command)
        except:
            print("Error Creating Movies Table")

    def check_user_table(self):
        """ Checks if the table contains rows """
        count = 0
        users = []
        sql_command = "SELECT * FROM Users;"
        self.cursor.execute(sql_command)
        data = self.cursor.fetchall()
        if not data:
            # No data - Create new user
            self.create_user()
        else:
            for user in data:
                print(user[0], ": ", user[1])
                users.append(user[0])
                count += 1
            # There is data - Select User
            value = int(input("Select a user or (0 to create another user): "))
            if value == 0:
                self.create_user()
            elif value <= count:
                self.current_user = users[value - 1]
                self.check_movie_table()

    def create_user(self):
        try:
            print("CREATING NEW USER")
            name = input("Enter your name: ")
            self.cursor.execute("INSERT INTO Users (Name) VALUES (?)", (name,))
            self.connection.commit()
            self.check_user_table()
        except Exception as e:
            print("ERROR CREATING USER", e)

    def check_movie_table(self):
        """ Checks if the table contains rows """
        sql_command = "SELECT * FROM Movies where User_ID = " + str(self.current_user)
        self.cursor.execute(sql_command)
        data = self.cursor.fetchall()
        if not data:
            # No data
            self.display_options()
        else:
            # Has data
            for movie in data:
                self.items.append(str(movie[0]))
            self.display_items()

    def display_items(self):
        """ Sorts the items in the list and displays them """
        self.empty_list = False
        count = 1
        # Sort the items by alphabetical order
        self.items.sort()
        # Display Items from the List
        for item in self.items:
            print(str(count) + ": " + item.strip("\n"))
            count += 1
        self.display_options()

    def display_options(self):
        """ Displays the available options and calls the prompt_user method """
        # If the file is empty
        if self.empty_list:
            print("[A]dd [Q]uit")
        elif self.saved:
            print("[A]dd [D]elete [Q]uit")
        else:
            print("[A]dd [D]elete [S]ave [Q]uit")
        self.prompt_user()

    def prompt_user(self):
        """ Handles user input """
        value = input("> ").lower()
        if value == "a":
            self.add_item()
        elif value == "d":
            self.delete_item()
        elif value == "s":
            self.save_file()
        elif value == "q":
            self.quit()
        else:
            print("ERROR: invalid choice -- enter one of 'AaDdSsQq'")
            self.display_options()
        self.display_items()

    def add_item(self):
        """ Adds new movie to list (Does not directly update the database) """
        item = input("Add Movie: ")
        self.items.append(item)
        self.empty_list = False
        self.saved = False
        self.file_changes += 1

    def delete_item(self):
        """ Deletes item from the list (Does not directly update the database) """
        item = int(input("Delete Item by index (or 0 to cancel) : "))
        if item == 0:
            pass
        else:
            del self.items[item-1]
            self.saved = False
            self.file_changes += 1

    def save_file(self):
        """ Saves the list to the database """
        try:
            self.cursor.execute("DELETE FROM Movies where User_ID = " + str(self.current_user))    # Delete rows in db so we can re-insert them
            for movie in self.items:
                self.cursor.execute("INSERT INTO Movies (Name, User_ID) VALUES (?,?);", (movie, self.current_user))
                self.connection.commit()
        except Exception as e:
            print("ERROR SAVING TO DB", e)

        self.saved = True
        print(f"{self.file_changes} changes made to the database")
        self.file_changes = 0   # Set the value back to 0
        input("Press Enter to continue..")

    def quit(self):
        """
        Prompts the user if changes to the list were made,
        which allows user to save the file before exiting the program
        """
        if not self.saved:
            value = input("Save unsaved changes (Y/N)").lower()
            if value == "y":
                self.save_file()
                sys.exit(0)
            elif value == 'n':
                sys.exit(0)
            else:
                print("Error: Invalid response")
                self.quit()
        else:
            # No changes were made
            sys.exit(0)

    def main(self):
        self.create_user_table()
        self.create_movie_table()
        self.check_user_table()


if __name__ == "__main__":
    list_manager = ListManager()
    list_manager.main()
