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
    image = j['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    return {'title': title, 'authors': authors, 'isbn': isbn, 'image': image}

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
        s = self.user
        self.render('sell.html', selling=s.selling)

    def post(self):
        isbn = self.request.get('isbn')
        price = self.request.get('price')
        condition = self.request.get('condition')
        b = getBookInfoFromISBN(isbn)
        book = md.Book(title=b['title'],
                       authors=b['authors'][0],
                       isbn=b['isbn'],
                       image=b['image'])
        book.put()

        # Now we want to update the current user's selling list.
        if self.user.selling:
            self.user.selling.append(book)
        else:
            self.user.selling = [book]

        self.user.put()

        # And add this user into a collection where this book exists.
        c = md.Collection.query(md.Collection.book == book).fetch(1)

        if c:
            c[0].owner.append(self.user)
        else:
            c = md.Collection(book=book, owner=[self.user])
            c.put()

        self.redirect('/sell')

class BuyHandler(BaseHandler):
    def get(self):
        s = self.user
        self.render('buy.html', wishlist=s.wishlist)

    def post(self):
        course = self.request.get("course")
        course = md.Course.query(md.Course.course == course).fetch(1)
        collections = []
        if course:
            book_list = course[0].textbooks

            #find collections for da books
            for book in book_list:
                c = md.Collection.query(md.Collection.book == book)
                collections.append(c)

        self.render('buy.html', book_list=book_list, course=course[0].course,
            collections=collections)

class AddHandler(BaseHandler):
    def get(self):
        self.render('add.html')

    def makeBookHelper(self, b):
        book_dict = getBookInfoFromISBN(b)
        authors = " ".join(book_dict['authors'])
        book = md.Book(title=book_dict['title'], authors=authors,
                isbn=book_dict['isbn'], image=book_dict['image'])
        book.put()
        return book

    def post(self):
        school = self.request.get('school')
        course = self.request.get('course')
        book = self.request.get('book') # book can be a list of books or just one

        booklist = []

        if type(book) == type([]):
            for b in book:
                booklist.append(self.makeBookHelper(b))
        else:
            booklist.append(self.makeBookHelper(book))

        course = md.Course(course=course,
                schoolname=school,
                textbooks=booklist)
        course.put()
        self.render('add.html', success=True)

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

        if pw != pw_confirm:
            errors['pw_error'] = 'Your passwords do not match!'

        if errors == {}:
            new_student = md.Student(name=name,
                                 email=email,
                                 pw_hash=makePWHash(name, pw),
                                 schoolname=college)
            new_student.put()
        else:
            pass # TODO: should probably error check...

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
