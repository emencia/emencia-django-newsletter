from south.db import db
from django.db import models
from emencia.django.newsletter.models import *


class Migration:

    def forwards(self, orm):

        # Adding model 'MailingList'
        db.create_table('newsletter_mailinglist', (
            ('id', orm['newsletter.MailingList:id']),
            ('name', orm['newsletter.MailingList:name']),
            ('description', orm['newsletter.MailingList:description']),
            ('creation_date', orm['newsletter.MailingList:creation_date']),
            ('modification_date', orm['newsletter.MailingList:modification_date']),
        ))
        db.send_create_signal('newsletter', ['MailingList'])

        # Adding model 'ContactMailingStatus'
        db.create_table('newsletter_contactmailingstatus', (
            ('id', orm['newsletter.ContactMailingStatus:id']),
            ('newsletter', orm['newsletter.ContactMailingStatus:newsletter']),
            ('contact', orm['newsletter.ContactMailingStatus:contact']),
            ('status', orm['newsletter.ContactMailingStatus:status']),
            ('link', orm['newsletter.ContactMailingStatus:link']),
            ('creation_date', orm['newsletter.ContactMailingStatus:creation_date']),
        ))
        db.send_create_signal('newsletter', ['ContactMailingStatus'])

        # Adding model 'WorkGroup'
        db.create_table('newsletter_workgroup', (
            ('id', orm['newsletter.WorkGroup:id']),
            ('name', orm['newsletter.WorkGroup:name']),
            ('group', orm['newsletter.WorkGroup:group']),
        ))
        db.send_create_signal('newsletter', ['WorkGroup'])

        # Adding model 'Link'
        db.create_table('newsletter_link', (
            ('id', orm['newsletter.Link:id']),
            ('title', orm['newsletter.Link:title']),
            ('url', orm['newsletter.Link:url']),
            ('creation_date', orm['newsletter.Link:creation_date']),
        ))
        db.send_create_signal('newsletter', ['Link'])

        # Adding model 'Newsletter'
        db.create_table('newsletter_newsletter', (
            ('id', orm['newsletter.Newsletter:id']),
            ('title', orm['newsletter.Newsletter:title']),
            ('content', orm['newsletter.Newsletter:content']),
            ('mailing_list', orm['newsletter.Newsletter:mailing_list']),
            ('server', orm['newsletter.Newsletter:server']),
            ('header_sender', orm['newsletter.Newsletter:header_sender']),
            ('header_reply', orm['newsletter.Newsletter:header_reply']),
            ('status', orm['newsletter.Newsletter:status']),
            ('sending_date', orm['newsletter.Newsletter:sending_date']),
            ('slug', orm['newsletter.Newsletter:slug']),
            ('creation_date', orm['newsletter.Newsletter:creation_date']),
            ('modification_date', orm['newsletter.Newsletter:modification_date']),
        ))
        db.send_create_signal('newsletter', ['Newsletter'])

        # Adding model 'SMTPServer'
        db.create_table('newsletter_smtpserver', (
            ('id', orm['newsletter.SMTPServer:id']),
            ('name', orm['newsletter.SMTPServer:name']),
            ('host', orm['newsletter.SMTPServer:host']),
            ('user', orm['newsletter.SMTPServer:user']),
            ('password', orm['newsletter.SMTPServer:password']),
            ('port', orm['newsletter.SMTPServer:port']),
            ('tls', orm['newsletter.SMTPServer:tls']),
            ('headers', orm['newsletter.SMTPServer:headers']),
            ('mails_hour', orm['newsletter.SMTPServer:mails_hour']),
        ))
        db.send_create_signal('newsletter', ['SMTPServer'])

        # Adding model 'Contact'
        db.create_table('newsletter_contact', (
            ('id', orm['newsletter.Contact:id']),
            ('email', orm['newsletter.Contact:email']),
            ('first_name', orm['newsletter.Contact:first_name']),
            ('last_name', orm['newsletter.Contact:last_name']),
            ('subscriber', orm['newsletter.Contact:subscriber']),
            ('valid', orm['newsletter.Contact:valid']),
            ('tester', orm['newsletter.Contact:tester']),
            ('tags', orm['newsletter.Contact:tags']),
            ('content_type', orm['newsletter.Contact:content_type']),
            ('object_id', orm['newsletter.Contact:object_id']),
            ('creation_date', orm['newsletter.Contact:creation_date']),
            ('modification_date', orm['newsletter.Contact:modification_date']),
        ))
        db.send_create_signal('newsletter', ['Contact'])

        # Adding ManyToManyField 'WorkGroup.mailinglists'
        db.create_table('newsletter_workgroup_mailinglists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workgroup', models.ForeignKey(orm.WorkGroup, null=False)),
            ('mailinglist', models.ForeignKey(orm.MailingList, null=False))
        ))

        # Adding ManyToManyField 'MailingList.subscribers'
        db.create_table('newsletter_mailinglist_subscribers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm.MailingList, null=False)),
            ('contact', models.ForeignKey(orm.Contact, null=False))
        ))

        # Adding ManyToManyField 'WorkGroup.contacts'
        db.create_table('newsletter_workgroup_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workgroup', models.ForeignKey(orm.WorkGroup, null=False)),
            ('contact', models.ForeignKey(orm.Contact, null=False))
        ))

        # Adding ManyToManyField 'WorkGroup.newsletters'
        db.create_table('newsletter_workgroup_newsletters', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workgroup', models.ForeignKey(orm.WorkGroup, null=False)),
            ('newsletter', models.ForeignKey(orm.Newsletter, null=False))
        ))

        # Adding ManyToManyField 'MailingList.unsubscribers'
        db.create_table('newsletter_mailinglist_unsubscribers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailinglist', models.ForeignKey(orm.MailingList, null=False)),
            ('contact', models.ForeignKey(orm.Contact, null=False))
        ))

        # Adding ManyToManyField 'Newsletter.test_contacts'
        db.create_table('newsletter_newsletter_test_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newsletter', models.ForeignKey(orm.Newsletter, null=False)),
            ('contact', models.ForeignKey(orm.Contact, null=False))
        ))

    def backwards(self, orm):

        # Deleting model 'MailingList'
        db.delete_table('newsletter_mailinglist')

        # Deleting model 'ContactMailingStatus'
        db.delete_table('newsletter_contactmailingstatus')

        # Deleting model 'WorkGroup'
        db.delete_table('newsletter_workgroup')

        # Deleting model 'Link'
        db.delete_table('newsletter_link')

        # Deleting model 'Newsletter'
        db.delete_table('newsletter_newsletter')

        # Deleting model 'SMTPServer'
        db.delete_table('newsletter_smtpserver')

        # Deleting model 'Contact'
        db.delete_table('newsletter_contact')

        # Dropping ManyToManyField 'WorkGroup.mailinglists'
        db.delete_table('newsletter_workgroup_mailinglists')

        # Dropping ManyToManyField 'MailingList.subscribers'
        db.delete_table('newsletter_mailinglist_subscribers')

        # Dropping ManyToManyField 'WorkGroup.contacts'
        db.delete_table('newsletter_workgroup_contacts')

        # Dropping ManyToManyField 'WorkGroup.newsletters'
        db.delete_table('newsletter_workgroup_newsletters')

        # Dropping ManyToManyField 'MailingList.unsubscribers'
        db.delete_table('newsletter_mailinglist_unsubscribers')

        # Dropping ManyToManyField 'Newsletter.test_contacts'
        db.delete_table('newsletter_newsletter_test_contacts')

    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'newsletter.contact': {
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subscriber': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
            'tester': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'newsletter.contactmailingstatus': {
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['newsletter.Contact']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['newsletter.Link']", 'null': 'True', 'blank': 'True'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['newsletter.Newsletter']"}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        },
        'newsletter.link': {
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'newsletter.mailinglist': {
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['newsletter.Contact']"}),
            'unsubscribers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['newsletter.Contact']", 'null': 'True', 'blank': 'True'})
        },
        'newsletter.newsletter': {
            'content': ('django.db.models.fields.TextField', [], {'default': "u'<body>\\n<!-- Edit your newsletter here -->\\n</body>'"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'header_reply': ('django.db.models.fields.CharField', [], {'default': "'Emencia Newsletter<noreply@emencia.com>'", 'max_length': '255'}),
            'header_sender': ('django.db.models.fields.CharField', [], {'default': "'Emencia Newsletter<noreply@emencia.com>'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['newsletter.MailingList']"}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'sending_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['newsletter.SMTPServer']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'test_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['newsletter.Contact']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'newsletter.smtpserver': {
            'headers': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mails_hour': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '25'}),
            'tls': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'newsletter.workgroup': {
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['newsletter.Contact']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailinglists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['newsletter.MailingList']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'newsletters': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['newsletter.Newsletter']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['newsletter']
