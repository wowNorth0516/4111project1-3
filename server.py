
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
import io
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response,url_for,send_from_directory,send_file
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from markupsafe import escape

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir,static_folder='static')


DATABASE_USERNAME = ""
DATABASE_PASSWRD = ""
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://yy3262:2893@{DATABASE_HOST}/project1"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass

# @app.route('/')
# def index():
#     select_query = "SELECT companyname from company"
#     cursor = g.conn.execute(text(select_query))

#     names = []
#     for result in cursor:
#         names.append(result[0])
#     cursor.close()

#     context = dict(data=names)

#     return render_template("index.html", **context)

    # querytest = "SELECT * from FinancialData"
    # result_proxy = g.conn.execute(querytest)
    # rows = result_proxy.fetchall()
    # columns = result_proxy.keys()
    # financialdata = pd.DataFrame(rows, columns=columns)
    # cursor.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/do_login', methods=['POST'])
def do_login():
    username = escape(request.form['username'])
    password = escape(request.form['password'])
    # Redirect to the success page
    return redirect(url_for('success', username=username))

@app.route('/success/<username>')
def success(username):
    select_query = "SELECT companyname from company"
    cursor = g.conn.execute(text(select_query))

    names = []
    for result in cursor:
        names.append(result[0])
    cursor.close()

    context = dict(data=names)
    return render_template('success.html', username=username, **context)


# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
	return render_template("another.html")


# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
# 	# accessing form inputs from user
# 	name = request.form['name']
	
# 	# passing params in for each variable into query
# 	params = {}
# 	params["new_name"] = name
# 	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
# 	g.conn.commit()
# 	return redirect('/')


@app.route('/login')
def login():
	abort(401)
	this_is_never_executed()


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=True, threaded=threaded)

run()
