"""
models/person.py

Person base class, ported from TaskFlow's models/person.py so that
chess_cli gets the same two-level inheritance chain TaskFlow uses
(Person -> User -> Admin) instead of User being the top of the tree.
Encapsulates name/email with validation via @property, exactly like
the TaskFlow version.
"""


class Person:
    """
    Base class representing any human entity in the system.
    Encapsulates name/email with validation via @property.
    """

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    # Encapsulated attributes
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not str(value).strip():
            raise ValueError("Name cannot be empty.")
        self._name = str(value).strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        value = str(value).strip()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError(f"Invalid email address: {value!r}")
        self._email = value.lower()

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, email={self.email!r})"
