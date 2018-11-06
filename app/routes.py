from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Game
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from random import choice
import json


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '': #To determine if the URL is relative or absolute
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/pastgame/')
@app.route('/pastgame/<game_id>')
@login_required
def pastgame(game_id=None):
    if game_id:
        try:
            game_board = Game.query.get(game_id)
            board = json.loads(game_board.board)
            board_val = game_board.result.split(',')
            found_val = game_board.found.split(',')
            ctx = {'board_val': board_val, 'board': board, 'found_val':found_val, 'score':game_board.score} 
            return render_template('game.html', ctx=ctx, pastgame="yes")       
        except:
            return redirect(url_for('index'))        	
    games = Game.query.filter_by(user_id=current_user.id)
    return render_template('game_list.html', games=games)


@app.route('/')
@app.route('/index/')
@login_required
def index(name=None):
    boggle = Boggle()
    tree = PrefixTree()
    load_tree(tree)
    found = set()
    boggle.play(tree, found)    	
    board_val = boggle.board
    # print(board_val)
    print(found)
    board_vals = list(found)
    ctx = {'board_val':board_vals, 'board':  json.dumps(board_val)}
    return render_template('game.html', ctx=ctx, pastgame="no")


@app.route('/answer-submit/', methods = ['POST'])
@login_required
def save_answer():
    if request.method == 'POST':
        try:
            posted_data = request.form.to_dict() 
            board = posted_data['boggle_board']
            found_list = ','.join(request.form.getlist('found_list[]'))
            words_list = ','.join(request.form.getlist('words_list[]'))
            score = posted_data['score']
            gh = Game(user_id=current_user.id, board=board, found=found_list, result=words_list,score=score)
            db.session.add(gh)
            db.session.commit()
            message = "Score saved."
            response = app.response_class(
            response=json.dumps(message),
            status=200,
            mimetype='application/json'
            )
        except:
            message = "Some error occurred. Sorry for the inconvineince"
            response = app.response_class(response=json.dumps(data),status=400,mimetype='application/json')	       
    return response
        # words_list = request.form.getlist('words_list[]')
        # score = request.form.get('score') 


class Boggle(object):
    def __init__(self, board=None):
        self.size = 4
        if board is None:
            self.board = []
            for i in range(0, self.size):
                self.board.append([])
                for j in range(0, self.size):
                    self.board[i].append(Boggle.random_letter())
        else:
            self.board = board
 
    @staticmethod
    def random_letter():
        freq = {'E': 5,
                'A': 3,
                'O': 3,
                'I': 3,
                'U': 2,
                'S': 2
                }
        choices = []
        for i in range(ord('A'), ord('Z')+1):
            if chr(i) in freq:
                choices += [chr(i)] * freq[chr(i)]
            else:
                choices.append(chr(i))
        return choice((choices))
 

    def play(self, tree, found):
        for rai in range(0, self.size):
            for cai in range(0, self.size):
                self.search_r(tree, found, rai, cai)
 
    def search_r(self, tree, found, row, col, path=None, node=None, word=None):
        letter = self.board[row][col]
        if node is None or path is None or word is None:
            node = tree.find_letter(letter)
            path = [(row, col)]
            word = letter
        else:
            node = node.find_letter(letter)
            path.append((row, col))
            word = word + letter
        if node is None:
            return
        elif node.stop:
            # if (len(word)>3):
            found.add(word)
        for ri in range(row - 1, row + 2):
            for ci in range(col - 1, col + 2):
                if (ri >= 0 and ri < self.size and ci >= 0 and ci < self.size  and not (ri == row and ci == col) and (ri, ci) not in path) :
                    self.search_r(tree, found, ri, ci, path[:], node, word[:])
 
    def __repr__(self):
        return "Boggle(size={0}, board={1})".format(self.size, self.board)


class PrefixTree(object):
    def __init__(self, letter=None):
        self.letter = letter
        self.children = {}
        self.stop = False
 
    def add(self, word):
        if len(word):
            letter = word[0]
            word = word[1:]
            if letter not in self.children:
                self.children[letter] = PrefixTree(letter);
            return self.children[letter].add(word)
        else:            
            self.stop = True
            return self
 
    def find_letter(self, letter):
        if letter not in self.children:
            return None
        return self.children[letter]
 
    # def __repr__(self):
    #     return "PrefixTree(letter={0}, stop={1})".format(self.letter, self.stop)


def load_tree(tree):
    with open('dictionary.txt') as f:
        for line in f: 
            word = line.rstrip().upper()
            tree.add(word)

