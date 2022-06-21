#importing neccessary modules 

#from crypt import methods
import os
from flask import (Flask, request, jsonify, abort)

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

#importing random for random questions
import random


  
# importing our models
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Set up pagination

def paginate_questions(request, group):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in group]
    current_questions = questions[start:end]
    return current_questions


# main function to return the app instance
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # CORS(app, resources={r"*/api/*" : {"origins": '*'}})
    CORS(app)
   

    

    
    # Setting the after_request decorator to set Access-Control-Allow
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        
        return response    
    
    
    #Created an endpoint to handle GET requests
    #for all available categories.
    @app.route('/categories', methods=["GET"])
    def all_categories():
       group = Category.query.order_by(Category.id).all()
       current_categories = paginate_questions(request, group)

       if len(current_categories) == 0:
            abort(404)

       return jsonify({
            'success': True,
            'categories': {caty.id: caty.type for caty in group}
        })

    


    
    
    #Create an endpoint to handle GET requests for questions,
    #including pagination (every 10 questions).
    #This endpoint should return a list of questions,
    #number of total questions, current category, categories.

    #TEST: At this point, when you start the application
    #you should see questions and categories generated,
    #ten questions per page and pagination at the bottom of the screen for three pages.
    #Clicking on the page numbers should update the questions.
    
    @app.route('/questions')
    def all_questions():
        group = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, group)
          
        categories = Category.query.order_by(Category.id).all()  
        if len(current_questions) == 0:
            abort(404)    
            
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(group),
            'current_category': None,
            'categories': {caty.id: caty.type for caty  in categories },
        }), 200
       
    
    
    #Create an endpoint to DELETE question using a question ID.

    #TEST: When you click the trash icon next to a question, the question will be removed.
    #This removal will persist in the database and when you refresh the page.
    @app.route('/questions/<quest_id>', methods=['DELETE'])
    def delete_a_question(quest_id):
        try:
            question_ask = Question.query.filter(Question.id == quest_id).one_or_none()

            if question_ask is None:
                abort(404)

            else:
                question_ask.delete()
                group = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, group)
                return jsonify({
                'success': True,
                'deleted': quest_id,
                'questions': current_questions,
                'total_questions': len(group)
                })
        
        except Exception:
            abort(422)

    #Create an endpoint to POST a new question,
    #which will require the question and answer text,
    #category, and difficulty score.

    #TEST: When you submit a question on the "Add" tab,
    #the form will clear and the question will appear at the end of the last page
    #of the questions list in the  "List" tab.
    @app.route('/questions', methods=["POST"])
    def new_submit_question():
        body = request.get_json()

        question_new = body.get('question', None)
        answer_new = body.get('answer', None)
        category_new = body.get('category', None)
        difficulty_new = body.get('difficulty', None)
        search = body.get('searchTerm', None)
        try:
            if search:
                questions = Question.query.filter(Question.question.ilike(f'%{search}%')).all()

                current_questions = [quest.format() for quest in questions]
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(current_questions),
                })

            else:
                quests = Question(question=question_new,answer=answer_new,category=category_new,difficulty=difficulty_new)
                quests.insert()

                group = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, group)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
        except Exception:
            
            abort(422)
        
    

    
    
    #Create a POST endpoint to get questions based on a search term.
    #It should return any questions for whom the search term
    #is a substring of the question.

    #TEST: Search by any phrase. The questions list will update to include
    #only question that include that string within their question.
    #Try using the word "title" to start.
    
    #alternate search handler  
    """ @app.route('/question/search', methods=['POST'])
    def question_search():
        body = request.get_json()
        term_search = body.get('search_value', None)

        if term_search:
            results_search = Question.query.filter(Question.question.ilike(f'%{term_search}%')).all()

            return jsonify({
                'success': True,
                'questions': [quests.format() for quests in results_search],
                'total_questions': len(results_search),
                'current_category': []
            })
        else:
            abort(404)"""

    
    
    #Create a GET endpoint to get questions based on category.

    #TEST: In the "List" tab / main screen, clicking on one of the
    #categories in the left column will cause only questions of that
    #category to be shown.
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def all_questions_at_category(cat_id):
        
        category = Category.query.filter(Category.id == cat_id).first()

        group = Question.query.order_by(Question.id).filter(Question.category == cat_id).all()
        current_questions = paginate_questions(request,group)
        
        categories = Category.query.order_by(Category.id).all()  

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(group),
            'categories': {caty.id: caty.type for caty in categories},
            'current_category': cat_id
        })

 
    
    #Create a POST endpoint to get questions to play the quiz.
    #This endpoint should take category and previous question parameters
    #and return a random questions within the given category,
    #if provided, and that is not one of the previous questions.

    #TEST: In the "Play" tab, after a user selects "All" or a category,
    #one question at a time is displayed, the user is allowed to answer
    #and shown whether they were correct or not.
    
    @app.route('/quizzes', methods=["POST"])
    def start_game_quizzy():
       try:
            body = request.get_json()
            
            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)
            category_id = quiz_category['id']

            if category_id == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter( Question.id.notin_(previous_questions),Question.category == category_id).all()
            question = None
            if(questions):
                question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })

       except Exception:
            abort(422)
    
    
    #Create error handlers for all expected errors
    #including 404 and 422.
    
    
    # Resources not found
    @app.errorhandler(404)
    def not_found(error):
        return ( 
                jsonify({
            "success": False,
            "error": 404,
            "message": 'Resources not found'
        }), 404
        )
    # Cant be processed
    @app.errorhandler(422)
    def unprocessable(error):
        return ( 
              jsonify({
            "success": False,
            "error": 422,
            "message": "Can't be processed"
        }), 422
        )
    #Bad request
    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400
        )
        
    # Method not allowed
    @app.errorhandler(405)
    def bad_request(error):
        return  (
            jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 400
        )
        
    # return app instance
    return app

