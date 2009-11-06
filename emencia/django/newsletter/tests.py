"""Unit tests for emencia.django.newsletter"""
from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.http import Http404
from django.db import IntegrityError
from django.contrib.sites.models import Site

from emencia.django.newsletter.tokens import tokenize
from emencia.django.newsletter.tokens import untokenize
from emencia.django.newsletter.mailer import Mailer
from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import MailingList
from emencia.django.newsletter.models import SMTPServer
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus

class FakeSMTP(object):
    mails_sent = 0
    def sendmail(self, *ka, **kw):
        self.mails_sent += 1

    def quit(*ka, **kw):
        pass
    
def fake_email_content(*ka, **kw):
    return ''

class SMTPServerTestCase(TestCase):
    """Tests for the SMTPServer model"""

    def setUp(self):
        self.server = SMTPServer.objects.create(name='Test SMTP',
                                                host='smtp.domain.com')
        self.server_2 = SMTPServer.objects.create(name='Test SMTP 2',
                                                  host='smtp.domain2.com')
        self.contact = Contact.objects.create(email='test@domain.com')
        self.mailinglist = MailingList.objects.create(name='Test MailingList')
        self.mailinglist.subscribers.add(self.contact)
        self.newsletter = Newsletter.objects.create(title='Test Newsletter',
                                                    content='Test Newsletter Content',
                                                    mailing_list=self.mailinglist,
                                                    server=self.server)
        
        self.newsletter_2 = Newsletter.objects.create(title='Test Newsletter 2',
                                                      content='Test Newsletter 2 Content',
                                                      mailing_list=self.mailinglist,
                                                      server=self.server)
        self.newsletter_3 = Newsletter.objects.create(title='Test Newsletter 2',
                                                      content='Test Newsletter 2 Content',
                                                      mailing_list=self.mailinglist,
                                                      server=self.server_2)
        
    def test_credits(self):
        # Testing unlimited account
        self.assertEquals(self.server.credits(), 1000)
        # Testing default limit
        self.server.mails_hour = 42
        self.assertEquals(self.server.credits(), 42)

        # Testing credits status, with multiple server case
        ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                            contact=self.contact,
                                            status=ContactMailingStatus.SENT)
        self.assertEquals(self.server.credits(), 41)
        ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                            contact=self.contact,
                                            status=ContactMailingStatus.SENT_TEST)
        self.assertEquals(self.server.credits(), 40)
        # Testing with a fake status
        ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                            contact=self.contact,
                                            status=ContactMailingStatus.ERROR)
        self.assertEquals(self.server.credits(), 40)
        # Testing with a second newsletter sharing the server
        ContactMailingStatus.objects.create(newsletter=self.newsletter_2,
                                            contact=self.contact,
                                            status=ContactMailingStatus.SENT)
        self.assertEquals(self.server.credits(), 39)
        # Testing with a third newsletter with another server
        ContactMailingStatus.objects.create(newsletter=self.newsletter_3,
                                            contact=self.contact,
                                            status=ContactMailingStatus.SENT)
        self.assertEquals(self.server.credits(), 39)


class ContactTestCase(TestCase):
    """Tests for the Contact model"""

    def setUp(self):
        self.mailinglist_1 = MailingList.objects.create(name='Test MailingList')
        self.mailinglist_2 = MailingList.objects.create(name='Test MailingList 2')

    def test_unique(self):
        contact = Contact(email='test@domain.com').save()
        self.assertRaises(IntegrityError, Contact(email='test@domain.com').save)
        
    def test_mail_format(self):
        contact = Contact(email='test@domain.com')
        self.assertEquals(contact.mail_format(), 'test@domain.com')
        contact = Contact(email='test@domain.com', first_name='Toto')
        self.assertEquals(contact.mail_format(), 'test@domain.com')
        contact = Contact(email='test@domain.com', first_name='Toto', last_name='Titi')
        self.assertEquals(contact.mail_format(), 'Titi Toto <test@domain.com>')

    def test_subscriptions(self):
        contact = Contact.objects.create(email='test@domain.com')
        self.assertEquals(len(contact.subscriptions()), 0)
        
        self.mailinglist_1.subscribers.add(contact)
        self.assertEquals(len(contact.subscriptions()), 1)
        self.mailinglist_2.subscribers.add(contact)
        self.assertEquals(len(contact.subscriptions()), 2)

    def test_unsubscriptions(self):
        contact = Contact.objects.create(email='test@domain.com')
        self.assertEquals(len(contact.unsubscriptions()), 0)
        
        self.mailinglist_1.unsubscribers.add(contact)
        self.assertEquals(len(contact.unsubscriptions()), 1)
        self.mailinglist_2.unsubscribers.add(contact)
        self.assertEquals(len(contact.unsubscriptions()), 2)


class MailingListTestCase(TestCase):
    """Tests for the MailingList model"""

    def setUp(self):
        self.contact_1 = Contact.objects.create(email='test1@domain.com')
        self.contact_2 = Contact.objects.create(email='test2@domain.com', valid=False)
        self.contact_3 = Contact.objects.create(email='test3@domain.com', subscriber=False)
        self.contact_4 = Contact.objects.create(email='test4@domain.com')

    def test_subscribers_count(self):
        mailinglist = MailingList(name='Test MailingList')
        mailinglist.save()
        self.assertEquals(mailinglist.subscribers_count(), 0)
        mailinglist.subscribers.add(self.contact_1, self.contact_2, self.contact_3)
        self.assertEquals(mailinglist.subscribers_count(), 3)

    def test_unsubscribers_count(self):
        mailinglist = MailingList.objects.create(name='Test MailingList')
        self.assertEquals(mailinglist.unsubscribers_count(), 0)
        mailinglist.unsubscribers.add(self.contact_1, self.contact_2, self.contact_3)
        self.assertEquals(mailinglist.unsubscribers_count(), 3)

    def test_expedition_set(self):
        mailinglist = MailingList.objects.create(name='Test MailingList')
        self.assertEquals(len(mailinglist.expedition_set()), 0)
        mailinglist.subscribers.add(self.contact_1, self.contact_2, self.contact_3)
        self.assertEquals(len(mailinglist.expedition_set()), 1)
        mailinglist.subscribers.add(self.contact_4)
        self.assertEquals(len(mailinglist.expedition_set()), 2)
        mailinglist.unsubscribers.add(self.contact_4)
        self.assertEquals(len(mailinglist.expedition_set()), 1)


class NewsletterTestCase(TestCase):
    """Tests for the Newsletter model"""

    def setUp(self):
        self.server = SMTPServer.objects.create(name='Test SMTP',
                                                host='smtp.domain.com')
        self.contact = Contact.objects.create(email='test@domain.com')
        self.mailinglist = MailingList.objects.create(name='Test MailingList')
        self.newsletter = Newsletter.objects.create(title='Test Newsletter',
                                                    content='Test Newsletter Content',
                                                    mailing_list=self.mailinglist,
                                                    server=self.server)
    def test_mails_sent(self):
        self.assertEquals(self.newsletter.mails_sent(), 0)
        ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                            contact=self.contact,
                                            status=ContactMailingStatus.SENT)
        ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                            contact=self.contact,
                                            status=ContactMailingStatus.SENT_TEST)
        self.assertEquals(self.newsletter.mails_sent(), 1)


class TokenizationTestCase(TestCase):
    """Tests for the tokenization process"""

    def setUp(self):
        self.contact = Contact.objects.create(email='test@domain.com')
        
    def test_tokenize_untokenize(self):
        uidb36, token = tokenize(self.contact)
        self.assertEquals(untokenize(uidb36, token), self.contact)
        self.assertRaises(Http404, untokenize, 'toto', token)
        self.assertRaises(Http404, untokenize, uidb36, 'toto')

class MailerTestCase(TestCase):
    """Tests for the Mailer object"""

    def setUp(self):
        self.server = SMTPServer.objects.create(name='Test SMTP',
                                                host='smtp.domain.com',
                                                mails_hour=100)
        self.contacts = [Contact.objects.create(email='test1@domain.com'),
                         Contact.objects.create(email='test2@domain.com'),
                         Contact.objects.create(email='test3@domain.com'),
                         Contact.objects.create(email='test4@domain.com'),]
        self.mailinglist = MailingList.objects.create(name='Test MailingList')
        self.mailinglist.subscribers.add(*self.contacts)
        self.newsletter = Newsletter.objects.create(title='Test Newsletter',
                                                    content='Test Newsletter Content',
                                                    mailing_list=self.mailinglist,
                                                    server=self.server,
                                                    status=Newsletter.WAITING)
        self.newsletter.test_contacts.add(*self.contacts[:2])

        
    def test_expedition_list(self):
        mailer = Mailer(self.newsletter, test=True)
        self.assertEquals(len(mailer.get_expedition_list()), 2)
        self.server.mails_hour = 1
        self.assertEquals(len(mailer.get_expedition_list()), 1)

        self.server.mails_hour = 100
        mailer = Mailer(self.newsletter)
        self.assertEquals(len(mailer.get_expedition_list()), 4)
        self.server.mails_hour = 3
        self.assertEquals(len(mailer.get_expedition_list()), 3)

        self.server.mails_hour = 100
        ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                            contact=self.contacts[0],
                                            status=ContactMailingStatus.SENT)
        ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                            contact=self.contacts[1],
                                            status=ContactMailingStatus.SENT)
        self.assertEquals(len(mailer.get_expedition_list()), 2)
        self.assertFalse(self.contacts[0] in mailer.get_expedition_list())

    def test_can_send(self):
        mailer = Mailer(self.newsletter)
        self.assertTrue(mailer.can_send)

        # Checks credits
        self.server.mails_hour = 1
        ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                            contact=self.contacts[0],
                                            status=ContactMailingStatus.SENT)
        mailer = Mailer(self.newsletter)
        self.assertFalse(mailer.can_send)
        self.server.mails_hour = 10
        mailer = Mailer(self.newsletter)
        self.assertTrue(mailer.can_send)

        # Checks statut
        self.newsletter.status = Newsletter.DRAFT
        mailer = Mailer(self.newsletter)
        self.assertFalse(mailer.can_send)
        mailer = Mailer(self.newsletter, test=True)
        self.assertTrue(mailer.can_send)

        # Checks expedition time
        self.newsletter.status = Newsletter.WAITING
        self.newsletter.sending_date = datetime.now() + timedelta(hours=1)
        mailer = Mailer(self.newsletter)
        self.assertFalse(mailer.can_send)
        self.newsletter.sending_date = datetime.now()
        mailer = Mailer(self.newsletter)
        self.assertTrue(mailer.can_send)

    def test_run(self):        
        mailer = Mailer(self.newsletter)
        mailer.smtp = FakeSMTP()
        mailer.build_email_content = fake_email_content        
        mailer.run()
        self.assertEquals(mailer.smtp.mails_sent, 4)
        self.assertEquals(ContactMailingStatus.objects.filter(
            status=ContactMailingStatus.SENT, newsletter=self.newsletter).count(), 4)
        
        mailer = Mailer(self.newsletter, test=True)
        mailer.smtp = FakeSMTP()
        mailer.build_email_content = fake_email_content
        
        mailer.run()
        self.assertEquals(mailer.smtp.mails_sent, 2)
        self.assertEquals(ContactMailingStatus.objects.filter(
            status=ContactMailingStatus.SENT_TEST, newsletter=self.newsletter).count(), 2)

    def test_update_newsletter_status(self):
        mailer = Mailer(self.newsletter, test=True)
        self.assertEquals(self.newsletter.status, Newsletter.WAITING)
        mailer.update_newsletter_status()
        self.assertEquals(self.newsletter.status, Newsletter.WAITING)

        mailer = Mailer(self.newsletter)
        self.assertEquals(self.newsletter.status, Newsletter.WAITING)
        mailer.update_newsletter_status()
        self.assertEquals(self.newsletter.status, Newsletter.SENDING)

        for contact in self.contacts:
            ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                                contact=contact,
                                                status=ContactMailingStatus.SENT)
        mailer.update_newsletter_status()
        self.assertEquals(self.newsletter.status, Newsletter.SENT)

