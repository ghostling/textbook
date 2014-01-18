from google.appengine.ext import ndb

class book(ndb.Model):
	"""prepresents a single book"""
    title = ndb.StringProperty(required=True)
    authors = ndb.StringProperty(repeated=True)
    isbn = ndb.StringProperty(required=True)
    image = ndb.StringProperty() # just be a link to an image for now?
    orig_price = ndb.FloatProperty(required=True)

class course(ndb.Model):
	"""a course with a list of textbooks for the course. title is something like
			Data Structures and Algorithms, name is EECS 281"""
		title = ndb.StringProperty(required=True)
		name = ndb.StringPoporty(required=True)
		textbooks = ndb.StructuredProperty(book, repeated=True)

class collection(ndb.Model):
	"""represents all available books of a given title"""
		book = ndb.StructuredProperty(book, repeated=False)
		owner = ndb.StructuredProperty(student, repeated=True)

class student(ndb.Model):
	"""represents a user/student"""
		wishlist = ndb.StructuredProperty(book, repeated=True)
		selling = ndb.StructuredProperty(book, repeated=True)
		name = ndb.StringProperty(required=True)
