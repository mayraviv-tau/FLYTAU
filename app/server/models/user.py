"""
User data models for FLYTAU application.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Base user class for customers."""
    email: str
    first_name: str
    last_name: str

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }


@dataclass
class RegisteredCustomer(User):
    """Registered customer with account."""
    balance: float
    birth_date: Optional[str] = None
    passport_number: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary."""
        data = super().to_dict()
        data.update({
            'balance': float(self.balance),
            'is_registered': True
        })
        if self.birth_date:
            data['birth_date'] = str(self.birth_date)
        if self.passport_number:
            data['passport_number'] = self.passport_number
        return data


@dataclass
class Manager:
    """Manager/admin user."""
    id_number: str
    first_name: str
    last_name: str

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id_number': self.id_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_type': 'manager'
        }
