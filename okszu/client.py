from django.contrib.auth.models import User
from django.http import request


class Attestation:
    curr_user = User.objects.get()
    test = 5

    def __init__(self):
        print(self.test)
        print(self.curr_user)

    def __str__(self):
        return "Объект АТТЕСТАЦИЯ"