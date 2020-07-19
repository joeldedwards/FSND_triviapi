import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])

    def test_get_category_questions(self):
        res = self.client().get('/categories/6/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 6)

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_question(self):
        question = {
            'question': 'Who won the EPL in 2000?',
            'answer': 'Manchester United',
            'difficulty': 1,
            'category': 6
        }
        
        res = self.client().post('/add', json=question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_questions(self):
        res = self.client().delete('/questions/24')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 24).one_or_none()
        
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 24)
        
    def test_fail_delete_questions(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        
    def test_search_questions(self):
        res = self.client().post('/questions/search', json={"searchTerm":"play"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_quiz(self):
        res = self.client().post('/quizzes', json={
            "previous_questions": [], 
            "quiz_category": {
                "id": "1", 
                "type": "Science"
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['question'])

    def test_fail_quiz(self):
        res = self.client().post('/quizzes', json={
            "previous_questions": [], 
            "quiz_category": {
                "id": "10", "type": "Science"
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()