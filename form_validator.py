import re
import os

"""
Form validation. Returns errors for a specific form as a list
"""


class BaseForm(object):

    def __init__(self):
        self._errors = []
        self._form_name = ""

    def add_error(self, message):
        self._errors.append(message)

    def get_errors(self):
        return self._errors

    def get_form_name(self):
        return self._form_name

    def validate(self):
        success = True
        if self._errors:
            success = False
        return success


class LoginForm(BaseForm):

    def __init__(self, username, password):
        BaseForm.__init__(self)
        self._username = username
        self._password = password
        self._form_name = "Login"

    def validate(self):
        regex = "^[a-zA-Z0-9_.-]+$"
        username_min = 1
        username_max = 15
        password_min = 6
        password_max = 20
        if not self._username:
            self._errors.append('Username field is required')
        if not self._password:
            self._errors.append('Password field is required')
        if not acceptable_chars(self._username, regex):
            self._errors.append('Username has invalid characters')
        if not acceptable_chars(self._password, regex):
            self._errors.append('Password has invalid characters')
        if not between_length(self._username, username_min, username_max):
            self._errors.append('Username must be between %s and %s characters long' % (username_min, username_max))
        if not between_length(self._password, password_min, password_max):
            self._errors.append('Password must be between %s and %s characters long' % (password_min, password_max))
        return self._errors


class RegisterForm(BaseForm):

    def __init__(self, username, password, verify_password):
        BaseForm.__init__(self)
        self._username = username
        self._password = password
        self._verify_password = verify_password
        self._form_name = "Register"

    def validate(self):
        regex = "^[a-zA-Z0-9_.-]+$"
        username_min = 1
        username_max = 15
        password_min = 6
        password_max = 20
        if not self._username:
            self._errors.append('Username field is required')
        if not self._password:
            self._errors.append('Password field is required')
        if not acceptable_chars(self._username, regex):
            self._errors.append('Username has invalid characters')
        if not acceptable_chars(self._password, regex):
            self._errors.append('Password has invalid characters')
        if not between_length(self._username, username_min, username_max):
            self._errors.append('Username must be between %s and %s characters long' % (username_min, username_max))
        if not between_length(self._password, password_min, password_max):
            self._errors.append('Password must be between %s and %s characters long' % (password_min, password_max))
        if self._verify_password != self._password:
            self._errors.append('Password field and verify password field do not match')
        return self._errors

class PostForm(BaseForm):

    def __init__(self, title, url, content):
        BaseForm.__init__(self)
        self._title = title
        self._url = url
        self._content = content
        self._form_name = "Post"

    def validate(self):
        title_min = 1
        title_max = 255
        content_max = 1000
        if not self._title:
            self._errors.append('Title field is required')
        if not between_length(self._title, title_min, title_max):
            self._errors.append('Title must be between %s and %s characters long' % (title_min, title_max))
        if not between_length(self._content, 0, content_max):
            self._errors.append('Content has exceeded maximum characters of %s' % (content_max))
        if self._url and not valid_url(self._url):
            self._errors.append('Invalid URL')
        return self._errors

def acceptable_chars(data, regex):
    """
    Validates the data against a provided regular expression
    """
    if re.match(regex, data):
        return True
    return False

def between_length(data, min_length, max_length):
    """
    Validates the data against the provided minimum and maximum length allowed
    """
    return min_length <= len(data) <= max_length

def valid_url(data):
    """
    Validates the data against valid URL strings
    """
    if re.match('(?:https?://|www.)[^"\' ]+', data):
        return True
    return False
