from allauth.account.forms import UserForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime, date
from django.utils.safestring import mark_safe
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, UserEditForm, CommentForm, ProfileForm
from .models import Profile, FriendRequest, Friend, CourseModel, Event, Comment
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.views import generic
import re
from time import strptime
from .utils import WeeklyTimeTable
from django.http import HttpResponseRedirect


class ScheduleView(generic.ListView):  # this class is no longer used
    model = Event
    template_name = 'homepage/schedule_builder.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calendar'] = mark_safe("test string")
        return context


def view_schedule(request, userID):
    try:
        schedule_owner = Profile.objects.get(user=User.objects.get(id=userID))
        # get comments associated with schedule
    except User.DoesNotExist:
        return HttpResponse("The user has not created a schedule yet.")
    events = Event.objects.filter(owner=schedule_owner)
    is_owner = request.user == User.objects.get(id=userID)
    html_weekly_timetable = WeeklyTimeTable(schedule_owner, is_owner)
    html_weekly_timetable = mark_safe(html_weekly_timetable.output_entire_calendar())
    comments = Comment.objects.filter(user=User.objects.get(id=userID))
    # new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.user = User.objects.get(id=userID)
            # Save the comment to the database
            new_comment.save()
            comment_form = CommentForm()

    else:
        comment_form = CommentForm()
    return render(request, 'homepage/schedule_builder.html',
                  {'calendar': html_weekly_timetable, 'events': events, 'comments': comments,
                   'comment_form': comment_form}  # add comments to render
                  )


@login_required()
def delete_event(request, eventID):
    current_profile = Profile.objects.get(user=request.user)
    event_selected = Event.objects.get(id=eventID)
    five_digit_num = event_selected.unique_num
    events = Event.objects.filter(unique_num=five_digit_num, owner=current_profile)
    events.delete()
    courses = CourseModel.objects.filter(class_num=five_digit_num, owner_profile=current_profile)
    courses.delete()
    return redirect("homepage:schedule_builder", userID=request.user.id)


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def friend_request(request, pk):
    sender = request.user
    recipient = Profile.objects.get(id=pk)
    model = FriendRequest.objects.get_or_create(sender=request.user, receivers=recipient)
    return render(request, 'homepage/friendslist.html')


def userpage(request):
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    return render(request=request, template_name="homepage/edit.html",
                  context={"user": request.user, "user_form": user_form, "profile_form": profile_form})


@login_required()
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profile updated successfully')
            # current_profile = Profile.objects.get(user=request.user)
            # courselist = CourseModel.objects.filter(profile_id=current_profile.id)
            # if len(courselist) == 0:  # initialize to NULL for conditional in html file for printing course table
            #     courselist = None
            return HttpResponseRedirect('dashboard')
        else:
            messages.error(request, 'Error in updating the profile')
            return render(request, 'homepage/edit.html', {'user_form': user_form})
    # if request.method:
    #     print("help")
    #     current_profile = Profile.objects.get(user=request.user)
    #     courselist = CourseModel.objects.filter(profile_id=current_profile.id)
    #     if len(courselist) == 0:  # initialize to NULL for conditional in html file for printing course table
    #         courselist = None
    #     return render(request, 'homepage/dashboard.html', {'section': 'dashboard', 'courselist': courselist})
    else:
        # user = request.user
        # current_profile = Profile.objects.get(user=user)
        # courselist = CourseModel.objects.filter(profile_id=current_profile.id)
        # if len(courselist) == 0:  # initialize to NULL for conditional in html file for printing course table
        #     courselist = None
        # return render(request, 'homepage/dashboard.html', {'section': 'dashboard', 'courselist': courselist})
        # print("hi")
        user_form = UserEditForm(instance=request.user)
        return render(request, 'homepage/edit.html', {'user_form': user_form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            email = user_form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is already in use')
            else:
                new_user = user_form.save(commit=False)
                new_user.set_password(user_form.cleaned_data['password'])
                new_user.save()
                return render(request, 'homepage/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'homepage/register.html', {'user_form': user_form})


@login_required
def dashboard(request):
    user = request.user
    current_profile = Profile.objects.get(user=user)
    courselist = CourseModel.objects.filter(owner_profile=current_profile)
    courselist_json = []
    if len(courselist) == 0:  # initialize to NULL for conditional in html file for printing course table
        courselist = None
    else:
        for each in courselist:
            courselist_dict = {"course_title": each.course_title, "course_acronym": each.course_acronym,
                               "class_num": each.class_num, "course_type": each.course_type,
                               "course_instructor": each.course_instructor}
            if each.course_day_and_time:
                courselist_dict["more_than_one_meeting"] = "yes"
                meeting_list = each.course_day_and_time.split(";")
                courselist_dict["meetings"] = meeting_list
                location_list = each.locations.split(";")
                courselist_dict["locations"] = location_list
            else:
                courselist_dict["course_days"] = each.course_days
                courselist_dict["course_time"] = each.course_time
                courselist_dict["location"] = each.location
            courselist_json.append(courselist_dict)
    return render(request, 'homepage/dashboard.html',
                  {'section': 'dashboard', 'courselist': courselist,
                   'courselist_json': courselist_json})  # , 'user':userID, 'actual_user': person})


def searchfriend(request):
    current_profile = Profile.objects.get(user=request.user)
    profiles_searched = []
    if request.method == "GET":
        search_query = request.GET['friendsearch']
        if len(search_query) > 0:
            # query any profile whose email/username/first/last name contains the search
            search_results_user_model = User.objects.filter(email__icontains=search_query) | \
                                        User.objects.filter(username__icontains=search_query) | \
                                        User.objects.filter(first_name__icontains=search_query) | \
                                        User.objects.filter(last_name__icontains=search_query)
            search_results = []
            for user in search_results_user_model:
                search_results.append(Profile.objects.get(user=user))

            friend_model, created = Friend.objects.get_or_create(current_user=current_profile)
            friends = friend_model.users.all()
            for profile in search_results:
                if len(friends) > 0:
                    is_friend = profile in friends
                else:
                    is_friend = False
                profiles_searched.append((profile, is_friend))
    return friendslist(request, profiles_searched)


def index(request):
    response = requests.get("http://luthers-list.herokuapp.com/api/deptlist/").json()
    result = []
    for x in range(0, len(response) - 15, 16):
        dict = {"first": response[x], "second": response[x + 1], "third": response[x + 2],
                "fourth": response[x + 3], "fifth": response[x + 4], "sixth": response[x + 5],
                "seventh": response[x + 6], "eighth": response[x + 7], "ninth": response[x + 8],
                "tenth": response[x + 9], "eleventh": response[x + 10], "twelve": response[x + 11],
                "thirteen": response[x + 12], "fourteen": response[x + 13], "fifteen": response[x + 14],
                "sixteen": response[x + 15]}
        result.append(dict)
    result.append({"first": response[len(response) - 1]})
    return render(request, 'homepage/index.html', {'response': result})


def department(request, department):
    response = requests.get("https://luthers-list.herokuapp.com/api/dept/" + department + "/").json()
    # changes the data so that all labs and lectures of the same class belong together
    modified_dict = {}
    # list of all classes' names
    class_names_list = []
    # all non-duplicated classes with subject, catalog_number, description, and subject+catalog_number (e.g. CS1110)
    all_classes = {}
    for each in response:
        class_name = department + " " + each["catalog_number"]  # e.g. CS 1110, thus can be duplicated
        meeting_day = ""  # used only when the class has 1 "meetings" element
        time = ""
        location = ""  # used only when the class has 1 "meetings" element
        start_time_struct = ""  # for classes with 1 meeting element
        end_time_struct = ""  # for classes with 1 meeting element
        start_time_structs = ""  # for classes with > 1 meeting element
        end_time_structs = ""  # for classes with > 1 meeting element
        locations = ""  # same as above
        each["meeting_day_and_time"] = ""  # used when the class has >1 meetings elements
        each['more_than_one_meeting'] = False
        if len(each["meetings"]) > 0:
            for meeting in each["meetings"]:
                meeting_day = meeting["days"]
                time = toFormat(meeting["start_time"]) + " - " + toFormat(meeting["end_time"])
                location = meeting["facility_description"]
                start_time_structs += meeting["start_time"] + ";"
                end_time_structs += meeting["end_time"] + ";"
                meeting["time"] = time
                each["meeting_day_and_time"] += meeting_day + ": " + time + ";"  # like "Mo: time;TuTh: time"
                start_time_struct = meeting["start_time"]
                end_time_struct = meeting["end_time"]
                locations += location + ";"
            if len(each["meetings"]) > 1:
                each['more_than_one_meeting'] = True
        each["meeting_day"] = meeting_day  # for classes with 1 meeting element
        each["meeting_time"] = time  # similar to ⬆️; these two key-value pairs are set for EACH bc form is outside
        each["location"] = location  # same as above
        each["start_time_struct"] = start_time_struct  # for classes with 1 meeting element
        each["end_time_struct"] = end_time_struct  # for classes with 1 meeting element
        each["start_time_structs"] = start_time_structs  # for classes with > 1 meeting element
        each["end_time_structs"] = end_time_structs  # for classes with > 1 meeting element
        locations = locations.strip(";")
        each["locations"] = locations
        # meeting's for-loop in html

        if class_name in class_names_list:
            modified_dict[class_name].append(each)
        else:
            class_names_list.append(class_name)
            modified_dict[class_name] = [each]
            all_classes[class_name] = each["description"]
    return render(request, 'homepage/department.html',
                  {'modified_dict': modified_dict, 'all_classes': all_classes,
                   'set_of_classes': class_names_list, 'department': department},
                  )


def search(request):
    response = requests.get("http://luthers-list.herokuapp.com/api/deptlist/").json()
    departments = []
    for cell in response:
        departments.append(cell['subject'])
    if request.method == "POST":
        dept_name = request.POST['searched'].upper().replace(' ', '')
        number = request.POST['searched2'].replace(' ', '')
        if dept_name in departments and not number:
            return department(request, dept_name)
        if dept_name in departments and number:
            response = requests.get("http://luthers-list.herokuapp.com/api/dept/" + dept_name + "/").json()
            # Find course name to make it easier to format html also checks validity of course number search
            course_name = ''
            day = ""
            time = ""
            location = ""  # used only when the class has 1 "meetings" element
            start_time_struct = ""  # for classes with 1 meeting element
            end_time_struct = ""  # for classes with 1 meeting element
            start_time_structs = ""  # for classes with > 1 meeting element
            end_time_structs = ""  # for classes with > 1 meeting element
            locations = ""  # same as above
            list_of_classes = []
            num_of_iteration = 0
            for i in response:
                if i['catalog_number'] == number:
                    i["meeting_day_and_time"] = ""  # for classes with >1 meeting elements
                    num_of_iteration += 1
                    if num_of_iteration == 1:  # this is just a safe approach in case that labs (which are assumed to
                        # be after lectures in the list) have a different name
                        course_name = i['description']
                    if len(i["meetings"]) > 0:
                        for meeting in i["meetings"]:
                            day = meeting["days"]
                            time = toFormat(meeting["start_time"]) + " - " + toFormat(meeting["end_time"])
                            meeting["time"] = time
                            location = meeting["facility_description"]
                            locations += location + ";"
                            i["meeting_day_and_time"] += day + ": " + time + ";"  # like "MoWe: time;TuTh: time"
                            start_time_struct = meeting["start_time"]
                            end_time_struct = meeting["end_time"]
                            start_time_structs += meeting["start_time"] + ";"
                            end_time_structs += meeting["end_time"] + ";"
                    i['more_than_one_meeting'] = len(i["meetings"]) > 1
                    i["meeting_day"] = day
                    i["meeting_time"] = time
                    i["location"] = location  # same as above
                    i["start_time_struct"] = start_time_struct  # for classes with 1 meeting element
                    i["end_time_struct"] = end_time_struct  # for classes with 1 meeting element
                    i["start_time_structs"] = start_time_structs  # for classes with > 1 meeting element
                    i["end_time_structs"] = end_time_structs  # for classes with > 1 meeting element
                    locations.strip(";")
                    i["locations"] = locations  # same as above
                    list_of_classes.append(i)
            if len(list_of_classes) != 0:
                return render(request, 'homepage/search.html',
                              {'searched': dept_name, 'searched2': number,
                               'list_of_classes': list_of_classes, "course_name": course_name})
            return render(request, 'homepage/search.html',
                          {'searched': dept_name, 'searched2': None, 'response': response})
        else:
            return render(request, 'homepage/search.html', {})
    else:
        return render(request, 'homepage/search.html', {})


class CustomLoginView(LoginView):
    authentication_form = LoginForm


def toFormat(time):
    if len(time) < 2:
        result = ""
    else:
        hour = time[:2]
        minute = time[3:5]
        if 0 <= int(hour) <= 11:
            result = hour + ":" + minute + "am"
        else:
            if int(hour) != 12:
                hour = int(hour) - 12
            else:
                hour = 12
            minute = time[3:5]
            result = str(hour) + ":" + minute + "pm"
    return result


@login_required()
def friendslist(request, profiles_searched="no search"):
    all_users = Profile.objects.all()
    current_profile = Profile.objects.get(user=request.user)
    friend_model, created = Friend.objects.get_or_create(current_user=current_profile)
    friends = friend_model.users.all()
    if len(friends) == 0:
        friends = None
    friend_requests_to_me = FriendRequest.objects.filter(receiver=current_profile)
    if len(friend_requests_to_me) == 0:
        friend_requests_to_me = None
    friend_requests_from_me = FriendRequest.objects.filter(sender=current_profile)
    if len(friend_requests_from_me) == 0:
        friend_requests_from_me = None
    is_search_input = False
    if profiles_searched != "no search":
        is_search_input = True
    return render(request, 'homepage/friendslist.html',
                  {'friends': friends, 'all_users': all_users,
                   'friend_requests_to_me': friend_requests_to_me, 'friend_requests_from_me': friend_requests_from_me,
                   "profiles_searched": profiles_searched, 'myself': current_profile,
                   'is_search_input': is_search_input})


@login_required
def send_friend_request(request, userID):
    from_profile = Profile.objects.get(user=request.user)
    to_profile = Profile.objects.get(id=userID)
    if from_profile.user == to_profile.user:  # make it so that you cannot friend yourself
        messages.info(request, 'You cannot send a request to yourself')
        # return HttpResponseRedirect('friendslist')
        return redirect('homepage:friendslist')
        # return HttpResponse('')
    friend_request, created = FriendRequest.objects.get_or_create(sender=from_profile, receiver=to_profile)
    if created:
        messages.info(request, 'You have sent a request to user')
        return redirect('homepage:friendslist')
        # return HttpResponseRedirect('friendslist')
        # return HttpResponse('')
    else:
        messages.info(request, 'Friend request was already sent!')
        return redirect('homepage:friendslist')
        # return HttpResponseRedirect('friendslist')
        # return HttpResponse(status=204)
        # return render(request, 'homepage/friendslist.html')


@login_required
def accept_friend_request(request, requestID):
    friend_request = FriendRequest.objects.get(id=requestID)
    from_profile = friend_request.sender
    current_profile = Profile.objects.get(user=request.user)
    if friend_request.receiver == current_profile:
        Friend.make_friend(current_profile, from_profile)
        Friend.make_friend(from_profile, current_profile)
        friend_request.delete()
        # TODO: create a pop-up message that says you've accepted the req from xxx, etc.
        messages.info(request, 'You have accepted their request!')
        return redirect('homepage:friendslist')
    else:  # don't think this else statement is ever executed? if so, delete this if-else structure
        return HttpResponse('friend request not accepted')


def cancel_friend_request(request, requestID):
    # TODO: pop-up message that asks whether the user is sure to cancel the request
    messages.info(request, 'You have canceled that request...')
    friend_request = FriendRequest.objects.get(id=requestID)
    friend_request.delete()
    return redirect('homepage:friendslist')


@login_required
def remove_friend(request, userID):
    friend_to_be_deleted = Profile.objects.get(id=userID)
    from_profile = Profile.objects.get(user=request.user)
    Friend.delete_friend(from_profile, friend_to_be_deleted)
    Friend.delete_friend(friend_to_be_deleted, from_profile)
    messages.info(request, 'You have deleted this user as a friend...')
    # TODO: add a message that pops up on top, telling you that you've deleted xxx
    #   if have time, can add a confirmation page asking whether user wants to delete (low priority)
    return redirect('homepage:friendslist')


def addToList(request):
    # get class info from <form input>
    print(request)
    class_number = request.POST['courseAddedToList']  # 5 digit code
    course_sect = request.POST['course_section_add']  # course_section like 001
    course_title = request.POST['course_title_add']  # Introduction to CS
    course_name = request.POST['course_name_add']  # CS 1110
    course_days = request.POST['course_days_add']
    location = request.POST['location']
    course_type = request.POST['course_type_add']
    course_time = request.POST['course_time_add']
    course_instructor = request.POST['course_instructor_add']
    course_enrolled = request.POST['course_enrolled_add']
    course_waitlisted = request.POST['course_waitlisted_add']
    more_than_one_meeting = request.POST['more_than_one_meeting']  # string variable
    meeting_day_and_time = request.POST['meeting_day_and_time'][:-1]  # strip the last ";"
    locations = request.POST['locations']
    start_time_struct_for_1_meeting = request.POST[
        'start_time_struct_for_1_meeting']  # for classes with 1 meeting element
    end_time_struct_for_1_meeting = request.POST['end_time_struct_for_1_meeting']  # for classes with 1 meeting element
    start_time_struct_for_more_1_meeting = request.POST["start_time_struct_for_more_1_meeting"][:-1]  # > 1 meeting
    end_time_struct_for_more_1_meeting = request.POST["end_time_struct_for_more_1_meeting"][:-1]  # > 1 meeting
    try:
        credit = int(request.POST['credit'])
    except:
        credit = 3
    list_of_day_time = []
    current_profile = Profile.objects.get(user=request.user)
    overlapped = False

    if more_than_one_meeting == "True":
        list_of_day_time = meeting_day_and_time.split(";")
        list_of_location = locations.split(";")
    valid_time = True
    if len(list_of_day_time) > 0:  # means course has more than one meeting element
        count = 0
        start_time_struct_for_more_1_meeting = start_time_struct_for_more_1_meeting.split(";")
        end_time_struct_for_more_1_meeting = end_time_struct_for_more_1_meeting.split(";")
        for day_time in list_of_day_time:  # number of meeting elements
            days = day_time.split(":")[0]  # days in each meeting element, e.g Mo or MoWe
            try:
                new_start_time = strptime(start_time_struct_for_more_1_meeting[count], "%H.%M.%S.000000%z")  # struct time
            except:
                valid_time = False
                new_start_time = start_time_struct_for_more_1_meeting[count]
            try:
                new_end_time = strptime(end_time_struct_for_more_1_meeting[count], "%H.%M.%S.000000%z")  # struct time
            except:
                valid_time = False
                new_end_time = end_time_struct_for_more_1_meeting[count]
            for day in split_days_into_list(days):  # for each day in each meeting element
                events = Event.objects.filter(day=day, owner=current_profile)
                if valid_time:
                    for event in events:
                        event_start_time = strptime(event.start_time_as_time_object, "%H.%M.%S.000000%z")
                        event_end_time = strptime(event.end_time_as_time_object, "%H.%M.%S.000000%z")
                        if check_overlap(event_start_time, event_end_time, new_start_time, new_end_time):
                            overlapped = True
                            return render(request, "homepage/overlap.html")
            count += 1
        num, created = CourseModel.objects.get_or_create(class_num=class_number, course_sect=course_sect,
                                                         course_title=course_title, \
                                                         course_acronym=course_name,
                                                         course_type=course_type, \
                                                         course_day_and_time=meeting_day_and_time,
                                                         course_instructor=course_instructor,
                                                         course_enrolled=course_enrolled,
                                                         locations=locations, \
                                                         course_waitlisted=course_waitlisted,
                                                         credit=credit,
                                                         owner_profile=current_profile)
        index = 0
        for day_time in list_of_day_time:
            days = day_time.split(":")[0]
            index_of_colon = day_time.index(":")
            start_time_str = day_time[index_of_colon + 2:].split(" - ")[0]  # e.g. 12:00pm
            end_time_str = day_time[index_of_colon + 2:].split(" - ")[1]  # e.g. 1:15pm
            start_time_as_time_object = start_time_struct_for_more_1_meeting[index]
            end_time_as_time_object = end_time_struct_for_more_1_meeting[index]
            for day in split_days_into_list(days):
                event, created = Event.objects.get_or_create(title=course_name, description=course_title,
                                                             day=day, start_time=start_time_str,
                                                             end_time=end_time_str,
                                                             start_time_as_time_object=
                                                             start_time_as_time_object,
                                                             end_time_as_time_object=
                                                             end_time_as_time_object, course=num,
                                                             location=list_of_location[index],
                                                             owner=current_profile, unique_num=class_number)
            index += 1

    else:  # for classes with only 1 meeting element
        # Create event but don't save it yet, use get request to see if it exists in database
        days = split_days_into_list(course_days)
        start_time, end_time = course_time.split(" - ")
        try:
            new_event_start_time = strptime(start_time_struct_for_1_meeting, "%H.%M.%S.000000%z")
        except:
            valid_time = False
            new_event_start_time = start_time_struct_for_1_meeting
        try:
            new_event_end_time = strptime(end_time_struct_for_1_meeting, "%H.%M.%S.000000%z")
        except:
            valid_time = False
            new_event_end_time = end_time_struct_for_1_meeting
        for day in days:
            events = Event.objects.filter(day=day, owner=current_profile)
            if valid_time:
                for event in events:
                    event_start_time = strptime(event.start_time_as_time_object, "%H.%M.%S.000000%z")
                    event_end_time = strptime(event.end_time_as_time_object, "%H.%M.%S.000000%z")
                    if check_overlap(event_start_time, event_end_time, new_event_start_time, new_event_end_time):
                        # messages.error(request,
                        # 'There is an overlap with another class, please modify your schedule in the schedule builder')
                        overlapped = True
                        return render(request, "homepage/overlap.html")
        if not overlapped:
            num, created = CourseModel.objects.get_or_create(class_num=class_number, course_sect=course_sect,
                                                             course_title=course_title, \
                                                             course_acronym=course_name, course_days=course_days,
                                                             course_type=course_type, \
                                                             course_time=course_time,
                                                             course_instructor=course_instructor,
                                                             course_enrolled=course_enrolled, \
                                                             course_waitlisted=course_waitlisted,
                                                             location=location,
                                                             credit=credit, owner_profile=current_profile
                                                             )
            for day in days:
                event, created = Event.objects.get_or_create(title=course_name, description=course_title,
                                                             day=day, start_time=start_time, end_time=end_time,
                                                             start_time_as_time_object=start_time_struct_for_1_meeting,
                                                             end_time_as_time_object=end_time_struct_for_1_meeting,
                                                             location=location,
                                                             owner=current_profile, unique_num=class_number, course=num)
    userID = request.user.id
    # if not overlapped:
    return redirect("homepage:schedule_builder", userID=userID)

    # counter = 0
    # for i in range(0, len(day_s), 2):
    #     char_1, char_2 = day_s[i], day_s[i + 1]
    #     day = char_1 + char_2
    #     eventy = Event(title=num.course_title, description=num.course_title, day=day, start_time=start_time,
    #                    end_time=stop_time)
    #     try:
    #         event_temp = Event.objects.get(day=day, start_time=start_time, end_time=stop_time)
    #         for i in range(0, len(day_s), 2):
    #             if counter == 0:
    #                 break
    #             char_1, char_2 = day_s[i], day_s[i + 1]
    #             day = char_1 + char_2
    #             event_instance = Event(title=num.course_title, description=num.course_title, day=day,
    #                                    start_time=start_time, end_time=stop_time)
    #             if event_temp == event_instance:
    #                 event_instance.delete()
    #                 break
    #             event_instance.delete()
    #         break
    #         pass
    #     except ObjectDoesNotExist:
    #         eventy.save()
    #         counter += 1


def showSchedule(request):
    return render(request, 'homepage/schedule.html')


# splits a string on uppercase letters, so that MoWeFr --> 3 days instead of 1
def split_days_into_list(days):
    my_list = re.findall('[a-zA-Z][^A-Z]*', days)
    return my_list


def check_overlap(fixed_start, fixed_end, new_start, new_end):
    overlap = False
    if new_start == fixed_end or new_end == fixed_start:  # edge case
        overlap = False
    elif (fixed_start <= new_start <= fixed_end) or \
            (fixed_start <= new_end <= fixed_end):  # inner limits
        overlap = True
    elif new_start <= fixed_start and new_end >= fixed_end:  # outer limits
        overlap = True
    return overlap
