Python Programming: Foundations and Best Practices 2.0

# Homework Assignment #8

A command-line address book application for managing contacts with phone numbers and birthdays. Built with Python, featuring data persistence using pickle serialization.

## Features

- **Contact Management**
  - Add new contacts with phone numbers
  - Store multiple phone numbers per contact
  - Edit existing phone numbers
  - Delete contacts
  - View all contacts

- **Birthday Tracking**
  - Add birthday information to contacts (format: DD.MM.YYYY)
  - Display upcoming birthdays within the next 7 days
  - Automatically adjust birthday celebrations if they fall on weekends (moved to following Monday)

- **Data Persistence**
  - Automatically saves contacts to `addressbook.pkl` file
  - Loads existing contacts on startup
  - Data survives application restarts

- **Input Validation**
  - Phone numbers must be exactly 10 digits
  - Birthday dates use DD.MM.YYYY format
  - Error handling with helpful user messages

## Commands

| Command | Syntax | Description |
|---------|--------|-------------|
| `hello` | `hello` | Display greeting message |
| `add` | `add <name> <phone>` | Add a new contact or phone to existing contact |
| `change` | `change <name> <old_phone> <new_phone>` | Update a phone number |
| `phone` | `phone <name>` | Display all phones for a contact |
| `all` | `all` | Display all contacts |
| `add-birthday` | `add-birthday <name> <birthday>` | Add birthday to a contact (DD.MM.YYYY) |
| `show-birthday` | `show-birthday <name>` | Display birthday of a contact |
| `birthdays` | `birthdays` | Show upcoming birthdays in next 7 days |
| `exit` / `close` | `exit` or `close` | Exit the application |

## Usage Examples

```bash
# Start the application
python task_serialization.py

# Add a contact
Enter a command: add John 1234567890
Contact added.

# Add multiple phones to a contact
Enter a command: add John 9876543210
Contact updated.

# Add a birthday
Enter a command: add-birthday John 15.03.1990
Birthday added.

# View upcoming birthdays
Enter a command: birthdays
Upcoming birthdays in the next 7 days:
John - 15.03.2026

# View all contacts
Enter a command: all
Address book:
Contact name: John, phones: 1234567890; 9876543210, birthday: 15.03.1990
```

## Project Structure

- `task_serialization.py` - Main application file containing:
  - `Field` classes: Base class for contact fields (Name, Phone, Birthday)
  - `Record` class: Individual contact representation
  - `AddressBook` class: Container for all contacts (extends UserDict)
  - Command handlers and CLI interface

## Technical Details

- **Language**: Python 3.x
- **Dependencies**: Standard library only (collections, datetime, functools, pickle)
- **Data Format**: Pickle binary serialization
- **Data File**: `addressbook.pkl`

### Key Classes

- **Field**: Base class for storing contact field values
- **Name**: Contact name field
- **Phone**: Phone number field with 10-digit validation
- **Birthday**: Birthday field with date parsing and formatting
- **Record**: Represents a single contact with methods for phone/birthday management
- **AddressBook**: Collection of contacts with search and birthday calculation features

### Special Features

- `__getstate__` and `__setstate__` methods for proper pickle serialization of complex objects
- Decorator-based error handling for command functions
- Automatic birthday adjustment for weekend celebrations

## Error Handling

The application handles various errors gracefully:
- Invalid phone number format (must be 10 digits)
- Invalid date format (must be DD.MM.YYYY)
- Missing or non-existent contacts
- Duplicate phone numbers
- Invalid commands

## Data Persistence

Contacts are automatically saved to `addressbook.pkl` when:
- The user exits with `exit` or `close` command
- The application is interrupted (Ctrl+C)
- An unexpected error occurs

## Notes

- Phone numbers must be exactly 10 digits
- Dates must be in DD.MM.YYYY format
- Birthday celebration dates are adjusted to the next Monday if they fall on Saturday or Sunday
- Multiple phone numbers can be stored per contact
- The address book persists between sessions via pickle serialization
