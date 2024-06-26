from enum import Enum


class LetterWritingStatus(Enum):
    BEFORE = 0
    PROCESSING = 1

    def parse(self) -> int:
        return self.value


def parse_letter_status(status: LetterWritingStatus) -> int:
    return status.value