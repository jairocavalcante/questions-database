# encoding: utf-8

from qdb import *

import hashlib
from datetime import datetime

import unittest
from unittest import TestCase

class TestUser(TestCase):
	def test_create_user(self):
		user = User('wilson.freitas@gmail.com', 'lalalala')
		self.assertEqual(user.name, None)
		self.assertEqual(user.email, 'wilson.freitas@gmail.com')
		self.assertEqual(user.login, None)
		self.assertEqual(user.password, 'lalalala')
	
	def test_compare_user(self):
		user1 = User('wilson.freitas@gmail.com', 'lalalala')
		user2 = User('wilson.freitas@gmail.com', 'lalalala')
		self.assertEqual(user1, user2)


class TestContent(TestCase):
	def setUp(self):
		self.text = 'question text goes here'
	
	def test_create_content(self):
		content = Content(self.text)
		self.assertEqual(content.text, self.text)
		digest = hashlib.sha1(self.text).hexdigest()
		self.assertEqual(content.hash, digest)
	
	def test_create_content_unicode(self):
		# with self.assertRaises(Exception):
		text = u'é verdade'
		print text.encoding()
		content = Content(text)
	
	def test_compare_content(self):
		content1 = Content(self.text)
		content2 = Content(self.text)
		self.assertEqual(content1, content2)


class TestContentFactory(TestCase):
	def setUp(self):
		self.text = 'question text goes here'
		self.text2 = 'question text goes there'
		self.factory = ContentFactory()
	
	def test_create_content(self):
		content = self.factory.get_content(self.text)
		self.assertEqual(content.text, self.text)
		digest = hashlib.sha1(self.text).hexdigest()
		self.assertEqual(content.hash, digest)
	
	def test_factory_length(self):
		self.assertEqual(self.factory.length(), 0)
		content = self.factory.get_content(self.text)
		self.assertEqual(self.factory.length(), 1)
		content = self.factory.get_content(self.text)
		self.assertEqual(self.factory.length(), 1)
		content = self.factory.get_content(self.text2)
		self.assertEqual(self.factory.length(), 2)
	
	def test_create_empty_content(self):
		content = self.factory.get_content('')
		content = self.factory.get_content('')
		self.assertEqual(self.factory.length(), 1)

	def test_create_none_content(self):
		with self.assertRaises(TypeError):
			content = self.factory.get_content(None)


class TestQuestion(TestCase):
	def setUp(self):
		self.user = User('wilson.freitas@gmail.com', 'lalalala')
		self.date_created = datetime.today()
		factory = ContentFactory()
		self.content = factory.get_content('text goes here')
	
	def test_create_question(self):
		question = Question(self.date_created, self.content, self.user)
		self.assertEqual(question.date_created, self.date_created)
		self.assertEqual(question.content, self.content)
		self.assertEqual(question.user, self.user)
		self.assertEqual(question.tags, [])
		self.assertEqual(question.subject, None)
		self.assertEqual(question.parent, None)
	
	def test_change_attributes(self):
		question = Question(self.date_created, self.content, self.user)
		with self.assertRaises(AttributeError):
			question.tags = ['primeiro ano']
		with self.assertRaises(AttributeError):
			question.subject = 'Math'
		with self.assertRaises(AttributeError):
			question.parent = None
		with self.assertRaises(AttributeError):
			question.date_created = self.date_created
		with self.assertRaises(AttributeError):
			question.content = self.content
		with self.assertRaises(AttributeError):
			question.user = self.user
	
	def test_question_compare(self):
		question1 = Question(self.date_created, self.content, self.user)
		question2 = Question(self.date_created, self.content, self.user)
		self.assertEqual(question1, question2)
		question2 = Question(self.date_created, self.content, self.user,
			tags=['math'])
		self.assertNotEqual(question1, question2)
	
	def test_question_copy(self):
		question1 = Question(self.date_created, self.content, self.user)
		user = User('wilson@gmail.com', 'lalalala')
		question2 = question1.copy(user=user)
		self.assertNotEqual(question1, question2)
		self.assertEqual(question1, question2.parent)
		question2 = question1.copy(user=user, parent=None)
		self.assertNotEqual(question1, question2)
		self.assertEqual(question1, question2.parent)
		question2 = question1.copy()
		self.assertNotEqual(question1, question2)
		self.assertEqual(question1, question2.parent)
		

class TestQuestionnaire(TestCase):
	def setUp(self):
		self.user = User('wilson.freitas@gmail.com', 'lalalala')
		self.date_created = datetime.today()
		factory = ContentFactory()
		self.content = factory.get_content('text goes here')
	
	def test_questionnaire_create(self):
		question1 = Question(self.date_created, self.content, self.user)
		user = User('wilson@gmail.com', 'lalalala')
		question2 = question1.copy(user=user)
		questionnaire = Questionnaire('title', user)
		questionnaire.add_question(question1)
		questionnaire.add_question(question2)
		self.assertEqual(len(questionnaire), 2)
		self.assertEqual(questionnaire.user, user)
		self.assertEqual(questionnaire.title, 'title')
		

# class TestListOfQuestions(TestCase):
# 	def test_create_list_of_questions(self):
# 		l = ListOfQuestions()
# 		self.assertEqual(len(l), 0)
	


if __name__ == '__main__':
	unittest.main()
	
