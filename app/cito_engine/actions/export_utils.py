import csv
from django.http import HttpResponse


def get_events_csv_formatter(data, filename='events.csv'):
    """
     An isolated method which exports events in csv.
    """
    field_names = ['id', 'team', 'severity', 'category', 'status', 'description', 'summary']
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    writer = csv.writer(response)
    if data:
        writer.writerow([unicode(fieldname) for fieldname in field_names])
    for record in data:
        writer.writerow([unicode(getattr(record, field)) for field in field_names])
    return response