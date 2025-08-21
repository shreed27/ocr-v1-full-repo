from django import forms
from entity.models import Randomcode
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
    email=forms.EmailField(label = 'Email', max_length = 30,
                           widget = forms.TextInput(attrs = {'class':'box',
                                                             'title':'Enter Your Email'}))
    password1=forms.CharField(label = 'Password', max_length = 30,
                             widget = forms.PasswordInput(attrs = {'class':'box',
                                                             'title':'Enter Your Password'}))
    password2=forms.CharField(label = 'Password Confirm', max_length = 30,
                             widget = forms.PasswordInput(attrs = {'class':'box',
                                                                   'title':'Retype Your Password'}))
    invitecode = forms.CharField(label = 'Invite Code', max_length = 30,
                           widget = forms.TextInput(attrs = {'class':'box',
                                                             'title':'Enter Your Invitecode'}))
    username=forms.CharField(label = 'Username', max_length = 30,
                           widget = forms.TextInput(attrs = {'class':'box',
                                                             'title':'Enter Your Username'}))
    #groups=forms.ChoiceField(label = 'Groups', choices = (('teachers', 'Teacher'),))

    def clean_username(self):
        users = User.objects.filter(username__iexact = self.cleaned_data['username'])
        if not users:
            return self.cleaned_data['username']
        raise forms.ValidationError('Existed username!')

    def clean_email(self):
        emails = User.objects.filter(email__iexact = self.cleaned_data['email'])
        if not emails:
            return self.cleaned_data['email']
        raise forms.ValidationError('Existed email!')

    def clean_invitecode(self):
        invitecode = self.cleaned_data['invitecode']
        if invitecode:
            try:
                # Note: for testing purpose get unused code from entity_randomcode table
                randomcode = Randomcode.objects.get(randomcode = invitecode, used = False)
            except:
                raise forms.ValidationError('Incorrect Invitation Code!')
            else:
                return randomcode

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != '' and password2 !='':
            if password1 == password2:
                return password2
            else:
                raise forms.ValidationError('You must input same password!')
        else:
            raise forms.ValidationError('Password cannot be empty')

class LoginForm(forms.Form):
    username = forms.CharField(label = 'Username', max_length=30,
                           widget = forms.TextInput(attrs = {'class':'box',
                                                             'title':'Enter Your Username'}))
    password = forms.CharField(label = 'Password', max_length=30,
                              widget = forms.PasswordInput(attrs ={'class':'box',
                                                                   'title':'Enter Your Password'}))

class InfoModForm(forms.Form):
    username = forms.CharField(label = 'Username', max_length=30,
                           widget = forms.TextInput(attrs = {'class':'box',
                                                             'title':'Enter Your Username'}))
    newpassword = forms.CharField(label = 'Password',max_length=30,
                              widget = forms.PasswordInput(attrs ={'class':'box',
                                                                   'title':'Enter Your Password'}))
    newpasswordc = forms.CharField(label = 'Password Confirm',max_length=30,
                              widget = forms.PasswordInput(attrs ={'class':'box',
                                                                   'title':'Retype Your Password'}))
    email=forms.EmailField(label = 'Email', max_length = 30,
                           widget = forms.TextInput(attrs = {'class':'box',
                                                             'title':'Enter Your Email'}))

    def clean_username(self):
        users = User.objects.filter(username__iexact = self.cleaned_data['username'])
        if not users:
            raise forms.ValidationError('User %s not existed!'%self.cleaned_data['username'])
        else:
            return self.cleaned_data['username']

    def clean_newpasswordc(self):
        if self.cleaned_data['newpassword'] != '' and (self.cleaned_data['newpassword']== self.cleaned_data['newpasswordc']):
            return self.cleaned_data['newpasswordc']
        else:
            raise forms.ValidationError("Password can't be confirmed!")

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(label = 'Username',max_length=30,
                           widget = forms.TextInput(attrs = {'class':'box',
                                                             'title':'Enter Your Username'}))
    email=forms.EmailField(label = 'Email', max_length = 30,
                           widget = forms.TextInput(attrs = {'class':'box',
                                                             'title':'Enter Your Email'}))

    def clean_username(self):
        users = User.objects.filter(username__iexact = self.cleaned_data['username'])
        if not users:
            raise forms.ValidationError("User %s not existed!"%self.cleaned_data['username'])
        else:
            return self.cleaned_data['username']

    def clean_email(self):
        try:
            un=self.clean_username()
        except:
            raise forms.ValidationError("Invalid username")

        if self.cleaned_data['email'] == User.objects.get(username__exact=un).email:
            return self.cleaned_data['email']
        else:
            raise forms.ValidationError("Wrong email")
