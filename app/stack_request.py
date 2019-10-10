from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from auth import login_required
from db import get_db
import os 
from bokeh.plotting import figure
from bokeh.embed import components
from flask import current_app as app

ALLOWED_EXTENSIONS = {'txt', 'csv', 'dat','fits'}

bp = Blueprint('stack_request',__name__)

@bp.route('/')
def index():
    db = get_db()
    cur=db.cursor()
    cur.execute("SELECT s.id, title, filename, created, author_id, username  FROM stack_request s JOIN users u ON s.author_id=u.id  ORDER BY created DESC;")
    stack_requests_tuple=cur.fetchall()
    stack_requests=[]
    for stack_request in stack_requests_tuple:
    	stack_requests.append({'id':stack_request[0],'title':stack_request[1],'filename':stack_request[2],'created':stack_request[3],'author_id':stack_request[4],'username':stack_request[5]})
    
    return render_template('stack_request/index.html',stack_requests=stack_requests)

"""
@bp.route('/create',methods=('GET','POST'))
@login_required
def create():
	#Create a new post for the current user.
	if request.method == "POST":
		title = request.form["title"]
		filename = request.form["filename"]
		error = None
		if not title:
			error = 'Title is required.'
		if error is not None:
			flash(error)
		else:
			db = get_db()
			cur=db.cursor()
			cur.execute('INSERT INTO stack_requests (title, filename, author_id) VALUES (%s, %s, %s)',[title,filename, g.user['id']])
			db.commit()
			return redirect(url_for('stack_request.index'))
	return render_template('stack_request/create.html')
"""

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        title = request.form["title"]
        # if user does not select file, browser also
        # submit an empty part without filename
        #if file.filename == '':
        #    flash('No selected file')
        #    return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #import pdb;pdb.set_trace()
            save_dir=app.config['UPLOAD_FOLDER']+'/'+g.user['username']
            save_file=os.path.join(save_dir, filename)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            if os.path.exists(save_file):
                flash('File exists, change filename please.')	
                return redirect(request.url)
            else:
                file.save(save_file)
                db = get_db()
                cur=db.cursor()
                cur.execute('INSERT INTO stack_request (title, filename, author_id) VALUES (%s, %s, %s)',[title,filename, g.user['id']])
                db.commit()
                return redirect(url_for('stack_request.index'))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
       <label for="title">Title</label>
	   <input name="title" id="title" value="'''+g.user['username']+''' request" required>
       <input type=file name=file>
       <input type=submit value=Upload>
    </form>
    '''


def get_stack_request(id, check_author=True):
	db= get_db()
	cur=db.cursor()
	cur.execute('SELECT s.id, title, filename, created, author_id, username'
		                ' FROM stack_request s JOIN users u on s.author_id = u.id'
		                ' WHERE s.id = %s', (id,))
	stack_request_tuple=cur.fetchone()
	try:
		f=open(os.path.join(app.config['UPLOAD_FOLDER']+'/'+g.user['username'], stack_request_tuple[2]),"rU",newline='')
		file_content=f.read()
		f.close()
	except:
		file_content=''
	stack_request={'id':stack_request_tuple[0],'title':stack_request_tuple[1],'filename':stack_request_tuple[2],'created':stack_request_tuple[3],\
	'author_id':stack_request_tuple[4],'username':stack_request_tuple[5],'file_content':file_content}
	if stack_request is None:
		abort(404, "Stack Request {0} doesn't exist.".format(id))
	if check_author and stack_request['author_id'] != g.user['id']:
		abort(403)
	return stack_request


@bp.route('/<int:id>/update',methods=('GET','POST'))
@login_required
def update(id):
	stack_request = get_stack_request(id)
	print(stack_request)
	if request.method == 'POST':
		title = request.form['title']
		filename = request.form['filename']
		error = None

		if not title:
			error = 'Title is required.'
		if error is not None:
			flash(error)
		else:
			db = get_db()
			cur=db.cursor()
			cur.execute('UPDATE stack_requests SET title = %s, filename = %s'
				       ' WHERE id = %s', (title, filename, id))
			db.commit()
			return redirect(url_for('stack_request.index'))
	return render_template('stack_request/update.html', stack_request=stack_request)

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
	stack_request = get_stack_request(id)
	if request.method == 'POST':
		title = request.form['title']
		filename = request.form['filename']
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
	return render_template('stack_request/result.html', script=script, div=div)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
	get_stack_request(id)
	db = get_db()
	cur=db.cursor()
	cur.execute('DELETE FROM stack_request WHERE id = %s', (id,))
	db.commit()
	return redirect(url_for('stack_request.index'))

