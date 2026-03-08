from collections import UserDict
from datetime import datetime, timedelta, date
from typing import Callable
from functools import wraps
import pickle

DATE_FORMAT = "%d.%m.%Y"

def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, DATE_FORMAT).date()

class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be a 10-digit string.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            super().__init__(parse_date(value))
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
    def __str__(self):
        return self.value.strftime(DATE_FORMAT)

class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        if self.find_phone(phone) is None:
            self.phones.append(Phone(phone))
        else:
            raise ValueError(f"Phone {phone} already exists for this contact.")

    def edit_phone(self, old_phone: str, new_phone: str):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                break
        else:
            raise KeyError(f"Phone {old_phone} not found.")

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)
    
    def remove_phone(self, phone: str):
        self.phones = [p for p in self.phones if p.value != phone]

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday if self.birthday else 'N/A'}"
    
    def __getstate__(self):
        attributes = self.__dict__.copy()
        attributes['phones'] = [phone.value for phone in attributes['phones']]
        if attributes['birthday'] is not None:
            attributes['birthday'] = attributes['birthday'].value.strftime(DATE_FORMAT)
        return attributes
    
    def __setstate__(self, state):
        if 'phones' in state:
            state['phones'] = [Phone(phone) for phone in state['phones']]
        if 'birthday' in state and state['birthday'] is not None:
            state['birthday'] = Birthday(state['birthday'])
        self.__dict__.update(state)

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]

    def __str__(self):
        return f'Address book:\n{"\n".join(str(record) for record in self.data.values())}'

    def get_upcoming_birthdays(self) -> list[dict]:
        '''
        Returns a sorted list of users who have birthdays in the next 7 days,
        adjusting for weekends by moving celebrations to the following Monday.
        '''

        today = datetime.today().date()
        upcoming_congratulation_dates = []
        all_birthdays = filter(lambda t: t[1].birthday is not None, self.data.items())
        for name, birthday in map(lambda t: (t[0], t[1].birthday.value), all_birthdays):
            birthday_this_year = birthday.replace(year=today.year)
            days_until_birthday = (birthday_this_year - today).days
            if days_until_birthday < 0:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                days_until_birthday = (birthday_this_year - today).days

            if 0 <= days_until_birthday <= 7:
                if birthday_this_year.weekday() in [5, 6]:  # Saturday or Sunday
                    birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
                
                upcoming_congratulation_dates.append({
                    "name": name,
                    "congratulation_date": birthday_this_year.strftime(DATE_FORMAT)
                })

        return sorted(
            upcoming_congratulation_dates,
            key=lambda x: parse_date(x['congratulation_date'])
        )

def input_error(func: Callable) -> Callable:
    """Decorator to handle input errors for contact management functions."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except (KeyError, IndexError):
            return 'Invalid command.'
    
    return wrapper

def parse_input(input: str) -> tuple[str, ...]:
    """Parse the input from the user."""

    command, *args = input.strip().split(" ")
    command = command.lower()
    return command, *args

@input_error
def add_contact(args: list[str], book: AddressBook) -> str:
    """Adds a new contact to the contacts dictionary."""

    if len(args) != 2:
        raise ValueError("Usage: add <name> <phone>")
    name = args[0]
    phone = args[1]
    existing_record = book.find(name) # check if contact already exists
    if existing_record is not None:
        existing_record.add_phone(phone)
        return 'Contact updated.'
    
    new_record = Record(name)
    new_record.add_phone(phone)
    book.add_record(new_record)
    return 'Contact added.'

@input_error
def change_contact(args: list[str], book: AddressBook) -> str:
    """Changes the phone number of an existing contact."""

    if len(args) != 3:
        raise ValueError("Usage: change <name> <old_phone> <new_phone>")
    name = args[0]
    old_phone = args[1]
    new_phone = args[2]
    record = book.find(name)
    if record is None:
        raise ValueError(f"Contact '{name}' does not exist.")
    record.edit_phone(old_phone, new_phone)
    return 'Contact updated.'

@input_error
def show_phone(args: list[str], book: AddressBook) -> str:
    """Shows the phone number of a contact."""

    if len(args) != 1:
        raise ValueError("Usage: phone <name>")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ValueError(f"Contact '{name}' does not exist.")
    return ", ".join(phone.value for phone in record.phones)

@input_error
def show_all_contacts(book: AddressBook) -> str:
    """Shows all contacts in the address book."""

    if book:
        return str(book)
    else:
        return "No contacts found."

@input_error
def add_birthday(args: list[str], book: AddressBook) -> str:
    """Adds a birthday to an existing contact."""

    if len(args) != 2:
        raise ValueError("Usage: add-birthday <name> <birthday>")
    name = args[0]
    birthday = args[1]
    record = book.find(name)
    if record is None:
        raise ValueError(f"Contact '{name}' does not exist.")
    record.add_birthday(birthday)
    return 'Birthday added.'

@input_error
def show_birthday(args: list[str], book: AddressBook) -> str:
    """Shows the birthday of a contact."""

    if len(args) != 1:
        raise ValueError("Usage: show-birthday <name>")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ValueError(f"Contact '{name}' does not exist.")
    return str(record.birthday)

@input_error
def birthdays(args: list[str], book: AddressBook) -> str:
    """Shows upcoming birthdays in the next 7 days."""

    if len(args) != 0:
        raise ValueError("Usage: birthdays")
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next 7 days."
    return "Upcoming birthdays in the next 7 days:\n" + \
        "\n".join(f"{entry['name']} - {entry['congratulation_date']}" for entry in upcoming_birthdays)

def save_data(book: AddressBook, filename="addressbook.pkl") -> None:
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl") -> AddressBook:
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main() -> None:
    """Console bot for managing contacts."""

    book = load_data()

    try:
        while True:
            user_input = input("Enter a command: ")

            if not user_input.strip():
                print("Please enter a command.")
                continue

            command, *args = parse_input(user_input)

            match command:
                case "hello":
                    print("How can I help you?")
                case "add":
                    msg = add_contact(args, book)
                    print(msg)
                case "change": 
                    msg = change_contact(args, book)
                    print(msg)
                case "phone":
                    msg = show_phone(args, book) # phone
                    print(msg)
                case "all":
                    msg = show_all_contacts(book)
                    print(msg)
                case "add-birthday":
                    msg = add_birthday(args, book)
                    print(msg)
                case "show-birthday":
                    msg = show_birthday(args, book)
                    print(msg)
                case "birthdays":
                    msg = birthdays(args, book)
                    print(msg)
                case "exit" | "close":
                    print("Good bye!")
                    save_data(book)
                    break
                case _:
                    print("Invalid command.")

    except KeyboardInterrupt:
        print("\nGood bye!")
        save_data(book)
    except Exception as e:
        print(f"An error occurred: {e}")
        save_data(book)

if __name__ == '__main__':
    main()
