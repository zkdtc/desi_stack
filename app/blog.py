from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from auth import login_required
from db import get_db
import os 
from bokeh.plotting import figure
from bokeh.embed import components
from datetime import datetime

bp = Blueprint('blog',__name__)

@bp.route('/')
def index():
    db = get_db()
    cur=db.cursor()
    cur.execute("SELECT p.id, title, body, created, author_id, username  FROM post p JOIN users u ON p.author_id=u.id  ORDER BY created DESC;")
    posts_tuple=cur.fetchall()
    posts=[]
    for post in posts_tuple:
    	posts.append({'id':post[0],'title':post[1],'body':post[2],'created':post[3],'author_id':post[4],'username':post[5]})
    
    return render_template('blog/index.html',posts=posts)

@bp.route('/create',methods=('GET','POST'))
@login_required
def create():
	#Create a new post for the current user.
	if request.method == "POST":
		title = request.form["title"]
		body = request.form["body"]
		error = None
		if not title:
			error = 'Title is required.'
		if error is not None:
			flash(error)
		else:
			db = get_db()
			cur=db.cursor()
			cur.execute('INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s)',[title,body, g.user['id']])
			db.commit()
			return redirect(url_for('blog.index'))
	return render_template('blog/create.html')


def get_post(id, check_author=True):
	db= get_db()
	cur=db.cursor()
	cur.execute('SELECT p.id, title, body, created, author_id, username'
		                ' FROM post p JOIN users u on p.author_id = u.id'
		                ' WHERE p.id = %s', (id,))
	post_tuple=cur.fetchone()
	post={'id':post_tuple[0],'title':post_tuple[1],'body':post_tuple[2],'created':post_tuple[3],\
	'author_id':post_tuple[4],'username':post_tuple[5]}
	
	if post is None:
		abort(404, "Post id {0} doesn't exist.".format(id))
	if check_author and post['author_id'] != g.user['id']:
		abort(403)
	return post


@bp.route('/<int:id>/update',methods=('GET','POST'))
@login_required
def update(id):
	post = get_post(id)
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None

		if not title:
			error = 'Title is required.'
		if error is not None:
			flash(error)
		else:
			db = get_db()
			cur=db.cursor()
			cur.execute('UPDATE post SET title = %s, body = %s'
				       ' WHERE id = %s', (title, body, id))
			db.commit()
			return redirect(url_for('blog.index'))
	return render_template('blog/update.html', post=post)

def create_figure(id):
	file_dir=''
	filename=file_dir+'desi_stack_'+str(id)+'.fits'
	p = figure(plot_width=400, plot_height=400)
	if os.path.exists(filename):
		if id ==2:
			x=[1,2,3,4,5,6,7,8,9,10]
			y=[1,1,1,1,2,3,4,5,6,7]
		else:
			x=[1,2,3,4,5,6,7,8,9,10]
			y=[1,1,1,1,1,1,1,5,1,1]
		# add a circle renderer with x and y coordinates, size, color, and alpha
		p.circle(x, y, size=15, line_color="navy", fill_color="orange", fill_alpha=0.5)
	else:
		p.circle([-2,15], [-5,5], size=15, line_color="navy", fill_color="orange", fill_alpha=0.5)
		from bokeh.models import Label
		mytext = Label(x=0, y=0, text='Your Stacked Spectrum is in progress!')
		p.add_layout(mytext)
		return p

@bp.route('/<int:id>/result',methods=('GET','POST'))
@login_required
def result(id):
	post = get_post(id)
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None

		if not title:
			error = 'Title is required.'
		if error is not None:
			flash(error)
		else:
			pass
	plot = create_figure(id)
	script, div = components(plot)
	#import pdb;pdb.set_trace()
	return render_template('blog/result.html', script=script, div=div)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
	get_post(id)
	db = get_db()
	cur=db.cursor()
	cur.execute('DELETE FROM post WHERE id = %s', (id,))
	db.commit()
	return redirect(url_for('blog.index'))

