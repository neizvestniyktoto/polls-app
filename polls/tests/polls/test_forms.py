from django.test import TestCase
from django.utils import timezone

from polls.forms import QuestionForm, SignUpForm


class SignUpFormTest(TestCase):
    def createForm(self, email='email@email.com', birth_day=1, birth_month=1, birth_year=1900):
        kwargs = {
            'username': 'username',
            'first_name': 'first',
            'last_name': 'last',
            'email': email,
            'birth_day': birth_day,
            'birth_month': birth_month,
            'birth_year': birth_year,
            'password1': 'password8888',
            'password2': 'password8888',
        }
        return SignUpForm(data=kwargs)

    def test_invalid_day(self):
        form = self.createForm(birth_day=32, birth_month=1, birth_year=2020)
        self.assertFalse(form.is_valid())

    def test_invalid_february_day(self):
        form = self.createForm(birth_day=31, birth_month=2, birth_year=2020)
        self.assertFalse(form.is_valid())

    def test_invalid_month(self):
        form = self.createForm(birth_day=1, birth_month=13, birth_year=2020)
        self.assertFalse(form.is_valid())

    def test_invalid_year(self):
        form = self.createForm(birth_day=1, birth_month=1, birth_year=1800)
        self.assertFalse(form.is_valid())

    def test_date_in_future(self):
        current_date = timezone.now()
        kwargs = {
            'birth_day': current_date.day + 1,
            'birth_month': current_date.month,
            'birth_year': current_date.year,
        }
        form = self.createForm(**kwargs)
        self.assertFalse(form.is_valid())