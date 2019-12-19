from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)

class TakeCourseForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    course_id = forms.CharField(label='course_id', max_length=100)

class DropCourseForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    course_id = forms.CharField(label='course_id', max_length=100)