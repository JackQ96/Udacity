import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_paginate import Pagination, get_page_args
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# def pagination(request, selection):
#   page = request.args.get('page',1,type=int)
#   start = (page - 1) * QUESTIONS_PER_PAGE
#   end = start + QUESTIONS_PER_PAGE

#   questions = [question.format() for question in selection]
#   questions_current = questions[start:end]
#   return questions_current



def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"/api/*": {'origins': '*'}})




  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
     'Content-type, Authorization')
    response.headers.add('Access-COntrol-Allow-Methods', 
    'GET,POST,PATCH,DELETE,OPTIONS')
    return response


#   '''
#   @TODO: 
  # Create an endpoint to handle GET requests 
  # for all available categories.
  # '''

  @app.route('/categories')
  def get_categories():
    categories_format = {category.id: category.type for category in 
      Category.query.order_by(Category.id).all()}
    
  

    if len(categories_format) == 0:
     abort(404)

    

    return jsonify({
      'success': True,
      'categories': categories_format
    })

  

#   '''
#   @TODO: 
#   Create an endpoint to handle GET requests for questions, 
#   including pagination (every 10 questions). 
#   This endpoint should return a list of questions, 
#   number of total questions, current category, categories. 

  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    questions_format = [question.format() for question in questions]
    page = request.args.get('page', 1, type=int)
    start = (page-1) * 10
    end = start + 10
    categories_format = {category.id: category.type 
      for category in Category.query.order_by(Category.id).all()}
   

    if len(questions_format) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions_format[start:end],
      'categories': categories_format,
      'current_category': None,
      "total_questions": len(Question.query.all())
      })


#   TEST: At this point, when you start the application
#   you should see questions and categories generated,
#   ten questions per page and pagination at the bottom of the screen for three pages.
#   Clicking on the page numbers should update the questions. 
#   '''

#   '''
#   @TODO: 
#   Create an endpoint to DELETE question using a question ID. 


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)

    if question is None:
      abort(404)
    

    try:
      question.delete()
    except Exception as e:
      print(e)
      abort(422)


    else:
        return jsonify({
          'success': True,
          'deleted': question_id
        }),200


#   TEST: When you click the trash icon next to a question, the question will be removed.
#   This removal will persist in the database and when you refresh the page. 
#   '''

#   '''
#   @TODO: 
#   Create an endpoint to POST a new question, 
#   which will require the question and answer text, 
#   category, and difficulty score.

  @app.route('/add', methods=['POST'])
  def add_question():
    new_question = request.get_json()

    question = new_question.get('question')
    answer = new_question.get('answer')
    difficulty = new_question.get('difficulty')
    category = new_question.get('category')
      
    if ((question is None) or (answer is None) or (difficulty is None) or (category is None)):
      abort(422)
    

    try:

      add_question = Question(question = question, answer = answer,
        difficulty = difficulty, category = category)
      add_question.insert()

      return jsonify({
        'success': True,
        'question': add_question.format()
      })

    except:
      abort(422)
  



#   TEST: When you submit a question on the "Add" tab, 
#   the form will clear and the question will appear at the end of the last page
#   of the questions list in the "List" tab.  
#   '''

#   '''
#   @TODO: 
#   Create a POST endpoint to get questions based on a search term. 
#   It should return any questions for whom the search term 
#   is a substring of the question. 


  @app.route('/questions/search', methods = ['POST'])
  def search_question():

    page = request.args.get('page', 1, type=int)
    start = (page-1) * 10
    end = start + 10

    try:
      search_term = request.json.get('searchTerm', '')
      question_found = Question.query.filter(Question.question.ilike(
        f'%{search_term}%')).all()
      questions_format = [question.format() for question in question_found]

      

      return jsonify({
        'success': True,
        'questions': questions_format[start:end],
        'total_questions': len(question_found)
      })
    except:
      abort(422)






#   TEST: Search by any phrase. The questions list will update to include 
#   only question that include that string within their question. 
#   Try using the word "title" to start. 
#   '''

#   '''
#   @TODO: 
#   Create a GET endpoint to get questions based on category. 



  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_cat_question(category_id):
    questions = Question.query.filter_by(category=str(category_id)).all()
    questions_format = [question.format() for question in questions]

    page = request.args.get('page', 1, type=int)
    start = (page-1) * 10
    end = start + 10

    if len(questions_format) == 0:
      abort(404)


    return jsonify({
      'success': True,
      'questions': questions_format[start:end],
      "total_questions": len(Question.query.all())
      })

    







#   TEST: In the "List" tab / main screen, clicking on one of the 
#   categories in the left column will cause only questions of that 
#   category to be shown. 
#   '''


#   '''
#   @TODO: 
#   Create a POST endpoint to get questions to play the quiz. 
#   This endpoint should take category and previous question parameters 
#   and return a random questions within the given category, 
#   if provided, and that is not one of the previous questions. 


  @app.route('/quizzes', methods = ['POST'])
  def play_quiz():
    previous_questions = request.get_json().get('previous_questions',[])
    quiz_category = request.get_json().get('quiz_category', None)

    try:
      if quiz_category:
        if quiz_category['id'] == 0:
          quiz = Question.query.all()

        else:
          quiz = Question.query.filter_by(category = quiz_category['id']).all()
        
      if not quiz:
        return abort(422)

      data = []

      for question in quiz:
        if question.id not in previous_questions:
          data.append(question.format())
        
      if len(data) != 0:
        result = random.choice(data)
        return jsonify({
          'question': result
        })
      else:
        return jsonify({
          'question': False
        })
    
    except:
      abort(404)




#   TEST: In the "Play" tab, after a user selects "All" or a category,
#   one question at a time is displayed, the user is allowed to answer
#   and shown whether they were correct or not. 
#   '''

#   '''
#   @TODO: 
#   Create error handlers for all expected errors 
#   including 404 and 422. 
#   '''


  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Sorry not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "This is unprocessable"
        }), 422

  @app.errorhandler(500)
  def internal_server(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "The server does not know how to handle this"
        }), 500

  
  return app

    
