"""Managers for emencia.django.newsletter"""
from django.db import models


class ContactManager(models.Manager):
    """Manager for the contacts"""

    def subscribers(self):
        """Return all subscribers"""
        return self.get_query_set().filter(subscriber=True)

    def unsubscribers(self):
        """Return all unsubscribers"""
        return self.get_query_set().filter(subscriber=False)

    def valids(self):
        """Return only valid contacts"""
        return self.get_query_set().filter(valid=True)

    def valid_subscribers(self):
        """Return only valid subscribers"""
        return self.subscribers().filter(valid=True)
