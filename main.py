import webapp2
import jinja2
import os
import models as md

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

def render_str(template, **params):
    t = jinja_environment.get_template(template)
    return t.render(params)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class MainHandler(BaseHandler):
    def get(self):
        name = 'Bob'
        self.render('index.html', name=name)

    def post(self):
        pass

class BookHandler(BaseHandler):
    def get(self, book_id):
        self.write('Look up the book by id in DB and display stuff here')

class CourseHandler(BaseHandler):
    def get(self, course_id):
        self.write('Look up the course by id in DB and display stuff here')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    (r'/book/(\d+)', BookHandler),
    (r'/course/(\d+)', CourseHandler)
], debug=True)
