"""Command for sending the newsletter"""
from django.core.management.base import NoArgsCommand

from emencia.django.newsletter.mailer import Mailer
from emencia.django.newsletter.models import Newsletter

class Command(NoArgsCommand):
    """Send the newsletter in queue"""
    help = 'Send the newsletter in queue'

    def handle_noargs(self, **options):
        print 'Starting sending newsletters...'

        for newsletter in Newsletter.objects.exclude(
            status=Newsletter.DRAFT).exclude(status=Newsletter.SENT):
            mailer = Mailer(newsletter)
            if mailer.can_send:
                print 'Start emailing %s' % newsletter.title
                mailer.run()

        print 'End session sending'
        
    
