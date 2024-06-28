from accounts.models import User
from letters.models import Letter


def get_receiver(users, sender: User):
    for user in users:
        if user.id != sender.id:
            return user
    return None