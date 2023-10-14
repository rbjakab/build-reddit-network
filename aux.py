import settings
from datetime import datetime
import pytz


def getUserSubreddits(redditor):
    comment_subs = set(
        [comment.subreddit.display_name for comment in redditor.comments.new(limit=settings.data["api_limit"])]
    )
    thread_subs = set(
        [thread.subreddit.display_name for thread in redditor.submissions.new(limit=settings.data["api_limit"])]
    )
    return comment_subs | thread_subs


def getUserThreads(redditor):
    return set(list(redditor.submissions.top(time_filter="all")))


def getCurrentTime():
    return datetime.now(pytz.timezone("Europe/London"))


def addElementToSetLimit(_set, element, set_size):
    _set.add(element)
    if len(_set) > set_size:
        _set.pop()


def limitSetSize(_set, set_size):
    if len(_set) < set_size:
        return _set
    return set(list(_set)[:set_size])
