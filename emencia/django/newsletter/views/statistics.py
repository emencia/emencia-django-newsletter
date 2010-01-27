"""Views for emencia.django.newsletter statistics"""
from datetime import timedelta

import pyofc2
from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import date

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
    display_clicks = True
    if request.POST:
        display_clicks = request.POST.get('display_clicks')

    recipients = newsletter.mailing_list.expedition_set().count()
    dates = []
    day = newsletter.sending_date.date()
    for i in range(start, end + 1):
        dates.append(day + timedelta(days=i))

    labels = []
    total_clicks = []
    total_openings = []
    clicks_by_day = []
    openings_by_day = []

    for day in dates:
        day_status = ContactMailingStatus.objects.filter(newsletter=newsletter,
                                                         creation_date__day=day.day,
                                                         creation_date__month=day.month,
                                                         creation_date__year=day.year)
        opening_stats = get_newsletter_opening_statistics(day_status, recipients)
        click_stats = get_newsletter_clicked_link_statistics(day_status, recipients, 0)
        # Labels
        labels.append(date(day, 'D d M y').capitalize())
        # For determining max Y scale
        total_openings.append(opening_stats['total_openings'])
        total_clicks.append(click_stats['total_clicked_links'])
        # Values
        if not opening_stats['double_openings']:
            opening_stats['double_openings'] = None
        if not click_stats['double_clicked_links']:
            click_stats['double_clicked_links'] = None
        openings_by_day.append([opening_stats['unique_openings'],
                                opening_stats['double_openings']])
        clicks_by_day.append([click_stats['unique_clicked_links'],
                              click_stats['double_clicked_links']])


    b1 = pyofc2.bar_stack()
    b1.colours = (BAR_COLOR_1, BAR_COLOR_2)
    b1.keys = [{'colour': BAR_COLOR_1, 'text':_('Unique opening'), 'font-size': 13},
               {'colour': BAR_COLOR_2, 'text':_('Double openings'), 'font-size': 13},]
    #b1.on_show = {'type': 'pop', 'cascade': 1, 'delay': 0.5 }
    b1.values = openings_by_day

    b2 = pyofc2.bar_stack()
    b2.colours = (BAR_COLOR_3, BAR_COLOR_4)
    b2.keys = [{'colour': BAR_COLOR_3, 'text':_('Unique click'), 'font-size': 13},
               {'colour': BAR_COLOR_4, 'text':_('Double clicks'), 'font-size': 13},]
    #b2.on_show = {'type': 'pop', 'cascade': 1, 'delay': 0.5 }
    b2.values = clicks_by_day


    title = pyofc2.title(text=_('Consultation histogram'),
                         style='{font-size: 16px; color: #666666; text-align: center; font-weight: bold;}')
    y = pyofc2.y_axis(min=0, max=max(total_openings) + 2,
                      steps=max(total_openings) / 5, colour=AXIS_COLOR,
                      grid_colour=GRID_COLOR)

    x = pyofc2.x_axis(colour=AXIS_COLOR,
                      grid_colour=GRID_COLOR, labels=pyofc2.x_axis_labels(
                          rotate=60, labels=labels))

    chart = pyofc2.open_flash_chart(title=title,
                                    bg_colour=BG_COLOR,
                                    x_axis=x, y_axis=y)
    chart.add_element(b1)
    if display_clicks:
        chart.add_element(b2)

    return HttpResponse(chart.render())
