"""Utils for workgroups"""
from emencia.django.newsletter.models import WorkGroup


def request_workgroups(request):
    return WorkGroup.objects.filter(group__in=request.user.groups.all())


def request_workgroups_contacts_pk(request):
    contacts = []
    for workgroup in request_workgroups(request):
        contacts.extend([c.pk for c in workgroup.contacts.all()])
    return set(contacts)


def request_workgroups_mailinglists_pk(request):
    mailinglists = []
    for workgroup in request_workgroups(request):
        mailinglists.extend([ml.pk for ml in workgroup.mailinglists.all()])
    return set(mailinglists)


def request_workgroups_newsletters_pk(request):
    newsletters = []
    for workgroup in request_workgroups(request):
        newsletters.extend([n.pk for n in workgroup.newsletters.all()])
    return set(newsletters)
