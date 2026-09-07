"""
person.py
Defines the Person base class. User inherits from Person, demonstrating
the inheritance requirement (Person -> User).
"""


class Person:
    """
    Base class representing any human entity in the system.
    Encapsulates name/email with validation via @property.
    """

    def __init__(self, name: str, email: str):
        self._name = None
        self._email = None
        self.name = name    # goes through setter -> validation
        self.email = email  # goes through setter -> validation

    # ---------- Encapsulated attributes ----------
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
