import jinja2
import hmac
import json
import logging
import os
import hashlib
import urllib2
import webapp2
import models as md
import logging

from secret import SECRET_KEY

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
        self.user = uid and Account.byID(int(uid))

class MainHandler(BaseHandler):
    def get(self):

        context_obj = {
        }

        self.render('index.html', context = context_obj)

    def post(self):
        pass

class SellHandler(BaseHandler):
    def get(self):
        self.render('sell.html')

class BuyHandler(BaseHandler):
    def get(self):

        self.render('buy.html')

    def post(self):
        course_title = self.request.get("coursename")
        course = md.Course.query(md.Course.title == course_title)

        # After querying for a specific course by its title, we can render the
        # page again with the new information.
        self.render('buy.html', book_list=course.textbooks)

        # TODO: On this page the course name was filled in, after searching,
        # we don't want to lose the query entered, so we should pass that back
        # into the page


class AddHandler(BaseHandler):
    def get(self):
        self.render('add.html')

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        email = self.request.get('email')
        pw = self.request.get('password')

        # Look up the student by email address and check the password hash
        # against inputted password.
        s = md.Student.query(md.Student.email == email)
        if validPW(s.name, pw, s.pw_hash):
            self.login(s)
        else:
            pass # TODO: bad login error handling

class SignupHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        # Get values from the signup form.
        name = self.request.get('name')
        email = self.request.get('email')
        pw = self.request.get('password')
        pw_confirm = self.request.get('pw_confirm')
        college = self.request.get('college')

        # TODO: verify name, email, college is not in DB
        # and is valid. verify passwords match

        # Create a new user and add to database.
        new_student = md.Student(name=name,
                                 email=email,
                                 pw_hash=makePWHash(name, pw),
                                 college=college)
        new_student.put()

        # A user is immediately logged in after signup.
        self.login(new_student)
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/sell', SellHandler),
    ('/buy', BuyHandler),
    ('/add', AddHandler),
    ('/login', LoginHandler),
    ('/signup', SignupHandler)
], debug=True)
