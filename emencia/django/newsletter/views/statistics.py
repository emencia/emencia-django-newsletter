"""Views for emencia.django.newsletter statistics"""
import pyofc2

from django.http import HttpResponse
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.statistics import get_newsletter_statistics


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
               'stats': get_newsletter_statistics(newsletter)}
    
    return render_to_response('newsletter/newsletter_statistics.html',
                              context, context_instance=RequestContext(request))

def view_newsletter_charts(request, slug):
    newsletter = get_object_or_404(Newsletter, slug=slug)

    post_sending_status = ContactMailingStatus.objects.filter(
        newsletter=newsletter, creation_date__gte=newsletter.sending_date)

    from datetime import timedelta
    from django.db.models import Q

    opening_by_day = []
    for date in post_sending_status.dates('creation_date', 'day'):
        opening_by_day.append(ContactMailingStatus.objects.filter(Q(status=ContactMailingStatus.OPENED) | Q(status=ContactMailingStatus.OPENED_ON_SITE),
                                                                  creation_date__gte=date,
                                                                  creation_date__lte=date + timedelta(days=1),
                                                                  newsletter=newsletter).count())
    
    b1 = pyofc2.bar()
    b1.values = opening_by_day#range(9,0,-1)
    b1.colour = '#5B80B2'
    
    chart = pyofc2.open_flash_chart()
    chart.title = pyofc2.title(text='Opening charts')
    chart.add_element(b1)
    
    y = pyofc2.y_axis()
    y.min, y.max, y.steps = 0, max(opening_by_day) + 25, 25
    chart.y_axis = y

    return HttpResponse(chart.render())
