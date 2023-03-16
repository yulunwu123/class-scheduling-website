# title: Django - getting user objects in tests
# date: october 23, 2012
# code: they wrote everything in python
# url: https://stackoverflow.com/questions/13034946/django-getting-user-objects-in-tests/13035268#13035268

# title: Python: Loop through JSON File
# date: january 3, 2017
# code: they wrote everything in python
# url: https://stackoverflow.com/questions/41445573/python-loop-through-json-file

from django.contrib.auth import authenticate
from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate
from homepage import views
from django.contrib.auth.models import User
from homepage import models
from homepage.models import Profile, CourseModel, FriendRequest
import json


#Create tests for google auth
# https://docs.djangoproject.com/en/4.1/topics/auth/default/
class testAuth(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='foo', email='test@gmail.com', password='bar')
        self.user2 = User.objects.create_user(username='foo1', email='test@gmai.com', password='bar')
        self.client = Client()
        self.user.save()
        self.user2.save()

    def test_checkpassword(self):
        self.assertEqual(self.user.check_password('bar'), True)

    def test_authentication(self):
        self.assertEqual(authenticate(username='foo', password='bar'), self.user)


    def test_checkvalid_email(self):
        email = self.user.email
        email = email[len(email)-10:]
        self.assertEqual(email, '@gmail.com')

    def test_checkinvalid_email(self):
        email = self.user2.email
        email = email[len(email)-10:]
        self.assertNotEqual(email, '@gmail.com')
    # Need to log in to existing user, test authentication


#Create tests for views.py methods
class testViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='foo', email='test@gmail.com', password='bar')
        self.client = Client()

    def test_profile_object_num(self):
        self.client.login(username='foo', password='bar')
        self.assertEquals(len(Profile.objects.all()), 1)
        self.client.logout()

    def test_correct_profile_made(self):
        self.client.login(username='foo', password='bar')
        self.assertEqual(Profile.objects.get(id=1).user, self.user)
    def test_courselistlength_nocourses(self):
        #Need to send request data
        #Create request data somehow,
        # request = '''# login to admin account maybe?
        # views.dashboard(request=request)
        self.client.login(username='foo',password='bar')
        current_profile = Profile.objects.get(id=1)
        courselist = CourseModel.objects.filter(profile_id=current_profile.id)
        self.assertEqual(len(courselist),0)
        return

    def test_friendreq_to_me(self): #sending friend, accept, cancel request, remove friends
        self.client.login(username='foo', password='bar')
        current_profile = Profile.objects.get(id=1)
        friend_requests_to_me = FriendRequest.objects.filter(receiver=current_profile)
        self.assertEqual(len(friend_requests_to_me),0)
        return
    def test_friendreq_from_me(self):
        self.client.login(username='foo', password='bar')
        current_profile = Profile.objects.get(id=1)
        friend_requests_from_me = FriendRequest.objects.filter(sender=current_profile)
        self.assertEqual(len(friend_requests_from_me),0)


# richard
class testOAuth(TestCase):

    def setUp(self):
        self.login_url = reverse('homepage:home')
        self.homepage_url = reverse('homepage:home')
        self.logout_url = reverse('homepage:logout')
        self.dashboard_url = reverse('homepage:dashboard')
        self.signup_url = reverse('homepage:register')
        self.edit_url = reverse('homepage:edit')
        self.login_url = reverse('homepage:login')
        self.schedule_url = reverse('homepage:show_schedule')
        self.friend_url = reverse('homepage:edit')
        self.addlist_url = reverse('homepage:dashboard')
        self.client = Client()
        # Create dummy user
        self.user = User.objects.create_user('foo', 'test@gmail.com', 'bar')
        self.user_uva_email = User.objects.create_user('dummy', 'random@virginia.edu', 'test')
        self.user_hotmail = User.objects.create_user('hotmail', 'user@hotmail.com','password')
        self.user_authenticate = User.objects.create_user('johnny', 'meila@email.com', 'pass')




class HTTP_Request_Test(testOAuth):
    def test_addlist_not_logged_in_request(self):
        response = self.client.get(self.addlist_url)
        self.assertEqual(response.status_code, 302)

    def test_addlist_logged_in_request(self):
        self.client.login(username='foo', password='bar')
        response = self.client.get(self.friend_url)
        self.assertEqual(response.status_code, 200)  # goes to actual page

    def test_addlist_login_logout_request(self):
        self.client.login(username='foo', password='bar')
        self.client.logout()
        response = self.client.get(self.friend_url)
        self.assertEqual(response.status_code, 302)  # redirects

    def test_friend_not_logged_in_request(self):
        response = self.client.get(self.friend_url)
        self.assertEqual(response.status_code, 302)


    def test_friend_logged_in_request(self):
        self.client.login(username='foo', password='bar')
        response = self.client.get(self.friend_url)
        self.assertEqual(response.status_code, 200)  # goes to actual page

    def test_friend_login_logout_request(self):
        self.client.login(username='foo', password='bar')
        self.client.logout()
        response = self.client.get(self.friend_url)
        self.assertEqual(response.status_code, 302)  # redirects

    def test_schedule_not_logged_in_request(self):
        response = self.client.get(self.schedule_url)
        self.assertEqual(response.status_code, 200)  # redirects to login page

    def test_schedule_logged_in_request(self):
        self.client.login(username='foo', password='bar')
        response = self.client.get(self.schedule_url)
        self.assertEqual(response.status_code, 200)  # goes to actual page

    def test_schedule_login_logout_request(self):
        self.client.login(username='foo', password='bar')
        self.client.logout()
        response = self.client.get(self.schedule_url)
        self.assertEqual(response.status_code, 200)  # redirects


    # Tests the homepage http request
    def test_homepage_http_request(self):
        response = self.client.get(self.homepage_url)
        self.assertEqual(response.status_code, 200)

    def test_login_http_request(self):
        user = authenticate(username = 'johnny', password = 'pass')
        login = self.client.login(username = 'johnny', password = 'pass')
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_logout_http_request(self):
        user = authenticate(username = 'johnny', password = 'pass')
        self.client.login(username = 'johnny', password = 'pass')
        self.client.logout()
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302) # HTTP code 302 is correct since its a redirect
    # Test change password page
    def test_changepass_not_logged_in_request(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302) #HTTP code 302 since dashboard cannot be accessed without login
    def test_change_with_logged_in_request(self):
        self.client.login(username = 'foo', password = 'bar')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200) # successful page land since login was true


    # Test log in page
    def test_login_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_login_already_loggedin_request(self):
        self.client.login(username='foo', password='bar')
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    # Test sign up page
    def test_signup_request(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)

    def test_signup_loggedin_request(self):
        self.client.login(username='foo', password='bar')
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)



    # Test Edit page
    def test_edit_not_logged_in_request(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302) # redirects
    def test_edit_logged_in_request(self):
        self.client.login(username = 'foo', password = 'bar')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)  # goes to actual page

    def test_edit_login_logout_request(self):
        self.client.login(username='foo', password='bar')
        self.client.logout()
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302) # redirects

    # Test Dashboard page
    def test_dashboard_not_logged_in_request(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302) #HTTP code 302 since dashboard cannot be accessed without login
    def test_dashboard_with_logged_in_request(self):
        self.client.login(username = 'foo', password = 'bar')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200) # successful page land since login was true

    def test_dashboard_stress_test_request(self):
        self.client.login(username = 'foo', password='bar')
        self.client.logout()
        self.client.login(username='foo', password='bar')
        self.client.logout()
        self.client.login(username = 'foo', password='bar')
        self.client.logout()
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)

    # TODO idk why this test doesnt work anymore i didnt change anything
    # Tests all department http requests
    def test_dept_list_http_request(self):
        with open('homepage/static/departments.json') as data_file:
            data = json.load(data_file)
            for v in data:
                dept_acronym = v['subject']
                dept_url = 'https://a4-hoos-list.herokuapp.com/department/' + dept_acronym
                response = self.client.get(dept_url)
                self.assertEqual(response.status_code, 200)



class UserCreateTest(testOAuth):
    # Check that all users have been created successfully
    def test_user_created(self):
        self.assertEqual(User.objects.count(), 4)
    # Test valid gmail
    def test_user_login(self):
        logged_in = self.client.login(username='foo', password='bar')
        self.assertEqual(logged_in, True)  # check login success
    # Test valid uva email
    def test_user_uva_email(self):
        logged_in = self.client.login(username = 'dummy', password = 'test')
        self.assertEqual(logged_in, True)  # check login success
    # Testing login on a non-existent user
    def test_failed_login(self):
        logged_in = self.client.login(username = 'failed', password = 'login')
        self.assertEqual(logged_in, False)

    def test_failed_oauth(self):
        user = authenticate(username = 'username', password = 'password')
        self.assertEqual(user, None)
    def test_passed_oauth(self):
        user = authenticate(username = 'johnny', password = 'pass')
        self.assertTrue(user.is_authenticated)
    def test_passed_login(self):
        login = self.client.login(username = 'johnny', password = 'pass')
        self.assertTrue(login)


