from calendar import HTMLCalendar
from homepage.models import Event, CourseModel
from time import strptime


# title: HOW TO CREATE A CALENDAR USING DJANGO
# author: Hui Wen
# date: july 24, 2018
# code version: it was written in python, html, and css
# url: https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html
class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, week=None):
        self.year = year
        self.month = month
        self.week = week
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day)
        d = ''
        for event in events_per_day:
            d += f'<li> {event.title} </li>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal


class WeeklyTimeTable:
    def __init__(self, owner=None, is_owner=False):
        self.owner = owner;
        self.is_owner = is_owner

    def placeholder_modal(self):
        result = f'<div class="modal fade" id="detail" tabindex="-1"> \
        <div class="modal-dialog modal-dialog-centered"> \
        <div class="modal-content"> \
        <div class="modal-header" style="background-color:#FF7F50"> \
        <h1 class="modal-title fs-5" id="staticBackdropLabel">CS 1110-100 Laboratory 15150</h1> \
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button> \
        </div> \
        <div class="modal-body"> \
        <h6>Introduction to Programming</h6> \
        </div> \
        <div class="modal-footer"> \
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button> \
        </div></div></div></div>'
        return result

    def modals(self):
        all_modals = ""
        all_events = Event.objects.filter(owner=self.owner)
        corresponding_courses = set()
        for each in all_events:
            corresponding_courses.add(each.course)
        for course in corresponding_courses:
            modal = f'<div class="modal fade" id="detail-{course.id}" tabindex="-1"> \
            <div class="modal-dialog modal-dialog-centered"> \
            <div class="modal-content"> \
            <div class="modal-header" style="background-color:#FF7F50"> \
            <h1 class="modal-title fs-5">{course.course_acronym}-{course.course_sect} {course.course_type.upper()} {course.class_num}</h1> \
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button> \
            </div> \
            <div class="modal-body"> \
            <h6>{course.course_title}</h6> \
            <div class="detail-text">{course.course_instructor}</div> \
            <div class="detail-text">{course.credit} units</div>'
            if course.course_day_and_time:  # more than 1 meeting elements
                meetings = course.get_course_day_and_time_as_list()
                index = 0
                for meeting in meetings:
                    days = meeting.split(":")[0]
                    position_of_first_colon = meeting.index(':')
                    time = meeting[position_of_first_colon+1:]
                    modal += f'<div class="detail-text">{days} {time} \
                             @ {course.locations.split(";")[index]}</div>'
                    index += 1
            else:  # 1 meeting element
                modal += f'<div class="detail-text">{course.course_days} {course.course_time} \
                @ {course.location}</div>'
            modal += f'<div class="detail-text">{course.course_enrolled} enrolled</div>' \
                     f'<div class="detail-text">{course.course_waitlisted} waitlisted</div></div>'
            modal += f'<div class="modal-footer">  \
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button> \
                    </div></div></div></div>'
            all_modals += modal
        return all_modals

    def delete_modals(self):
        all_delete_warning_modals = ""
        all_events = Event.objects.filter(owner=self.owner)
        for event in all_events:
            modal = f'<div class="modal fade" id="delete-{event.id}" tabindex="-1"> \
            <div class="modal-dialog modal-dialog-centered"> \
            <div class="modal-content"> \
            <div class="modal-header" style="background-color:#FF7F50"> \
            <h1 class="modal-title fs-5">Delete</h1> \
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button> \
            </div> \
            <div class="modal-body"> \
            <div class="deletion-warning-text">Are you sure you want to delete all sections of this class from your schedule?</div> \
            </div> \
            <div class="modal-footer"> \
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button> \
            <a href="delete_event/{event.id}" class="btn btn-danger" role="button">Delete</a> \
            </div></div></div></div>'
            all_delete_warning_modals += modal
        return all_delete_warning_modals

    def Monday(self):
        opening_tag_for_5_days = '<div class="days">'
        opening_tag_for_monday = '<div class="day Mo">'
        monday_header = '<div class="date"><p class="date-day">Mon</p></div>'
        monday_events_opening_tag = '<div class="events">'
        monday_events_content = ''
        monday_events_closing_tag = '</div>'
        closing_tag_for_monday = '</div>'
        events = Event.objects.filter(owner=self.owner, day='Mo')
        for event in events:
            course = event.course
            start = event.start_time.strip()
            end = event.end_time.strip()
            print("end:", end)
            start_struct = to_time_struct_object(event.start_time_as_time_object)
            end_struct = to_time_struct_object(event.end_time_as_time_object)
            if is_not_ordinary_time(start_struct.tm_min):
                start = get_closest_class_name(event.start_time_as_time_object)
            if is_not_ordinary_time(end_struct.tm_min):
                end = get_closest_class_name(event.end_time_as_time_object)
                print("end as struct", event.end_time_as_time_object)
                print("end after modification:", end)
            start_no_colon = start.replace(":", "")
            end_no_colon = end.replace(":", "")
            corresponding_class_id = event.course.id
            monday_events_content += f'<div class="event start-{start_no_colon} end-{end_no_colon} green"' \
                                     f'data-bs-toggle="modal" data-bs-target="#detail-{corresponding_class_id}"' \
                                     f'id="event-card-{event.id}">'

            monday_events_content += f'<p class="title">{event.title}</p>'
            monday_events_content += f'<p class="others">{event.location}</p>'
            monday_events_content += f'<p class="others">{event.start_time.strip()}-{event.end_time.strip()}</p>'

            if self.is_owner:
                monday_events_content += f'<div class="delete">' \
                                         f'<a class="btn btn-sm" data-bs-toggle="modal"' \
                                         f'data-bs-target="#delete-{event.id}"' \
                                         f'role="button" id="trash-{event.id}">' \
                                         f'<i class="bi-trash" style="font-size: medium; opacity: 0.6"></i>' \
                                         f'</a></div>'
            monday_events_content += '</div>'

        result = opening_tag_for_5_days + opening_tag_for_monday + monday_header + monday_events_opening_tag + \
                 monday_events_content + monday_events_closing_tag + closing_tag_for_monday
        return result

    def Tuesday(self):
        opening_tag_for_tuesday = '<div class="day Tu"><div class="date"><p class="date-day">Tues</p></div>'
        tuesday_events_opening_tag = '<div class="events">'
        tuesday_events_content = ''
        events = Event.objects.filter(owner=self.owner, day='Tu')
        for event in events:
            start = event.start_time.strip()
            end = event.end_time.strip()
            start_struct = to_time_struct_object(event.start_time_as_time_object)
            end_struct = to_time_struct_object(event.end_time_as_time_object)
            if is_not_ordinary_time(start_struct.tm_min):
                start = get_closest_class_name(event.start_time_as_time_object)
            if is_not_ordinary_time(end_struct.tm_min):
                end = get_closest_class_name(event.end_time_as_time_object)
            start_no_colon = start.replace(":", "")
            end_no_colon = end.replace(":", "")
            corresponding_class_id = event.course.id
            tuesday_events_content += f'<div class="event start-{start_no_colon} end-{end_no_colon} green"' \
                                      f'data-bs-toggle="modal" data-bs-target="#detail-{corresponding_class_id}"' \
                                      f'id="event-card-{event.id}">'
            tuesday_events_content += f'<p class="title">{event.title}</p>'
            tuesday_events_content += f'<p class="others">{event.location}</p>'
            tuesday_events_content += f'<p class="others">{event.start_time.strip()} - {event.end_time.strip()}</p>'
            if self.is_owner:
                tuesday_events_content += f'<div class="delete">' \
                                         f'<a class="btn btn-sm" data-bs-toggle="modal"' \
                                         f'data-bs-target="#delete-{event.id}"' \
                                         f'role="button" id="trash-{event.id}">' \
                                         f'<i class="bi-trash" style="font-size: medium; opacity: 0.6"></i>' \
                                         f'</a></div>'
            tuesday_events_content += '</div>'
        tuesday_events_closing_tag = '</div>'
        closing_tag_for_tuesday = '</div>'
        result = opening_tag_for_tuesday + tuesday_events_opening_tag + tuesday_events_content + \
                 tuesday_events_closing_tag + closing_tag_for_tuesday
        return result

    def Wednesday(self):
        opening_tag_for_wednesday = '<div class="day We"><div class="date"><p class="date-day">Wed</p></div>'
        wednesday_events_opening_tag = '<div class="events">'
        wednesday_events_content = ''
        events = Event.objects.filter(owner=self.owner, day='We')
        for event in events:
            course = event.course
            start = event.start_time.strip()
            end = event.end_time.strip()
            start_struct = to_time_struct_object(event.start_time_as_time_object)
            end_struct = to_time_struct_object(event.end_time_as_time_object)
            if is_not_ordinary_time(start_struct.tm_min):
                start = get_closest_class_name(event.start_time_as_time_object)
            if is_not_ordinary_time(end_struct.tm_min):
                end = get_closest_class_name(event.end_time_as_time_object)
            start_no_colon = start.replace(":", "")
            end_no_colon = end.replace(":", "")
            corresponding_class_id = event.course.id
            wednesday_events_content += f'<div class="event start-{start_no_colon} end-{end_no_colon} green"' \
                                        f'data-bs-toggle="modal" data-bs-target="#detail-{corresponding_class_id}"' \
                                        f'id="event-card-{event.id}">'
            wednesday_events_content += f'<p class="title">{event.title}</p>'
            wednesday_events_content += f'<p class="others">{event.location}</p>'
            wednesday_events_content += f'<p class="others">{event.start_time.strip()} - {event.end_time.strip()}</p>'
            if self.is_owner:
                wednesday_events_content += f'<div class="delete">' \
                                         f'<a class="btn btn-sm" data-bs-toggle="modal"' \
                                         f'data-bs-target="#delete-{event.id}"' \
                                         f'role="button" id="trash-{event.id}">' \
                                         f'<i class="bi-trash" style="font-size: medium; opacity: 0.6"></i>' \
                                         f'</a></div>'
            wednesday_events_content += '</div>'
        closing_tags = '</div></div>'
        result = opening_tag_for_wednesday + wednesday_events_opening_tag + wednesday_events_content + closing_tags
        return result

    def Thursday(self):
        opening_tag_for_thursday = '<div class="day Th"><div class="date"><p class="date-day">Thurs</p></div>'
        thursday_events_opening_tag = '<div class="events">'
        thursday_events_content = ''
        events = Event.objects.filter(owner=self.owner, day='Th')
        for event in events:
            course = event.course
            start = event.start_time.strip()
            end = event.end_time.strip()
            start_struct = to_time_struct_object(event.start_time_as_time_object)
            end_struct = to_time_struct_object(event.end_time_as_time_object)
            if is_not_ordinary_time(start_struct.tm_min):
                start = get_closest_class_name(event.start_time_as_time_object)
            if is_not_ordinary_time(end_struct.tm_min):
                end = get_closest_class_name(event.end_time_as_time_object)
            start_no_colon = start.replace(":", "")
            end_no_colon = end.replace(":", "")
            corresponding_class_id = event.course.id
            thursday_events_content += f'<div class="event start-{start_no_colon} end-{end_no_colon} green"' \
                                       f'data-bs-toggle="modal" data-bs-target="#detail-{corresponding_class_id}"' \
                                       f'id="event-card-{event.id}">'
            thursday_events_content += f'<p class="title">{event.title}</p>'
            thursday_events_content += f'<p class="others">{event.location}</p>'
            thursday_events_content += f'<p class="others">{event.start_time.strip()} - {event.end_time.strip()}</p>'
            if self.is_owner:
                thursday_events_content += f'<div class="delete">' \
                                         f'<a class="btn btn-sm" data-bs-toggle="modal"' \
                                         f'data-bs-target="#delete-{event.id}"' \
                                         f'role="button" id="trash-{event.id}">' \
                                         f'<i class="bi-trash" style="font-size: medium; opacity: 0.6"></i>' \
                                         f'</a></div>'
            thursday_events_content += '</div>'
        closing_tags = '</div></div>'
        result = opening_tag_for_thursday + thursday_events_opening_tag + thursday_events_content + closing_tags
        return result

    def Friday(self):
        opening_tag_for_friday = '<div class="day Fr"><div class="date"><p class="date-day">Fri</p></div>'
        friday_events_opening_tag = '<div class="events">'
        friday_events_content = ''
        events = Event.objects.filter(owner=self.owner, day='Fr')
        for event in events:
            course = event.course
            start = event.start_time.strip()
            end = event.end_time.strip()
            start_struct = to_time_struct_object(event.start_time_as_time_object)
            end_struct = to_time_struct_object(event.end_time_as_time_object)
            if is_not_ordinary_time(start_struct.tm_min):
                start = get_closest_class_name(event.start_time_as_time_object)
            if is_not_ordinary_time(end_struct.tm_min):
                end = get_closest_class_name(event.end_time_as_time_object)
            start_no_colon = start.replace(":", "")
            end_no_colon = end.replace(":", "")
            corresponding_class_id = event.course.id
            friday_events_content += f'<div class="event start-{start_no_colon} end-{end_no_colon} green"' \
                                     f'data-bs-toggle="modal" data-bs-target="#detail-{corresponding_class_id}"' \
                                     f'id="event-card-{event.id}">'
            friday_events_content += f'<p class="title">{event.title}</p>'
            friday_events_content += f'<p class="others">{event.location}</p>'
            friday_events_content += f'<p class="others">{event.start_time.strip()} - {event.end_time.strip()}</p>'
            if self.is_owner:
                friday_events_content += f'<div class="delete">' \
                                         f'<a class="btn btn-sm" data-bs-toggle="modal"' \
                                         f'data-bs-target="#delete-{event.id}"' \
                                         f'role="button" id="trash-{event.id}">' \
                                         f'<i class="bi-trash" style="font-size: medium; opacity: 0.6"></i>' \
                                         f'</a></div>'
            friday_events_content += '</div>'
        closing_tags = '</div></div></div>'
        result = opening_tag_for_friday + friday_events_opening_tag + friday_events_content + closing_tags
        return result

    def opening_table_tags(self):  # time slots on left, 5 days on top
        return '<div class="calendar"><div class="timeline"><div class="spacer"></div>' \
               '<div class="spacer"></div><div class="spacer"></div>' \
               '<div>7 AM</div><div></div>' \
               '<div>7:30 AM</div><div></div>' \
               '<div>8 AM</div><div></div>' \
               '<div>8:30 AM</div><div></div>' \
               '<div>9 AM</div><div></div>' \
               '<div>9:30 AM</div><div></div>' \
               '<div>10 AM</div><div></div>' \
               '<div>10:30 AM</div><div></div>' \
               '<div>11 AM</div><div></div>' \
               '<div>11:30 AM</div><div></div>' \
               '<div>12 PM</div><div></div>' \
               '<div>12:30 PM</div><div></div>' \
               '<div>1 PM</div><div></div>' \
               '<div>1:30 PM</div><div></div>' \
               '<div>2 PM</div><div></div>' \
               '<div>2:30 PM</div><div></div>' \
               '<div>3 PM</div><div></div>' \
               '<div>3:30 PM</div><div></div>' \
               '<div>4 PM</div><div></div>' \
               '<div>4:30 PM</div><div></div>' \
               '<div>5 PM</div><div></div>' \
               '<div>5:30 PM</div><div></div><div>6 PM</div>' \
               '<div></div><div>6:30 PM</div>' \
               '<div></div><div>7 PM</div>' \
               '<div></div><div>7:30 PM</div>' \
               '<div></div><div>8 PM</div>' \
               '<div></div><div>8:30 PM</div>' \
               '<div></div><div>9 PM</div>' \
               '<div></div><div>9:30 PM</div>' \
               '<div></div><div>10 PM</div></div>'

    def ending_table_tag(self):  # the closing tag corresponding to the very 1st one (calendar)
        return '</div>'

    def output_entire_calendar(self):
        ls = [self.modals(), self.opening_table_tags(), self.Monday(),
                   self.Tuesday(), self.Wednesday(), self.Thursday(),
                   self.Friday(),
                   self.ending_table_tag()]
        if self.is_owner:
            ls.append(self.delete_modals())
        return ''.join(ls)


def to_time_struct_object(time_string):
    return strptime(time_string, "%H.%M.%S.000000%z")


def get_hour(time_object):
    return time_object.tm_hour


def get_minute(time_object):
    return time_object.tm_min


def is_not_ordinary_time(min):  # if start/end time is not at 0, 15, 30, or 45 minutes in an hour
    return min != 0 and min != 15 and min != 30 and min != 45


def get_closest_class_name(time_string):
    time_object = to_time_struct_object(time_string)
    hour = get_hour(time_object)
    minute = get_minute(time_object)
    class_name = ""
    if 0 <= hour < 10:
        class_name += "0" + str(hour) + ":"
        am_or_pm = "am"
    elif hour < 12:
        class_name += str(hour) + ":"
        am_or_pm = "am"
    elif hour == 12:
        class_name += str(hour) + ":"
        am_or_pm = "pm"
    else:
        class_name += str(hour - 12) + ":"
        am_or_pm = "pm"

    if 0 < minute < 8:
        class_name += "00" + am_or_pm
    elif 8 <= minute < 23:
        class_name += "15" + am_or_pm
    elif 23 <= minute < 38:
        class_name += "30" + am_or_pm
    elif 38 <= minute < 53:
        class_name += "45" + am_or_pm
    else:
        class_name += "00" + am_or_pm

    return class_name
