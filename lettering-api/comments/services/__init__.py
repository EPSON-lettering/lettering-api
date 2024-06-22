from accounts.models import User
from letters.models import Letter


def get_receiver(letter: Letter, sender: User):
    users = [letter.receiver, letter.sender]
    if users[0].id == sender.id:
        return users[0]
    return users[1]
