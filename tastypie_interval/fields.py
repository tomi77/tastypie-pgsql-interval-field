import re
from datetime import timedelta

from tastypie.exceptions import ApiFieldError
from tastypie.fields import ApiField


INTERVAL_REGEX = re.compile('^((?P<days>\d+) days, )?(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)$')


class IntervalField(ApiField):
    """
    An interval field.

    Covers ``interval.fields.IntervalField``.
    """
    dehydrated_type = 'timedelta'
    help_text = 'Time interval'

    def _parse(self, value):
        if isinstance(value, basestring):
            match = INTERVAL_REGEX.search(value)

            if match:
                data = match.groupdict()
                return timedelta(**dict((key, int(data[key] or 0)) for key in data))

        return value

    def convert(self, value):
        if value is None:
            return None

        if isinstance(value, basestring):
            match = INTERVAL_REGEX.search(value)

            if match:
                data = match.groupdict()
                value = timedelta(**dict((key, int(data[key] or 0)) for key in data))
            else:
                raise ApiFieldError("Timedelta provided to '%s' field doesn't appear to be a valid timedelta string: '%s'" % (self.instance_name, value))

        if isinstance(value, timedelta):
            hours, remainder = divmod(value.seconds, 3600)
            hours += value.days * 24
            minutes, seconds = divmod(remainder, 60)
            return '%02d:%02d:%02d' % (hours, minutes, seconds)

        return value

    def hydrate(self, bundle):
        value = super(IntervalField, self).hydrate(bundle)

        if value and not hasattr(value, 'days'):
            value = self._parse(value)

        return value
