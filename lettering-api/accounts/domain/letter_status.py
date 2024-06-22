from enum import Enum


class LetterWritingStatus(Enum):
    BEFORE = 0
    PROCESSING = 1

    def parse(self) -> int:
        return parse_letter_status(self)


def parse_letter_status(status: LetterWritingStatus):
    print(status)
    if status.PROCESSING:
        return 1
    return 0
