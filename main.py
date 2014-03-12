# encoding: utf-8

import qdb
import datetime
import webapp2
import jinja2
import os
import models
import re

from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)
	

def match_route(template, text):
	return re.search(template, text) is not None


class MainHandler(webapp2.RequestHandler):
	def get(self):
		self.render_template()
	
	def dispatch(self):
		user = self.get_user()
		# userlogin = self.request.cookies.get('userlogin', None)
		if user:
			if match_route(self.request.route.template, '/') or \
				match_route(self.request.route.template, '/login') or \
				match_route(self.request.route.template, '/signup'):
				self.redirect_to_user_home(user)
			else:
				super(MainHandler, self).dispatch()
		else:
			if match_route(self.request.route.template, '/') or \
				match_route(self.request.route.template, '/login') or \
				match_route(self.request.route.template, '/signup'):
				super(MainHandler, self).dispatch()
			else:
				self.redirect('/')
	
	def redirect_to_user_home(self, user):
		self.redirect('/u/%s' % user.login)
	
	def redirect_to_user_questions(self, user):
		self.redirect('/q/%s' % user.login)
	
	def redirect_to_user_favorites(self, user):
		self.redirect('/s/%s' % user.login)
	
	def redirect_to_user_questionaires(self, user):
		self.redirect('/b/%s' % user.login)
	
	def get_user(self):
		userlogin = self.request.cookies.get('userlogin', None)
		if userlogin:
			user = models.get_user_by_username(userlogin)
			if not user:
				self.response.set_cookie('userlogin', '', max_age=0,
					overwrite=True)
			return user
		else:
			return None
	
	def default_template(self):
		return type(self).__name__.replace('Handler', '').lower()
	
	def render_template(self, *args, **variables):
		user = self.get_user()
		if user:
			variables.update(session_user=self.get_user())
		if len(args) > 0:
			template = args[0]
		else:
			template = self.default_template()
		jj = JINJA_ENVIRONMENT.get_template('%s.html' % template)
		self.response.write(jj.render(variables))


def startswithany(s, seq):
	return any([s.startswith(part) for part in seq])


class SearchHandler(MainHandler):
	def get(self):
		query = self.request.get('q')


class FavoriteHandler(MainHandler):
	def get(self, question_key):
		question = models.get_question_by_key(question_key)
		if question:
			models.add_question_to_favorite_list(question, self.get_user())
		self.redirect_to_user_favorites(self.get_user())


class ListFavoritesHandler(MainHandler):
	def get(self, username):
		user = models.get_user_by_username(username)
		if user:
			questions = models.get_favorite_questions_by_user(user)
			variables = {'user': user,
				'questions': questions }
			self.render_template(**variables)
		else:
			variables = { 'message': 'Usuário não encontrado'.decode('utf-8') }
			self.render_template('fail', **variables)


class QuestionHandler(MainHandler):
	def dispatch(self):
		if startswithany(self.request.path, ['/q/new', '/q/edit']):
			handler = EditQuestionHandler(self.request, self.response)
		elif startswithany(self.request.path, ['/q/delete']):
			handler = DeleteQuestionHandler(self.request, self.response)
		else:
			action = self.request.path.split('/')[2]
			if models.check_username(action):
				handler = ListQuestionsHandler(self.request, self.response)
			else:
				handler = ViewQuestionHandler(self.request, self.response)
		handler.dispatch()


class ListQuestionsHandler(MainHandler):
	def get(self, *args, **kwargs):
		username = args[0]
		user = models.get_user_by_username(username)
		if user:
			questions = models.get_questions_by_user(user)
			variables = {'user': user,
				'questions': questions }
			self.render_template(**variables)
		else:
			variables = { 'message': 'Usuário não encontrado'.decode('utf-8') }
			self.render_template('fail', **variables)


class ViewQuestionHandler(MainHandler):
	def get(self, question_id):
		question = models.get_question_by_key(question_id)
		self.render_template(question=question)


class DeleteQuestionHandler(MainHandler):
	def get(self, *args, **kwargs):
		if len(args[0].split('/')) == 2:
			questionkey = args[0].split('/')[1]
			models.delete_question_by_key(questionkey)
		self.redirect_to_user_questions(self.get_user())


class EditQuestionHandler(MainHandler):
	def get(self, *args, **kwargs):
		if len(args[0].split('/')) == 2:
			questionkey = args[0].split('/')[1]
			question = models.get_question_by_key(questionkey)
			self.render_template(question=question)
		else:
			self.render_template()
	
	def post(self, *args, **kwargs):
		questionkey = self.request.get('question', '')
		if questionkey:
			parent_question = models.get_question_by_key(questionkey)
			question = models.add_question(author=self.get_user().login,
				subject=self.request.get('subject'),
				tags=self.request.get('tags'),
				content=self.request.get('content'),
				parent=parent_question)
		else:
			question = models.add_question(author=self.get_user().login,
				subject=self.request.get('subject'),
				tags=self.request.get('tags'),
				content=self.request.get('content'))
		self.redirect_to_user_questions(self.get_user())


class HomeHandler(MainHandler):
	def get(self, username):
		user = models.get_user_by_username(username)
		if user:
			questions = models.get_recent_questions()
			variables = {'user': user,
				'questions': questions }
			self.render_template(**variables)
		else:
			variables = { 'message': 'Usuário não encontrado'.decode('utf-8') }
			self.render_template('fail', **variables)


class LoginHandler(MainHandler):
	def get(self):
		variables = {}
		message = self.request.get('m')
		if message:
			variables['message'] = message
		self.render_template(**variables)
	
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		user = models.check_and_return_user(username, password)
		if user:
			self.redirect_to_user_home(user)
			self.response.set_cookie('userlogin', user.login,
				max_age=10*365*24*60*60, overwrite=True)
		else:
			self.redirect('/login?m=Authentication Error')


class IndexHandler(MainHandler):
	pass

class LogoutHandler(MainHandler):
	def get(self):
		self.response.set_cookie('userlogin', '', max_age=0, overwrite=True)
		self.redirect('/')


class SignupHandler(MainHandler):
	def post(self):
		username = self.request.get('username')
		email = self.request.get('email')
		password = self.request.get('password')
		try:
			user = models.add_user(username, email, password)
			self.redirect_to_user_home(user)
			self.response.set_cookie('userlogin', user.login,
				max_age=10*365*24*60*60, overwrite=True)
		except models.UserExistsException:
			variables = {
				'message': 'usuário já existe'.decode('utf-8'),
				'username': username,
				'email': email
			}
			template = JINJA_ENVIRONMENT.get_template('signup.html')
			self.response.write(template.render(variables))
		except models.EmailExistsException:
			variables = {
				'message': 'email já existe'.decode('utf-8'),
				'username': username,
				'email': email
			}
			template = JINJA_ENVIRONMENT.get_template('signup.html')
			self.response.write(template.render(variables))


app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/signup', SignupHandler),
    ('/u/(.+)', HomeHandler),
    # ('/q/new', NewQuestionHandler),
    # ('/q/delete', DeleteQuestionHandler),
    ('/q/(.+)', QuestionHandler),
    ('/f/(.+)', FavoriteHandler),
    ('/s/(.+)', ListFavoritesHandler),
    ('/search', SearchHandler),
], debug=True)


