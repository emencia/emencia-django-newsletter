"""Utils for importation of contacts"""
import csv

import xlrd
import vobject

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from emencia.django.newsletter.models import Contact


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

    for workgroup in workgroups:
        workgroup.contacts.add(contact)

    return contact, created


def vcard_contacts_import(stream, workgroups=[]):
    inserted = 0
    vcards = vobject.readComponents(stream)

    for vcard in vcards:
        defaults = {'email': vcard.email.value,
                    'first_name': vcard.n.value.given,
                    'last_name': vcard.n.value.family}
        contact, created = create_contact(defaults, workgroups)
        inserted += int(created)

    return inserted


def text_contacts_import(stream, workgroups=[]):
    """Import contact from a plaintext file, like CSV"""
    inserted = 0
    contact_reader = csv.reader(stream, dialect='edn')

    for contact_row in contact_reader:
        defaults = {}
        for i in range(len(contact_row)):
            defaults[COLUMNS[i]] = contact_row[i]
        contact, created = create_contact(defaults, workgroups)
        inserted += int(created)

    return inserted


def excel_contacts_import(stream, workgroups=[]):
    inserted = 0
    wb = xlrd.open_workbook(file_contents=stream.read())
    sh = wb.sheet_by_index(0)

    for row in range(sh.nrows):
        defaults = {}
        for i in range(len(COLUMNS)):
            try:
                value = sh.cell(row, i).value
                defaults[COLUMNS[i]] = value
            except IndexError:
                break
        contact, created = create_contact(defaults, workgroups)
        inserted += int(created)

    return inserted


def import_dispatcher(source, type_, workgroups):
    """Select importer and import contacts"""
    if type_ == 'vcard':
        return vcard_contacts_import(source, workgroups)
    elif type_ == 'text':
        return text_contacts_import(source, workgroups)
    elif type_ == 'excel':
        return excel_contacts_import(source, workgroups)
    return 0
