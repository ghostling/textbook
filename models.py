from google.appengine.ext import ndb

class Book(ndb.Model):
    title = ndb.StringProperty(required=True)
    authors = ndb.StringProperty(repeated=True)
    isbn = ndb.StringProperty(required=True)
    image = ndb.StringProperty() # just be a link to an image for now?
    orig_price = ndb.FloatProperty(required=True)

