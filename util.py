from datetime import datetime

def format_date(date):
    """
    Return the difference between now and given datetime as a string
    """
    # Strip milliseconds
    date = datetime.strptime(date.split('.')[0], '%Y-%m-%d %H:%M:%S')
    # Obtain difference from passed date to now
    date_now = datetime.now()
    date_diff = date_now - date

    # Difference of under a day
    if date_diff.days == 0:
        if date_diff.seconds < 60:
            return "just now"
        if date_diff.seconds < 3600:
            return str(int(date_diff.seconds / 60)) + " minutes ago"
        if date_diff.seconds < 7200:
            return "an hour ago"
        if date_diff.seconds < 86400:
            return str(int(date_diff.seconds / 3600)) + " hours ago"

    # Different longer than a day
    if date_diff.days == 1:
        return "Yesterday"
    if date_diff.days < 7:
        return str(date_diff.days) + " days ago"
    if date_diff.days < 31:
        return str(int(date_diff.days / 7)) + " weeks ago"
    if date_diff.days < 365:
        return str(int(date_diff.days / 30)) + " months ago"
    return str(int(date_diff.days / 365)) + " years ago"