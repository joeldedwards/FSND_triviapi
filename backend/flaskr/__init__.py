import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, questions):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in questions]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  def get_category_list():
    categories = {}
    for category in Category.query.all():
        categories[category.id] = category.type
    return categories

  # CATEGORIES
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()

    return jsonify({
      'success': True,
      'categories': get_category_list(),
      'total_categories': len(Category.query.all())
    })

  @app.route('/categories/<int:category_id>/questions')
  def list_questions(category_id):
    questions = Question.query.filter_by(category=category_id).order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'current_category': category_id,
      'questions': current_questions,
      'total_questions': len(questions)
    })

  # QUESTIONS
  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'current_category': "None",
      'categories': get_category_list(),
      'questions': current_questions,
      'total_questions': len(Question.query.all())
    })

  # DELETE QUESTION
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      
      if question is None:
        abort(404)
        
      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id
      }), 200

    except:
      abort(422)

  # ADD QUESTION
  @app.route('/add', methods=['POST'])
  def create_question():
    body = request.get_json()

    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)
    question = body.get('question', None)

    try:
        question = Question(
          question = question,
          answer = answer, 
          category = category, 
          difficulty = difficulty
        )
        question.insert()

        return jsonify({
          'success': True,
          'created': question.id,
          'total_questions': len(Question.query.all())
        })
        
    except:
      abort(422)

  # SEARCH QUESTIONS
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()
    
    if body.get('searchTerm') is not None:
      search_term = body.get('searchTerm', '')
      search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      
      if search_results == []:
        abort(404)

      else:
        search_results = paginate_questions(request, search_results)

        return jsonify({
          'success': True,
          'questions': search_results,
          'total_questions': len(Question.query.all()),
          'current_category': "None"
        })
    else:
      abort(400)

  # PLAY QUIZ
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():

    try:
      category = request.get_json().get('quiz_category')

      if not category:
        abort(404)
      
      previous_questions = request.get_json().get('previous_questions')

      if category['id'] == 0:
        questions = Question.query.all()
      else:
        questions = Question.query.filter_by(category=category['id']).all()
      
      questions_list =  [question.format() for question in questions if question.id not in previous_questions]
      random_question = random.choice(questions_list)

      return jsonify({
        'question': random_question
      })

    except:
      abort(422)

  # ERROR HANDLERS
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "internal server error"
      }), 500
  
  return app