"""Utils for importation of contacts"""
import csv

import xlrd

from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.utils.vcard import vcard_contacts_import


COLUMNS = ['email', 'first_name', 'last_name', 'tags']
csv.register_dialect('edn', delimiter=';')


def text_contacts_import(stream, workgroups=[]):
    """Import contact from a plaintext file, like CSV"""
    inserted = 0
    contact_reader = csv.reader(stream, dialect='edn')

    for contact_row in contact_reader:
        defaults = {}
        for i in range(len(contact_row)):
            defaults[COLUMNS[i]] = contact_row[i]
        contact, created = Contact.objects.get_or_create(
            email=defaults['email'],
            defaults=defaults)
        for workgroup in workgroups:
            workgroup.contacts.add(contact)
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
        contact, created = Contact.objects.get_or_create(
            email=defaults['email'],
            defaults=defaults)
        for workgroup in workgroups:
            workgroup.contacts.add(contact)
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
