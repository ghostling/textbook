from google.appengine.ext import ndb

class Book(ndb.Model):
    """represents a single book"""
    title = ndb.StringProperty(required=True)
    authors = ndb.StringProperty(required=True)
    isbn = ndb.StringProperty(required=True)
    image = ndb.StringProperty() # just be a link to an image for now?
    price = ndb.FloatProperty()
    condition = ndb.StringProperty()

class Course(ndb.Model):
    """a course with a list of textbooks for the course. title is something like
    Data Structures and Algorithms, name is EECS 281"""
    course = ndb.StringProperty(required=True)
    schoolname = ndb.StringProperty(required=True)
    textbooks = ndb.StructuredProperty(Book, repeated=True)

class Student(ndb.Model):
    """represents a user/student"""
    wishlist = ndb.StructuredProperty(Book, repeated=True)
    selling = ndb.StructuredProperty(Book, repeated=True)
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    schoolname = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)

class Collection(ndb.Model):
    """represents all available books of a given title"""
    book = ndb.StructuredProperty(Book, repeated=False)
    owner = ndb.LocalStructuredProperty(Student, repeated=True)

class UserBook(ndb.Model):
    """a book owned by a student with ideal price and conidtion"""
    book = ndb.StructuredProperty(Book, repeated=False)
    conidition = ndb.StringProperty(required=True)
    price = ndb.FloatProperty()
