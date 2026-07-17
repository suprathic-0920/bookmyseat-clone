import re
from django import template

register = template.Library()

@register.filter(name='youtube_id')
def youtube_id(value):
    """
    Extracts the 11-character YouTube video ID from a given URL.
    Returns None if no valid ID is found. This strict parsing is crucial
    for preventing XSS vulnerabilities.
    """
    if not value:
        return None

    # Regex to match various YouTube URL formats and extract the 11-character ID.
    # Handles: youtu.be/<id>, youtube.com/watch?v=<id>, youtube.com/embed/<id>, etc.
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )

    youtube_regex_match = re.match(youtube_regex, value)
    if youtube_regex_match:
        video_id = youtube_regex_match.group(6)
        # Ensure the extracted ID is strictly 11 characters long
        if len(video_id) == 11:
            return video_id

    return None
