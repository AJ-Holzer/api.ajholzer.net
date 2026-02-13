# ============================== #
#  Copyright (c) AJ-Holzer       #
#  SPDX-License-Identifier: MIT  #
# ============================== #


from enum import Enum, auto


# Define valid log levels
NAME_TO_LEVEL: list[str] = [
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
    "NOTSET",
]


# Config checking enum
class Condition(Enum):
    NotEmpty = auto()
    NotZero = auto()
    IsNumeric = auto()
    IsAlphaNumeric = auto()
    IsAlpha = auto()
    IsBool = auto()

    def validate(self, value: str) -> bool:
        """Validates the condition of the given value.

        Args:
            value (str): The value which conditions will be validate.

        Returns:
            bool: Whether the condition is true.
        """
        match self:
            case Condition.NotEmpty:
                return value == ""
            case Condition.NotZero:
                return not value.isnumeric() or int(value) == 0
            case Condition.IsNumeric:
                return not value.isnumeric()
            case Condition.IsAlphaNumeric:
                return not value.isalnum()
            case Condition.IsAlpha:
                return not value.isalpha()
            case Condition.IsBool:
                return value.lower() not in ["false", "true", "0", "1"]
