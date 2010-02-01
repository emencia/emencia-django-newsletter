"""Views for emencia.django.newsletter statistics"""
from datetime import timedelta

#import pyofc2
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import date

from emencia.django.newsletter.ofc import Chart
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.statistics import get_newsletter_statistics
from emencia.django.newsletter.statistics import get_newsletter_opening_statistics
from emencia.django.newsletter.statistics import get_newsletter_clicked_link_statistics

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
    start_date = newsletter.sending_date
    end_date = status.latest('creation_date').creation_date

    period = []
    for i in range((end_date - start_date).days):
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
               'period': get_statistics_period(newsletter),}

    return render_to_response('newsletter/newsletter_statistics.html',
                              context, context_instance=RequestContext(request))

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


    b1 = Chart()
    b1.type = 'bar_3d'
    b1.colour = BAR_COLOR_1
    b1.text = _('Total openings')
    b1.tip = _('#val# openings')
    b1.on_show = {'type': 'grow-up'}
    b1.values = openings_by_day

    b2 = Chart()
    b2.type = 'bar_3d'
    b2.colour = BAR_COLOR_2
    b2.text = _('Total clicked links')
    b2.tip = _('#val# clicks')
    b2.on_show = {'type': 'grow-up'}
    b2.values = clicks_by_day

    chart = Chart()
    chart.bg_colour = BG_COLOR
    chart.title.text = _('Consultation histogram')
    chart.title.style = '{font-size: 16px; color: #666666; text-align: center; font-weight: bold;}'

    chart.y_axis = {'colour': AXIS_COLOR, 'grid-colour': GRID_COLOR,
                    'min': 0, 'max': max(openings_by_day) + 2,
                    'steps': max(openings_by_day) / 5}
    chart.x_axis = {'colour': AXIS_COLOR, 'grid-colour': GRID_COLOR,
                    '3d': 5, 'labels': {'labels': labels, 'rotate': 60}}
    
    
    chart.elements = [b1, b2]

    return HttpResponse(chart.create())
