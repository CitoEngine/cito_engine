from .models import IncidentAuditLog


def incidentauditlog(incident, message, level='info'):
    try:
        IncidentAuditLog.objects.create(incident=incident, level=level, message=message)
    except Exception:
        pass