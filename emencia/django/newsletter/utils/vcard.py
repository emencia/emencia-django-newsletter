"""VCard system for importing/exporting Contact models"""
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


def vcard_contact_import(vcard, workgroups=[]):
    from emencia.django.newsletter.models import Contact

    defaults = {'email': vcard.email.value,
                'first_name': vcard.n.value.given,
                'last_name': vcard.n.value.family}

    contact, created = Contact.objects.get_or_create(email=defaults['email'],
                                                     defaults=defaults)
    for workgroup in workgroups:
        workgroup.contacts.add(contact)
    return int(created)  # TODO rewrite this


def vcard_contacts_import(stream, workgroups=[]):
    vcards = vobject.readComponents(stream)
    inserted = 0
    for vcard in vcards:
        inserted += vcard_contact_import(vcard, workgroups)
    return inserted
