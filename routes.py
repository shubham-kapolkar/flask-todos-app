
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Todo
from logger import Logger

todo_bp = Blueprint('todo', __name__)
log = Logger().get_logger()

@todo_bp.route('/')
def index():
    todos = Todo.query.all()
    log.info("Fetched all todos")
    return render_template('index.html', todos=todos)

@todo_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        if not title:
            flash('Title is required!', 'danger')
            return redirect(url_for('todo.add'))
        
        todo = Todo(title=title, description=description)
        db.session.add(todo)
        db.session.commit()
        log.info(f"Added todo: {title}")
        flash('Todo added!', 'success')
        return redirect(url_for('todo.index'))
    return render_template('add.html')

@todo_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    todo = Todo.query.get_or_404(id)
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        if not title:
            flash('Title is required!', 'danger')
            return redirect(url_for('todo.edit', id=id))
        
        todo.title = title
        todo.description = description
        db.session.commit()
        log.info(f"Updated todo ID {id}: {title}")
        flash('Todo updated!', 'success')
        return redirect(url_for('todo.index'))
    return render_template('edit.html', todo=todo)

@todo_bp.route('/toggle/<int:id>')
def toggle(id):
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    status = "completed" if todo.completed else "pending"
    log.info(f"Todo ID {id} marked as {status}")
    return redirect(url_for('todo.index'))

@todo_bp.route('/delete/<int:id>')
def delete(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    log.info(f"Deleted todo ID {id}: {todo.title}")
    flash('Todo deleted!', 'success')
    return redirect(url_for('todo.index'))


@todo_bp.route('/crash') # if 500 error handler is defined at bp level, otherwise fallbacks to the app level errorhandler
def crash():
    raise Exception("Test crash")


# 
@todo_bp.errorhandler(404)
def todo_not_found(e):
    flash("Todo not found!", "warning")
    return redirect(url_for("todo.index"))

'''
Catches:

abort(404) inside a todo route
Invalid todo ID in edit/delete
But does NOT catch /unknown-route
'''