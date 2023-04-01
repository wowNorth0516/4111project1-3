
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
import base64
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response,url_for,send_from_directory,send_file,session
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from markupsafe import escape
import random
from collections import defaultdict

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


DATABASE_USERNAME = "yy3262"
DATABASE_PASSWRD = "2893"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"


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

@app.route("/")
def index():
    return render_template('login.html')

@app.route('/do_login', methods=['POST'])
def do_login():
    # get input values from form
    username = escape(request.form['username'])
    password = escape(request.form['password'])

    # check if user exists in database
    select_query = "SELECT * FROM Users WHERE UserID = :UserID"
    cursor = g.conn.execute(text(select_query), {'UserID': username})
    result = cursor.fetchone()
    cursor.close()

    if not result:
        # user does not exist, display error message
        error_msg = "Username does not exist, please sign up or enter a valid username."
        return render_template('login.html', error_msg=error_msg)

    # redirect to success page
    else:
        select_query = "SELECT * FROM Users WHERE UserID = :UserID AND UserPSW = :UserPSW"
        cursor = g.conn.execute(text(select_query), {'UserID': username,'UserPSW': password})
        result = cursor.fetchone()
        cursor.close()
        if not result:
			#inccorect password, display error message
            error_msg = "Incorrect password, please try again."
            return render_template('login.html', error_msg=error_msg)
        else:
            return redirect(url_for('search', username=username))


@app.route('/is_employee_check', methods=['GET', 'POST'])
def is_employee_check():
    if request.method == 'POST':
        is_employee = request.form['is_employee']
        if is_employee == 'Yes':
            return render_template('signup_employee.html')
        else:
            return render_template('signup.html')
    else:
        return render_template('is_employee_check.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = escape(request.form['username'])
        password = escape(request.form['password'])
        is_employee = escape(request.form.get('is_employee'))
        
        # Check if user already exists
        select_query = "SELECT * FROM Users WHERE UserID = :UserID"
        cursor = g.conn.execute(text(select_query), {'UserID': username})
        result = cursor.fetchone()
        cursor.close()
        if result:
            error_msg = "Username already exists, please log in or choose a different username."
            return render_template('login.html', error_msg=error_msg)
        
        if is_employee == 'Yes':
            EmployeeID = escape(request.form['EmployeeID'])
            select_query = "SELECT * FROM Employee WHERE EmployeeID = :EmployeeID"
            cursor = g.conn.execute(text(select_query), {'EmployeeID':EmployeeID})
            result = cursor.fetchone()
            cursor.close()
            if result:
                # Insert to staff table
                insert_query = "INSERT INTO Staff (UserID, EmployeeID) \
                                VALUES (:UserID, :EmployeeID)"
                g.conn.execute(text(insert_query), {'UserID': username,'EmployeeID':EmployeeID})
                return redirect(url_for('login'))
            else:
                error_msg = "Invalid employee ID, please check and try again."
                return render_template('signup_employee.html', error_msg=error_msg)
        else:
            Age = escape(request.form['Age'])
            Gender = escape(request.form['Gender'])
            DesiredPosition = escape(request.form['DesiredPosition'])
            DesiredSalary = escape(request.form['DesiredSalary'])
            # Generate random jobseeker ID
            JobSeekerID = 'JS' + str(random.randint(10000, 99999))
            # Insert to jobseeker table
            insert_query = "INSERT INTO JobSeeker (UserID, JobSeekerID, Age, gender, DesiredPosition, DesiredSalary) \
                            VALUES (:UserID, :JobSeekerID, :Age, :Gender, :DesiredPosition, :DesiredSalary)"
            g.conn.execute(text(insert_query), {'UserID':username, 'JobSeekerID':JobSeekerID, 'Age':Age, 'Gender':Gender, 
                            'DesiredPosition':DesiredPosition, 'DesiredSalary':DesiredSalary})
            # Insert to user table
            insert_query = "INSERT INTO Users (UserID, UserPSW) \
                            VALUES (:UserID, :password)"
            g.conn.execute(text(insert_query),{'UserID': username,'UserPSW': password})
            
            return redirect(url_for('login'))
        
    else:
        return render_template('signup.html')

# @app.route('/initial/<username>')
# def success(username):
#     select_query = "SELECT * from FinancialData"
#     cursorX = g.conn.execute(text(select_query))

#     # Retrieve the data from the cursor
#     data = cursorX.fetchall()

#     context = {'username': username, 'data': data}
#     return render_template('initial.html', **context)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    
    select_query = "SELECT * FROM company WHERE LOWER(companyname) LIKE :query"
    cursor = g.conn.execute(text(select_query), {'query': f"%{query.lower()}%"})
    companies = [{"ID": c.companyid, "NAME": c.companyname, "HEADQUARTER": c.headquarter, "FOUNDINGDATE": c.foundingdate} for c in cursor.fetchall()]
    cursor.close()

    return render_template('search_results.html', query=query, companies=companies)

@app.route('/company/<company_id>')
def company_data(company_id):
    # Fetch all the related data from the database using SQL JOIN statements
    query = """
        SELECT e.*, d.*, l.cityname, l.stateid
    FROM employee e
    JOIN department d ON e.departmentid = d.departmentid
    JOIN location l ON d.stateid = l.stateid AND d.cityname = l.cityname
    WHERE e.companyid = :company_id;
    """
    result = g.conn.execute(text(query), {'company_id': company_id})
    data = result.fetchall()

    # Close the database connection
    result.close()

    # Pass the data to the template for rendering
    return render_template('company_details.html', data=data)

# data = [{"Employee ID": c.employeeid, "Employee Name":c.employeename, "Gender":c.gender,
#              "City":c.city,"State":c.state, "Department Name":c.departmentname,
#              "Salary": c.salary, "Company Annual Revenue": c.annualrevenue} for c in data_temp.fetchall()]

@app.route('/filter_data', methods=['POST'])
def filter_data():
    filter_option_1 = request.form['filter-option-1']
    filter_option_2 = request.form['filter-option-2']
    company_id = request.form['company_id']
    if filter_option_1 is not None or filter_option_2 is not None:
        if filter_option_1 == 'Gender':
            query = """SELECT e.*, d.cityname, d.stateid,d.departmentname
                FROM employee e 
                Join department d
                on e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND gender = :filter_option_2"""
        elif filter_option_1 == 'Positions':
            query = """SELECT e.*, d.cityname, d.stateid,d.departmentname
                FROM employee e
                Join department d 
                on e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND currentposition = :filter_option_2"""
        elif filter_option_1 == 'Departments':
            query = """SELECT * 
                FROM employee e
                WHERE companyid = :company_id AND departmentname = :filter_option_2"""
        elif filter_option_1 == 'Financial Data':
            query = "SELECT * FROM financialdata WHERE companyid = :company_id AND years = :filter_option_2"
        filtered_data = g.conn.execute(text(query), {'company_id': company_id, 'filter_option_2': filter_option_2}).fetchall()
        select_query_1 = "SELECT * FROM company"
        cursor = g.conn.execute(text(select_query_1))
        companies = [{"id": c.companyid, "name": c.companyname} for c in cursor.fetchall()]
        cursor.close()
        select_query_2 = "SELECT DISTINCT d.departmentid, d.departmentname FROM department d JOIN employee e ON d.departmentid = e.departmentid WHERE e.companyid = :company_id"
        cursor = g.conn.execute(text(select_query_2), {'company_id': company_id})
        departments = [{"id": d.departmentid, "name": d.departmentname} for d in cursor.fetchall()]
        cursor.close()
        g.conn.close()
        return render_template('filtered_data.html', filtered_data=filtered_data, filter_option_1=filter_option_1, filter_option_2=filter_option_2, company_id=company_id, companies=companies, departments=departments)
    else:
        return redirect(url_for('company_details', company_id=company_id))

@app.route('/compare_data', methods=['POST'])
def compare_data():
    company_id_1 = request.form['company_id']
    company_id_2 = request.form['compare_with']
    filter_option_1 = request.form['filter_option_1']
    filter_option_2 = request.form['filter_option_2']

    # Fetch data for company 1 based on the filter options
    data_company_1 = fetch_filtered_data(company_id_1, filter_option_1, filter_option_2)

    # Fetch data for company 2 based on the filter options
    data_company_2 = fetch_filtered_data(company_id_2, filter_option_1, filter_option_2)

    return render_template('comparison.html', data_company_1=data_company_1, data_company_2=data_company_2, filter_option_1=filter_option_1, filter_option_2=filter_option_2)

def fetch_filtered_data(company_id, filter_option_1, filter_option_2):
    if filter_option_1 == 'Gender':
        query = "SELECT * FROM employee WHERE companyid = :company_id AND gender = :filter_option_2"
    elif filter_option_1 == 'Positions':
        query = "SELECT * FROM employee WHERE companyid = :company_id AND currentposition = :filter_option_2"
    elif filter_option_1 == 'Departments':
        query = "SELECT * FROM employee WHERE companyid = :company_id AND departmentname = :filter_option_2"
    elif filter_option_1 == 'Financial Data':
        query = "SELECT * FROM financialdata WHERE companyid = :company_id AND years = :filter_option_2"
    results = g.conn.execute(text(query), {'company_id': company_id, 'filter_option_2': filter_option_2}).fetchall()
    return results

def get_user_data(user_id, compare_option):
    if compare_option == 'salary':
        query = "SELECT salary FROM employee WHERE userid = %s"
    elif compare_option == 'age':
        query = "SELECT age FROM employee WHERE userid = %s"
    # Add more compare options here

    g.conn.execute(query, (user_id,))
    return g.conn.fetchone()

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
#



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
