#** Nunez, Priscilla
#** SI 364 F18
#** HW5


import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, TextAreaField, IntegerField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

#***************************
# Application configurations
#***************************
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'hard to guess string from si364'
#** Created a database 
#** Final Postgres database includes uniqname
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/nunezpHW5"
#** Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################
#** App setup ****
##################
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


#########################
#** Set up Models *******
#########################

#** All provided.

#** Association table
on_list = db.Table('on_list',db.Column('item_id',db.Integer, db.ForeignKey('items.id')),db.Column('list_id',db.Integer, db.ForeignKey('lists.id')))

class TodoList(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(225))
    items = db.relationship('TodoItem',secondary=on_list,backref=db.backref('lists',lazy='dynamic'),lazy='dynamic')

class TodoItem(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(225))
    priority = db.Column(db.Integer)


########################
#*** Set up Forms ******
########################

#** Provided - Form to create a todo list
class TodoListForm(FlaskForm):
    name = StringField("What is the title of this TODO List?", validators=[Required()])
    items = TextAreaField("Enter your TODO list items in the following format: Description, Priority -- separated by newlines")
    submit = SubmitField("Submit")

#** Defined an UpdateButtonForm class for use to update todo items
#** Defined a form class for updating the priority of a todolist item
class UpdateButtonForm(FlaskForm):
    priority = IntegerField("Enter The new priority for this todo item", validators=[Required()])
    submit = SubmitField("Update")

#** Defined a DeleteButtonForm class for use to delete.

class DeleteButtonForm(FlaskForm):
    submit = SubmitField("Delete")

################################
#*** Helper Functions **********
################################

#** Provided.
def get_or_create_item(item_string):
    elements = [x.strip().rstrip() for x in item_string.split(",")]
    item = TodoItem.query.filter_by(description=elements[0]).first()
    if item:
        return item
    else:
        item = TodoItem(description=elements[0],priority=elements[-1])
        db.session.add(item)
        db.session.commit()
        return item

def get_or_create_todolist(title, item_strings=[]):
    l = TodoList.query.filter_by(title=title).first()
    if not l:
        l = TodoList(title=title)
    for s in item_strings:
        item = get_or_create_item(s)
        l.items.append(item)
    db.session.add(l)
    db.session.commit()
    return l


###################################
#*** Routes & view functions ******
###################################

#** Provided
@app.route('/', methods=["GET","POST"])
def index():
    form = TodoListForm()
    if request.method=="POST":
        title = form.name.data
        items_data = form.items.data
        new_list = get_or_create_todolist(title, items_data.split("\n"))
        return redirect(url_for('all_lists'))
    return render_template('index.html',form=form)

#** Provided
@app.route('/all_lists',methods=["GET","POST"])
def all_lists():
    form = DeleteButtonForm()
    lsts = TodoList.query.all()
    return render_template('all_lists.html',todo_lists=lsts, form=form)

#** Updated the all_lists.html template and the all_lists view function such that there is a delete button available for each ToDoList saved.
#** By clicking on the delete button for each list, that list should get deleted.
#** Provided 
@app.route('/list/<ident>',methods=["GET","POST"])
def one_list(ident):
    form = UpdateButtonForm()
    lst = TodoList.query.filter_by(id=ident).first()
    items = lst.items.all()
    return render_template('list_tpl.html',todolist=lst,items=items,form=form)
#** Updated the one_list view function and the list_tpl.html view file so that there is an Update button next to each todolist item, and the priority integer of that item can be updated. 


#** Completes route to update an individual ToDo item's priority.
@app.route('/update/<item>',methods=["GET","POST"])
def update(item):
    form = UpdateButtonForm()
    if form.validate_on_submit():
        priority = form.priority.data
        todo = TodoItem.query.filter_by(id=item).first()
        todo.priority = priority
        db.session.commit()
        flash('Updated priority of {}'.format(todo.description))
        return redirect(url_for('all_lists'))

@app.route('/delete/<lst>',methods=["GET","POST"])
def delete(lst):
    form = DeleteButtonForm()
    todoList = TodoList.query.filter_by(id=lst).first()
    db.session.delete(todoList)
    db.session.commit()
    flash('Deleted list {}'.format(todoList.title))
    return redirect(url_for('all_lists'))

if __name__ == "__main__":
    db.create_all()
    manager.run()
