"""VCard system for importing/exporting Contact models"""
from datetime import datetime

import vobject
from django.http import HttpResponse

def vcard_contact_export(contact):
    """Export in VCard 3.0 a Contact model instance"""
    VCARD_PATTERN = u'BEGIN:VCARD\r\nVERSION:3.0\r\n'\
                    'EMAIL;TYPE=INTERNET:%(email)s\r\n'\
                    'FN:%(first_name)s %(last_name)s\r\n'\
                    'N:%(last_name)s;%(first_name)s;;;\r\n'\
                    'END:VCARD\r\n'
    return VCARD_PATTERN % contact.__dict__

def vcard_contacts_export(contacts):
    """Export multiples contacts in VCard"""
    export = ''
    for contact in contacts:
        export += '%s\r\n' % vcard_contact_export(contact)
    return export

def vcard_contacts_export_response(contacts, filename=''):
    """Return VCard contacts attached in a HttpResponse"""
    if not filename:
        filename = 'contacts_edn_%s' % datetime.now().strftime('%d-%m-%Y')
    filename = filename.replace(' ', '_')
        
    response = HttpResponse(vcard_contacts_export(contacts),
                            mimetype='text/x-vcard')
    response['Content-Disposition'] = 'attachment; filename=%s.vcf' % filename
    return response

def vcard_contact_import(vcard):
    pass

def vcard_contacts_import(stream):
    pass

