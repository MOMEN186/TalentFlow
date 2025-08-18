# api/reports/utils.py
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None

def default_range(end=None, days=30):
    end = end or timezone.localdate()
    start = end - timedelta(days=days)
    return start, end

def has_field(model, field_name):
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False

def find_first_field(model, candidates):
    """
    Return the first field name that exists on model from candidates,
    or None if none exist.
    """
    for c in candidates:
        if has_field(model, c):
            return c
    return None

def active_filter_for_date(model, as_of):
    """
    Return a Q filter representing "employed as of as_of" using
    commonly named fields (hire/date_joined + termination/termintion/left).
    """
    hire_field = find_first_field(model, ['hire_date', 'date_joined', 'joined_date'])
    term_field = find_first_field(model, ['termination_date', 'termintion_date', 'left_date', 'exit_date'])

    if hire_field and term_field:
        # employee hired on or before as_of and either has no termination or termination after as_of
        q = Q(**{f"{hire_field}__lte": as_of}) & (Q(**{f"{term_field}__isnull": True}) | Q(**{f"{term_field}__gt": as_of}))
        return q

    if hire_field and has_field(model, 'status'):
        # hired on/before and status active
        return Q(**{f"{hire_field}__lte": as_of}) & Q(status__iexact='active')

    if hire_field:
        return Q(**{f"{hire_field}__lte": as_of})

    # fallback: if status exists, use it
    if has_field(model, 'status'):
        return Q(status__iexact='active')

    return Q()
