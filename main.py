import jinja2
import json
import logging
import os
import urllib2
import webapp2
import models as md
import logging

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

def render_str(template, **params):
    t = jinja_environment.get_template(template)
    return t.render(params)

def getBookInfoFromISBN(isbn):
    link = "https://www.googleapis.com/books/v1/volumes?q=%s" % isbn
    page = urllib2.urlopen(link).read()
    j = json.loads(page)
    title = j['items'][0]['volumeInfo']['title']
    authors = j['items'][0]['volumeInfo']['authors']
    return title, authors

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

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

    def get(post):
        course_title = self.request.get("coursename")
        course = md.course.query(md.course.title == course_title)
        context_obj = { 
            "books": https://github.com/ghostling/textbook.git,
            "title": course_title,
        }

        self.render('buy.html', context = context_obj)


class AddHandler(BaseHandler):
    def get(self):
        self.render('add.html')

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/sell', SellHandler),
    ('/buy', BuyHandler),
    ('/add', AddHandler),
    ('/login', LoginHandler)
    # (r'/signup/(\d+)', SignupHandler)
], debug=True)
