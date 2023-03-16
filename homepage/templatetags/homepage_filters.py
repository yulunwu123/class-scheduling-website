# custom template filter
# 

#*Title: How to create custom template tags and filters
#*Author: Django
#*Date: 2005-2022
#*Code version: Written in python
#*URL: https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#writing-custom-template-filters
#*Software License: N/A
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)



