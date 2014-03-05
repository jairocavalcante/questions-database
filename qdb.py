
import hashlib

class User(object):
	def __init__(self, email, password):
		self.name = None
		self.email = email
		self.login = None
		self.password = password
	
	def __str__(self):
		return str(self.__dict__)
	
	__repr__ = __str__
	
	def __eq__(self, other):
		return self.__dict__ == other.__dict__

class Question(object):        
	def __init__(self, date_created, content, user, tags=[], subject=None, parent=None):
		self._date_created = date_created
		self._content = content
		self._user = user
		self._tags = tags
		self._subject = subject
		self._parent = parent
	
	@property
	def date_created(self):
		return self._date_created
	
	@property
	def content(self):
		return self._content
	
	@property
	def user(self):
		return self._user
	
	@property
	def tags(self):
		return self._tags
		
	@property
	def subject(self):
		return self._subject
		
	@property
	def parent(self):
		return self._parent
	
	def copy(self, **kwargs):
		if kwargs.has_key('parent'):
			del(kwargs['parent'])
		attrs = {k.replace('_', '', 1): self.__dict__[k] for k in self.__dict__
			if k.startswith('_')}
		attrs.update(parent=self, **kwargs)
		question = Question(**attrs)
		return question
	
	def __str__(self):
		return str(self.__dict__)
	
	__repr__ = __str__
	
	def __eq__(self, other):
		return self.__dict__ == other.__dict__


class Questionnaire(object):
	def __init__(self, title, user):
		self.title = title
		self._user = user
		self.questions = []
	
	def add_question(self, question):
		self.questions.append(question)
	
	@property
	def user(self):
		return self._user
	
	def __len__(self):
		return len(self.questions)


class Content(object):
	def __init__(self, text):
		if text is None:
			raise TypeError('Invalid text provided to create the content.')
		self.text = self.to_unicode_or_bust(text)
		obj = hashlib.sha1(self.text.encode('utf-8'))
		self.hash = obj.hexdigest()
	
	def to_unicode_or_bust(self, obj, encoding='utf-8'):
		if isinstance(obj, basestring):
			if not isinstance(obj, unicode):
				obj = unicode(obj, encoding)
		return obj
	
	def __str__(self):
		return str((self.hash, self.text))
	
	__repr__ = __str__
	
	def __eq__(self, other):
		return self.hash == other.hash


class ContentFactory(object):
	def __init__(self):
		self.contents = {}
	
	def get_content(self, text):
		content = Content(text)
		if content.hash not in self.contents:
			self.contents[content.hash] = content
		else:
			content = self.contents[content.hash]
		return content
	
	def length(self):
		return len(self.contents)

