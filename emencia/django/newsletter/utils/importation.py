"""Utils for importation of contacts"""
import csv
from datetime import datetime

import xlrd
import vobject

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag

from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import MailingList


COLUMNS = ['email', 'first_name', 'last_name', 'tags']
csv.register_dialect('edn', delimiter=';')


def create_contact(contact_dict, workgroups=[]):
    """Create a contact and validate the mail"""
    contact_dict['email'] = contact_dict['email'].strip()
    try:
        validate_email(contact_dict['email'])
        contact_dict['valid'] = True
    except ValidationError:
        contact_dict['valid'] = False

    contact, created = Contact.objects.get_or_create(
        email=contact_dict['email'],
        defaults=contact_dict)

    if not created:
        new_tags = contact_dict.get('tags')
        if new_tags:
            Tag.objects.update_tags(contact, '%s, %s' % (contact.tags, new_tags))

    for workgroup in workgroups:
        workgroup.contacts.add(contact)

    return contact, created


def create_contacts(contact_dicts, importer_name, workgroups=[]):
    """Create all the contacts to import and
    associated them in a mailing list"""
    inserted = 0
    when = str(datetime.now()).split('.')[0]
    mailing_list = MailingList(
        name=_('Mailing list created by importation at %s') % when,
        description=_('Contacts imported by %s.') % importer_name)
    mailing_list.save()

    for workgroup in workgroups:
        workgroup.mailinglists.add(mailing_list)

    for contact_dict in contact_dicts:
        contact, created = create_contact(contact_dict, workgroups)
        mailing_list.subscribers.add(contact)
        inserted += int(created)

    return inserted


def vcard_contacts_import(stream, workgroups=[]):
    """Import contacts from a VCard file"""
    contacts = []
    vcards = vobject.readComponents(stream)

    for vcard in vcards:
        contact = {'email': vcard.email.value,
                   'first_name': vcard.n.value.given,
                   'last_name': vcard.n.value.family}
        contacts.append(contact)

    return create_contacts(contacts, 'vcard', workgroups)


def text_contacts_import(stream, workgroups=[]):
    """Import contact from a plaintext file, like CSV"""
    contacts = []
    contact_reader = csv.reader(stream, dialect='edn')

    for contact_row in contact_reader:
        contact = {}
        for i in range(len(contact_row)):
            contact[COLUMNS[i]] = contact_row[i]
        contacts.append(contact)

    return create_contacts(contacts, 'text', workgroups)


def excel_contacts_import(stream, workgroups=[]):
    """Import contacts from an Excel file"""
    contacts = []
    wb = xlrd.open_workbook(file_contents=stream.read())
    sh = wb.sheet_by_index(0)

    for row in range(sh.nrows):
        contact = {}
        for i in range(len(COLUMNS)):
            try:
                value = sh.cell(row, i).value
                contact[COLUMNS[i]] = value
            except IndexError:
                break
        contacts.append(contact)

    return create_contacts(contacts, 'excel', workgroups)


def import_dispatcher(source, type_, workgroups):
    """Select importer and import contacts"""
    if type_ == 'vcard':
        return vcard_contacts_import(source, workgroups)
    elif type_ == 'text':
        return text_contacts_import(source, workgroups)
    elif type_ == 'excel':
        return excel_contacts_import(source, workgroups)
    return 0
