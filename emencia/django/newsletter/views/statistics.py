"""Views for emencia.django.newsletter statistics"""
import csv
from datetime import timedelta

from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import date

from emencia.django.newsletter.utils.ofc import Chart
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.utils.statistics import get_newsletter_top_links
from emencia.django.newsletter.utils.statistics import get_newsletter_statistics
from emencia.django.newsletter.utils.statistics import get_newsletter_opening_statistics
from emencia.django.newsletter.utils.statistics import get_newsletter_clicked_link_statistics

BG_COLOR = '#ffffff'
GRID_COLOR = '#eeeeee'
AXIS_COLOR = '#666666'
BAR_COLOR_1 = '#5b80b2'
BAR_COLOR_2 = '#ff3333'
BAR_COLOR_3 = '#9459b4'
BAR_COLOR_4 = '#5eca71'


def get_statistics_period(newsletter):
    status = ContactMailingStatus.objects.filter(Q(status=ContactMailingStatus.OPENED) |
                                                 Q(status=ContactMailingStatus.OPENED_ON_SITE) |
                                                 Q(status=ContactMailingStatus.LINK_OPENED),
                                                 newsletter=newsletter)
    if not status:
        return []
    start_date = newsletter.sending_date.date()
    end_date = status.latest('creation_date').creation_date.date()

    period = []
    for i in range((end_date - start_date).days + 1):
        period.append(start_date + timedelta(days=i))
    return period


@login_required
def view_newsletter_statistics(request, slug):
    """Display the statistics of a newsletters"""
    opts = Newsletter._meta
    newsletter = get_object_or_404(Newsletter, slug=slug)

    context = {'title': _('Statistics of %s') % newsletter.__unicode__(),
               'object': newsletter,
               'opts': opts,
               'object_id': newsletter.pk,
               'app_label': opts.app_label,
               'stats': get_newsletter_statistics(newsletter),
               'period': get_statistics_period(newsletter)}

    return render_to_response('newsletter/newsletter_statistics.html',
                              context, context_instance=RequestContext(request))


@login_required
def view_newsletter_report(request, slug):
    newsletter = get_object_or_404(Newsletter, slug=slug)
    status = ContactMailingStatus.objects.filter(newsletter=newsletter,
                                                 creation_date__gte=newsletter.sending_date)
    links = set([s.link for s in status.exclude(link=None)])

    def header_line(links):
        link_cols = [smart_str(link.title) for link in links]
        return [smart_str(_('first name')), smart_str(_('last name')),
                smart_str(_('email')), smart_str(_('openings'))] + link_cols

    def contact_line(contact, links):
        contact_status = status.filter(contact=contact)

        link_cols = [contact_status.filter(status=ContactMailingStatus.LINK_OPENED,
                                           link=link).count() for link in links]
        openings = contact_status.filter(Q(status=ContactMailingStatus.OPENED) |
                                         Q(status=ContactMailingStatus.OPENED_ON_SITE)).count()
        return [smart_str(contact.first_name), smart_str(contact.last_name),
                smart_str(contact.email), openings] + link_cols

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report-%s.csv' % newsletter.slug

    writer = csv.writer(response)
    writer.writerow(header_line(links))
    for contact in newsletter.mailing_list.expedition_set():
        writer.writerow(contact_line(contact, links))

    return response


@login_required
def view_newsletter_density(request, slug):
    newsletter = get_object_or_404(Newsletter, slug=slug)
    status = ContactMailingStatus.objects.filter(newsletter=newsletter,
                                                 creation_date__gte=newsletter.sending_date)
    context = {'object': newsletter,
               'top_links': get_newsletter_top_links(status)['top_links']}

    return render_to_response('newsletter/newsletter_density.html',
                              context, context_instance=RequestContext(request))


@login_required
def view_newsletter_charts(request, slug):
    newsletter = get_object_or_404(Newsletter, slug=slug)

    start = int(request.POST.get('start', 0))
    end = int(request.POST.get('end', 6))

    recipients = newsletter.mailing_list.expedition_set().count()

    sending_date = newsletter.sending_date.date()
    labels, clicks_by_day, openings_by_day = [], [], []

    for i in range(start, end + 1):
        day = sending_date + timedelta(days=i)
        day_status = ContactMailingStatus.objects.filter(newsletter=newsletter,
                                                         creation_date__day=day.day,
                                                         creation_date__month=day.month,
                                                         creation_date__year=day.year)

        opening_stats = get_newsletter_opening_statistics(day_status, recipients)
        click_stats = get_newsletter_clicked_link_statistics(day_status, recipients, 0)
        # Labels
        labels.append(date(day, 'D d M y').capitalize())
        # Values
        openings_by_day.append(opening_stats['total_openings'])
        clicks_by_day.append(click_stats['total_clicked_links'])

    b1 = Chart(type='bar_3d', colour=BAR_COLOR_1,
               text=_('Total openings'), tip=_('#val# openings'),
               on_show={'type': 'grow-up'}, values=openings_by_day)

    b2 = Chart(type='bar_3d', colour=BAR_COLOR_2,
               text=_('Total clicked links'), tip=_('#val# clicks'),
               on_show={'type': 'grow-up'}, values=clicks_by_day)

    chart = Chart(bg_colour=BG_COLOR)
    chart.title.text = _('Consultation histogram')
    chart.title.style = '{font-size: 16px; color: #666666; text-align: center; font-weight: bold;}'

    chart.y_axis = {'colour': AXIS_COLOR, 'grid-colour': GRID_COLOR,
                    'min': 0, 'max': max(openings_by_day + clicks_by_day) + 2,
                    'steps': max(openings_by_day) / 5}
    chart.x_axis = {'colour': AXIS_COLOR, 'grid-colour': GRID_COLOR,
                    '3d': 5, 'labels': {'labels': labels, 'rotate': 60}}
    chart.elements = [b1, b2]

    return HttpResponse(chart.render())
