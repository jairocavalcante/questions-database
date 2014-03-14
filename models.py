
from google.appengine.ext import ndb
import qdb

class FavoriteList(ndb.Model):
	questions = ndb.KeyProperty(repeated=True)
	# ancestor: User


class User(ndb.Model):
	password = ndb.StringProperty(indexed=False)
	email = ndb.StringProperty(indexed=True)


class Question(ndb.Model):
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	content = ndb.KeyProperty()
	tags = ndb.StringProperty(repeated=True)
	subject = ndb.StringProperty(indexed=True)
	parent_ = ndb.KeyProperty()
	version = ndb.IntegerProperty(default=0)
	releasetag = ndb.StringProperty(default='HEAD', indexed=True)
	# user: ancestor


class Content(ndb.Model):
	text = ndb.TextProperty()
	# hashcode = ndb.StringProperty(indexed=True)
	# key: hashcode


def get_favorite_question_keys_by_user(user):
	userkey = ndb.Key(urlsafe=user.key)
	query = FavoriteList.query(ancestor=userkey)
	favlist = query.fetch()
	if favlist:
		return [key.urlsafe() for key in favlist[0].questions]
	else:
		return []


def get_favorite_questions_by_user(user):
	userkey = ndb.Key(urlsafe=user.key)
	query = FavoriteList.query(ancestor=userkey)
	favlist = query.fetch()
	if favlist:
		return [_question_from_model(key.get()) for key in favlist[0].questions]
	else:
		return []


def add_question_to_favorite_list(question, user):
	userkey = ndb.Key(urlsafe=user.key)
	query = FavoriteList.query(ancestor=userkey)
	favlist = query.fetch()
	if favlist:
		favlist = favlist[0]
		favlist.questions.append(ndb.Key(urlsafe=question.key))
	else:
		favlist = FavoriteList(parent=userkey)
		favlist.questions = [ndb.Key(urlsafe=question.key)]
	favlist.put()


def delete_question_from_favorite_list(question, user):
	userkey = ndb.Key(urlsafe=user.key)
	query = FavoriteList.query(ancestor=userkey)
	favlist = query.fetch()
	if favlist:
		favlist = favlist[0]
		try:
			idx = favlist.questions.index(ndb.Key(urlsafe=question.key))
			del favlist.questions[idx]
			favlist.put()
		except ValueError:
			pass

def get_user_by_username(username):
	user = ndb.Key('User', username).get()
	if user:
		return _user_from_model(user)
	else:
		return None

def get_user_by_key(key):
	userkey = ndb.Key(urlsafe=key)
	user = userkey.get()
	if user:
		return _user_from_model(user)
	else:
		return None

def check_username(username):
	userkey = ndb.Key('User', username)
	return userkey.get() is not None

def check_and_return_user(username, password):
	userkey = ndb.Key('User', username)
	user = userkey.get()
	if user and user.password == password:
		return _user_from_model(user)
	else:
		return None


class UserExistsException(Exception):
	pass


class EmailExistsException(Exception):
	pass


def delete_question(question):
	delete_question_by_key(question.key)


def delete_question_by_key(question_key):
	question_key = ndb.Key(urlsafe=question_key)
	question = question_key.get()
	delete_question_model(question)


def delete_question_model(question):
	question.releasetag = ''
	question.put()


def add_question(**kwargs):
	author = get_user_by_username(kwargs['author'])
	subject = kwargs['subject']
	tags = kwargs['tags']
	parent = kwargs.get('parent', None)
	_content = qdb.Content(kwargs['content'])
	content_key = ndb.Key('Content', _content.hash)
	content = content_key.get()
	if not content:
		content = Content(key=content_key, text=_content.text)
		content_key = content.put()
	author_key = ndb.Key(urlsafe=author.key)
	if parent:
		parent_key = ndb.Key(urlsafe=parent.key)
		parent = parent_key.get()
		if parent.key.parent() == author_key:
			version = parent.version + 1
			parent.releasetag = ''
			parent.put()
		else:
			version = 0
		question = Question(parent=author_key, content=content_key,
			version=version, parent_=parent.key)
	else:
		question = Question(parent=author_key, content=content_key)
	question.subject = subject
	question.tags = [tags]
	question.put()
	return _question_from_model(question)


def add_user(username, email, password):
	userkey = ndb.Key('User', username)
	user = userkey.get()
	if user:
		raise UserExistsException('login already exists')
	if User.query(User.email == email).count() > 0:
		raise EmailExistsException('email already exists')
	user = User(key=userkey, email=email, password=password)
	userkey = user.put()
	return _user_from_model(userkey.get())


def _user_from_model(user):
	_user = qdb.User(user.email, user.password)
	_user.login = user.key.id()
	_user.key = user.key.urlsafe()
	_user.favorites = get_favorite_question_keys_by_user(_user)
	return _user


def get_question_by_key(key):
	question_key = ndb.Key(urlsafe=key)
	return _question_from_model(question_key.get())


def get_questions_by_user(user):
	userkey = ndb.Key(urlsafe=user.key)
	query = Question.query(Question.releasetag == 'HEAD', ancestor=userkey).order(-Question.date_created)
	return [_question_from_model(q) for q in query.fetch()]


def get_recent_questions():
	query = Question.query(Question.releasetag == 'HEAD').order(-Question.date_created)
	return [_question_from_model(q) for q in query.fetch(10)]


def search_questions(q):
	query_content = Content.query(Content.text == q)
	query = Question.query(Question.releasetag == 'HEAD', Question.content.text).order(-Question.date_created)
	return [_question_from_model(q) for q in query.fetch()]

import markdown2

def _question_from_model(question):
	content = question.content.get().text
	# content = qdb.Content(content.text)
	author = question.key.parent().get()
	author = _user_from_model(author)
	_question = qdb.Question(question.date_created, content, author,
		subject=question.subject, tags=question.tags)
	_question.key = question.key.urlsafe()
	_question.html_content = markdown2.markdown(content)
	if question.tags:
		_question.str_tags = ', '.join(question.tags)
	else:
		_question.str_tags = ''
	return _question


