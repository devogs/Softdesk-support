import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Adds specific fields required for the SoftDesk application:
    - age: User's age, for GDPR consent verification.
    - can_be_contacted: User's consent to be contacted.
    - can_data_be_shared: User's consent for data sharing.
    - created_time: Timestamp of user creation.
    """

    age = models.IntegerField(null=True, blank=True)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the username as the string representation of the User.
        """
        return self.username

    def has_minimum_age(self):
        """
        Checks if the user meets the minimum age requirement (15 years) for registration.

        Returns:
            bool: True if age is 15 or more, False otherwise.
        """
        return self.age is not None and self.age >= 15

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def is_recently_registered(self):
        """
        Determines if the user was registered within the last 24 hours.

        Returns:
            bool: True if registered within the last 24 hours, False otherwise.
        """
        now = datetime.datetime.now(self.created_time.tzinfo)
        return now - self.created_time < datetime.timedelta(days=1)
