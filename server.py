
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
import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'your-secret-key'

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
            session['username'] = username
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

@app.route('/signup/employee', methods=['GET', 'POST'])
def signup_employee():
    if request.method == 'POST':
        username = escape(request.form['username'])
        password = escape(request.form['password'])
        EmployeeID = escape(request.form['EmployeeID'])
        
        # Check if user already exists t
        user_exist_query = "SELECT * FROM Users WHERE UserID = :username"
        cursor = g.conn.execute(text(user_exist_query), {'username': username})
        user_exist = cursor.fetchone()
        cursor.close()
        if user_exist is not None:
            error_msg = "Username already exists, please log in or choose a different username."
            return render_template('login.html', error_msg=error_msg)
        else:
            select_query = "SELECT * FROM Employee WHERE EmployeeID = :EmployeeID"
            cursor = g.conn.execute(text(select_query), {'EmployeeID':EmployeeID})
            result = cursor.fetchone()
            cursor.close()
            if result:
                # Insert to user table
                insert_query = "INSERT INTO Users (UserID, UserPSW) \
                                VALUES (:username, :password)"
                g.conn.execute(text(insert_query),{'username': username,'password': password})
                g.conn.commit()
                 # Insert to staff table
                companyid_query = """
                    select companyid
                    from employee
                    where EmployeeID = :EmployeeID
                """
                cursor = g.conn.execute(text(companyid_query), {'EmployeeID':EmployeeID})
                companyid = cursor.fetchone()
                cursor.close()
                insert_query = "INSERT INTO Staff (UserID, EmployeeID, CompanyID) \
                                VALUES (:username, :EmployeeID,:companyid)"
                g.conn.execute(text(insert_query), {'username': username,'EmployeeID':EmployeeID, 'companyid':companyid[0]})
                g.conn.commit()
                return redirect(url_for('index'),code=302)
            else:
                error_msg = "Invalid employee ID, please check and try again."
                return render_template('signup_employee.html', error_msg=error_msg)
    else:
        return render_template('signup_employee.html')
        
@app.route('/signup/jobseeker', methods=['GET', 'POST'])
def signup_jobseeker():
    if request.method == 'POST':
        username = escape(request.form['username'])
        password = escape(request.form['password'])
        user_exist_query = "SELECT * FROM Users WHERE UserID = :username"
        cursor = g.conn.execute(text(user_exist_query), {'username': username})
        user_exist = cursor.fetchone()
        if user_exist is not None:
            error_msg = "Username already exists, please log in or choose a different username."
            return render_template('login.html', error_msg=error_msg)
        else:
            Age = int(request.form['Age'])
            Gender = escape(request.form['Gender'])
            DesiredPosition = int(request.form['DesiredPosition'])
            DesiredSalary = int(request.form['DesiredSalary'])
            if Age is not int:
                error_msg ="Check your enter of Age"
                return render_template('signup.html', error_msg=error_msg)
            elif Gender.capitalize() not in ('Female','Male'):
                error_msg ="Check your enter of Gender"
                return render_template('signup.html', error_msg=error_msg)
            elif DesiredPosition is not str:
                error_msg ="Check your enter of Desired Position"
                return render_template('signup.html', error_msg=error_msg)
            elif DesiredSalary is not int:
                error_msg ="Check your enter of Desired Salary"
                return render_template('signup.html', error_msg=error_msg)
            else:
                # Generate random jobseeker ID
                JobSeekerID = 'JS' + str(random.randint(10000, 99999))
                # Insert to user table
                insert_query = "INSERT INTO Users (UserID, UserPSW) \
                                VALUES (:username, :password)"
                g.conn.execute(text(insert_query),{'username': username,'password': password})
                g.conn.commit()
                # Insert to jobseeker table
                insert_query = "INSERT INTO JobSeeker (UserID, JobSeekerID, Age, gender, DesiredPosition, DesiredSalary) \
                                VALUES (:username, :JobSeekerID, :Age, :Gender, :DesiredPosition, :DesiredSalary)"
                g.conn.execute(text(insert_query), {'username':username, 'JobSeekerID':JobSeekerID, 'Age':Age, 'Gender':Gender, 
                                'DesiredPosition':DesiredPosition, 'DesiredSalary':DesiredSalary})
                g.conn.commit()
                return redirect(url_for('index'),code=302)   
    else:
        return render_template('signup.html')

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
       SELECT e.*, d.departmentname, d.stateid, d.cityname, f.annualrevenue, f.marketcapitalization 
        FROM employee e
        JOIN financialdata f
        ON e.companyid = f.companyid and e.years = f.years
        join department d
        on e.departmentid =  d.departmentid
        join location l
        on d.stateid = l.stateid and d.cityname = l.cityname
        where e.companyid = :company_id AND e.years = f.years;
    """
    result = g.conn.execute(text(query), {'company_id': company_id})
    data = result.fetchall()
    result.close()

    # Fetch the list of departments
    query2 = """
    SELECT DISTINCT d.departmentname
    FROM department d
    JOIN employee e ON d.departmentid = e.departmentid
    WHERE e.companyid = :company_id
    """
    result = g.conn.execute(text(query2), {'company_id': company_id})
    departments = [{"name": row.departmentname} for row in result.fetchall()]
    # Close the database connection
    result.close()

    # Pass the data and departments to the template for rendering
    return render_template('company_details.html', data=data, departments=departments)

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
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e 
                Join department d
                on e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND gender = :filter_option_2"""
        elif filter_option_1 == 'Positions':
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e
                Join department d 
                on e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND currentposition = :filter_option_2"""
        elif filter_option_1 == 'Departments':
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e
                JOIN department d
                ON e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND d.departmentname = :filter_option_2"""
        elif  filter_option_1 == 'Year':
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e
                JOIN department d
                ON e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND years = :filter_option_2"""
        elif  filter_option_1 == 'State':
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e
                JOIN department d
                ON e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND d.stateid = :filter_option_2"""
        elif filter_option_1 == 'Financial Data':
            query = "SELECT * FROM financialdata WHERE companyid = :company_id AND years = :filter_option_2"
        filtered_data = g.conn.execute(text(query), {'company_id': company_id, 'filter_option_2': filter_option_2}).fetchall()
        select_query_1 = "SELECT * FROM company"
        cursor = g.conn.execute(text(select_query_1))
        companies = [{"id": c.companyid, "name": c.companyname} for c in cursor.fetchall()]
        cursor.close()
        g.conn.close()
        return render_template('filtered_data.html', filtered_data=filtered_data, 
                               filter_option_1=filter_option_1, filter_option_2=filter_option_2, 
                               company_id=company_id, companies=companies)
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
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e 
                Join department d
                on e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND gender = :filter_option_2"""
        elif filter_option_1 == 'Positions':
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e
                Join department d 
                on e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND currentposition = :filter_option_2"""
        elif filter_option_1 == 'Departments':
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e
                JOIN department d
                ON e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND d.departmentname = :filter_option_2"""
        elif  filter_option_1 == 'Year':
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e
                JOIN department d
                ON e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND years = :filter_option_2"""
        elif  filter_option_1 == 'State':
            query = """SELECT e.*, d.departmentname, d.stateid, d.cityname
                FROM employee e
                JOIN department d
                ON e.departmentid = d.departmentid
                WHERE e.companyid = :company_id AND d.stateid = :filter_option_2"""
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

@app.route('/review', methods=['GET', 'POST'])
def review_data():
    company_id = request.args.get('company_id')
    query = """
    SELECT r.*
    FROM review r
    JOIN company c 
    ON c.companyname = r.companyname
    WHERE c.companyid = :company_id
    """
    results = g.conn.execute(text(query), {'company_id': company_id}).fetchall()
    
    if request.method == 'POST':
        add_review = request.form['add_review']
        rating = request.form['rating']
        query = """
            select distinct employeeid,c.companyname
            from staff 
            join company c
            on staff.companyid = c.companyid
            where userid = :username and c.companyid = :company_id
        """
        result1 = g.conn.execute(text(query), {'username': session["username"],'company_id': company_id}).fetchone()

        if result1 is not None:
            # Generate unique review id
            while True:
                reviewid = "REV" + "{:03d}".format(random.randint(0, 999))
                result = g.conn.execute(text("SELECT COUNT(*) FROM review WHERE reviewid = :reviewid"), {'reviewid': reviewid}).fetchone()
                if result[0] == 0:
                    # review id is unique, break out of loop
                    break

            companynamequery = """
                select companyname,companyid
                from company
                where companyid = :company_id
                """
            companyname = g.conn.execute(text(companynamequery), {'company_id': company_id}).fetchone()[0]
            yearsquery = """
                select years
                from employee
                where companyid = :company_id AND employeeid = :employeeid 
                """
            years = g.conn.execute(text(yearsquery), {'company_id': company_id,'employeeid':result1[0]}).fetchone()[0]
            #update review table
            query ="""
                INSERT INTO review (reviewid, companyname, rating, content) VALUES (:reviewid, :companyname, :rating, :add_review)
            """
            g.conn.execute(text(query), {'reviewid': reviewid, 'companyname': companyname, 'rating': rating, 'add_review': add_review})
            g.conn.commit()
            #update staff table
            userid = session['username']
            query = """
                UPDATE staff SET reviewid = :reviewid, years = :years
                WHERE employeeid = :employeeid AND userid = :userid
            """
            g.conn.execute(text(query), {'userid': userid, 'employeeid': result1[0], 
                                         'company_id':company_id,
                                         'reviewid': reviewid, 'years': years})
            g.conn.commit()
            #update added review to review table
            query = """
                SELECT r.*
                FROM review r
                JOIN company c 
                ON c.companyname = r.companyname
                WHERE c.companyid = :company_id
                """
            results = g.conn.execute(text(query), {'company_id': company_id}).fetchall()
            return render_template("review.html", company_id=company_id, results=results)
        else:
            error_msg = "Only employee can give comment"
            return render_template('review.html', error_msg=error_msg,company_id=company_id, results=results)
            
    return render_template("review.html", company_id=company_id, results=results)


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
