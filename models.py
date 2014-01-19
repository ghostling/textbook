from google.appengine.ext import ndb

class Book(ndb.Model):
    """represents a single book"""
    title = ndb.StringProperty(required=True)
    authors = ndb.StringProperty(required=True)
    isbn = ndb.StringProperty(required=True)
    image = ndb.StringProperty() # just be a link to an image for now?

class Course(ndb.Model):
    """a course with a list of textbooks for the course. title is something like
    Data Structures and Algorithms, name is EECS 281"""
    course = ndb.StringProperty(required=True)
    schoolname = ndb.StringProperty(required=True)
    textbooks = ndb.StructuredProperty(Book, repeated=True)

class UserBook(ndb.Model):
    price = ndb.FloatProperty()
    condition = ndb.StringProperty()
    sellerID = ndb.StringProperty()
    book = ndb.StructuredProperty(Book)

class Student(ndb.Model):
    """represents a user/student"""
    wishlist = ndb.StructuredProperty(Book, repeated=True)
    selling = ndb.StructuredProperty(UserBook, repeated=True)
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    schoolname = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
