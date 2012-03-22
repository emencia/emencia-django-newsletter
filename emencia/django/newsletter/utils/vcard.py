"""VCard system for exporting Contact models"""
from datetime import datetime

import vobject

from django.http import HttpResponse


def vcard_contact_export(contact):
    """Export in VCard 3.0 a Contact model instance"""
    if hasattr(contact.content_object, 'vcard_export'):
        return contact.content_object.vcard_export()

    vcard = vobject.vCard()
    vcard.add('n')
    vcard.n.value = vobject.vcard.Name(family=contact.last_name, given=contact.first_name)
    vcard.add('fn')
    vcard.fn.value = '%s %s' % (contact.first_name, contact.last_name)
    vcard.add('email')
    vcard.email.value = contact.email
    vcard.email.type_param = 'INTERNET'
    return vcard.serialize()


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
