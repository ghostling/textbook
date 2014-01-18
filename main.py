import jinja2
import hmac
import json
import logging
import os
import hashlib
import random
import string
import urllib2
import webapp2
import models as md
import logging

from secret import SECRET_KEY
from colleges import COLLEGES

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

def render_str(template, **params):
    t = jinja_environment.get_template(template)
    return t.render(params)

def makeSecureVal(val):
    return '%s|%s' % (val, hmac.new(SECRET_KEY, str(val)).hexdigest())

def checkSecureVal(secureVal):
    val = secureVal.split('|')[0]
    if secureVal == makeSecureVal(val):
        return val

def makeSalt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def makePWHash(name, pw, salt=""):
    if not salt:
        salt = makeSalt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def validPW(name, password, h):
    salt = h.split(',')[1]
    return h == makePWHash(name, password, salt)

def getBookInfoFromISBN(isbn):
    link = "https://www.googleapis.com/books/v1/volumes?q=%s" % isbn
    page = urllib2.urlopen(link).read()
    j = json.loads(page)
    title = j['items'][0]['volumeInfo']['title']
    authors = j['items'][0]['volumeInfo']['authors']
    image = j['items'][0]['imageLinks']['thumbnail']
    return title, authors

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        """Allows rendering of templates followed by template_args."""
        kw['loggedin'] = self.user
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        """Simply writes some plain text to page/http response."""
        self.response.out.write(*a, **kw)

    def setSecureCookie(self, name, val):
        """Sets a secure cookie of a given name and value."""
        cookieVal = makeSecureVal(val)
        self.response.headers.add_header(
                'Set-Cookie',
                '%s=%s; Path=/' % (name, cookieVal))

    def readSecureCookie(self, name):
        """Checks if a cookie is authentic."""
        cookieVal = self.request.cookies.get(name)
        return cookieVal and checkSecureVal(cookieVal)

    def login(self, user):
        """Logging in basically sets a secure cookie for that user."""
        self.setSecureCookie('user_id', str(user.key.id()))

    def logout(self):
        """For logout we can simply get rid of the original cookie values."""
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        """Function called before each page handler's get(), so we can verify
        that the user is logged in before giving them more permissions."""
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.readSecureCookie('user_id')
        self.user = uid and md.Student.get_by_id(int(uid))

class MainHandler(BaseHandler):
    def get(self):
        if self.user:
            self.render('homestream.html')
        else:
            self.render('index.html')

    def post(self):
        pass

class SellHandler(BaseHandler):
    def get(self):
        self.render('sell.html')

    def post(self):

        title = self.request.get('title')
        authors = self.request.get('authors')
        isbn = self.request.get('isbn')
        image_url = self.request.get('image')

        book = md.Book(
            title=title,
            authors=authors,
            isbn=isbn,
            image=image_url,
        )

        #check if textbook belongs to any course
        parent_course = md.Course.query(md.Course.textbooks.IN(book))
        if parent_course:
            #belongs to at least 1
            student = md.Student.get_by_id(self.user)
            collection = md.Collection.query(md.Collection.book == book)
            if collection:
                collection.owner.append(student)
            else:
                collection = md.Collection(book=book, owner=[student])
                collection.put()

        #TO DO:
        #else:
            #doesn't belong to any, notify and prompt to add to a course

class BuyHandler(BaseHandler):
    def get(self):

        self.render('buy.html')

    def post(self):
        course_title = self.request.get("coursename")
        course = md.Course.query(md.Course.title == course_title).fetch(1)
        book_list = None
        collections = None
        if course:
            book_list = course.textbooks

            #find collections for da books
            for book in book_list:
                collection = md.Collection.query(md.Collection.book == book)
                collections.append

        # TODO: Just the course.textbooks is probably not what we want. We
        # need to use the Collection object somehow as that tells us if those
        # books are actually available...

        # After querying for a specific course by its title, we can render the
        # page again with the new information.
        self.render('buy.html', book_list=book_list, course=course_title,
            collections=collections)

class AddHandler(BaseHandler):
    def get(self):
        self.render('add.html')

class LoginHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        email = self.request.get('email')
        pw = self.request.get('password')

        # Look up the student by email address and check the password hash
        # against inputted password.
        s = md.Student.query(md.Student.email == email).fetch(1)[0]
        if s and validPW(s.name, pw, s.pw_hash):
            self.login(s)
            self.redirect('/')
        else:
            pass # TODO: bad login error handling

class LogoutHandler(BaseHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class SignupHandler(BaseHandler):
    def get(self, errors={}):
        pass

    def post(self):
        # Get values from the signup form.
        name = self.request.get('name')
        college = self.request.get('college')
        email = self.request.get('email')
        pw = self.request.get('password')
        pw_confirm = self.request.get('c-password')

        errors = {}

        #Verify that the e-mail is not in DB
        verify_email = md.Student.query(md.Student.email == email).fetch(1)
        if verify_email:
            errors['email_error'] = 'This e-mail is in already in use. Please use another e-mail address.'

# Checks to make sure the  e-mail address is valid.

    check_user_email = []

    for x in range(0,len(check_user_email)):
        check_user_email.append(email[x])

    at_found = False
    for items in check_user_email:
        if items == "@":
            at_found = True
            break

    dot_found = False
    for items in check_user_email:
        if items == ".":
            dot_found = True
            break

    if at_found and dot_found != True:
        errors['email_error'] = 'This address is invalid. Please use another e-mail address.'

        if pw != pw_confirm:
            errors['pw_error'] = 'Your passwords do not match!'

        if errors == {}:
            new_student = md.Student(name=name,
                                 email=email,
                                 pw_hash=makePWHash(name, pw),
                                 schoolname=college)
            new_student.put()
        else:
            self.redirect('/#signup')


        # A user is immediately logged in after signup.
        self.login(new_student)
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/sell', SellHandler),
    ('/buy', BuyHandler),
    ('/add', AddHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/signup', SignupHandler)
], debug=True)
