from django.template.defaulttags import register


@register.filter
def get_course_details(dictionary, key):
    return dictionary.get(key)