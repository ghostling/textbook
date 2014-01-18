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
        book = md.Book(title="Book Title",
                authors=["Bob","Jim"],
                isbn="1234567890",
                image="http://placehold.it/350x150",
                orig_price=45.33)
        book.put()

        self.render('index.html')

    def post(self):
        pass

class SellHandler(BaseHandler):
    def get(self):
        self.render('sell.html')

class BuyHandler(BaseHandler):
    def get(self):
        self.render('buy.html')

class AddHandler(BaseHandler):
    def get(self):
        self.render('add.html')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/sell', SellHandler),
    ('/buy', BuyHandler),
    ('/add', AddHandler),
], debug=True)
