	▪	The PostgreSQL account: 
	The PostgreSQL account name for our database on our server is yy3262, which is Yijie Yang’s UNI.
	▪	The URL of our web application:
	http://34.23.72.248:8111
	▪	Description of implemented functions:
	The following parts of the original proposal in Part 1 were successfully implemented:
	1.	 User authentication system with login and sign-up pages, allowing users to create accounts as employees or job seekers.
	2.	 Employee ID validation for employee users.
	3.	 Storage capabilities for user data, including age, gender, desired position, and salary for job seekers.
	4.	 Search interface for users to find companies by keywords and suggestions.
	5.	 Company page with basic information
	6.	 Data filtering feature with options for year, location, department, position, gender, and financial data.
	7.	 Data comparing feature allowing users to choose data from one company to compare with another.
	▪	Description of two interesting web pages:
	•	Company Details Web Page
		This web page displays all the employees information for the interested company selected by the user, including their departments and locations. 
		This part is interesting because it requires joins of all tables that contain the employee-related data. 
		The page is also used for filtering company data based on user-selected criteria. 
		It involves interesting database operations because it requires generating dynamic SQL queries based on the selected companies and filter options. 
		The inputs on the page are used to identify the appropriate SQL query to return the desired filtered data. 
		The results are then displayed in a table format on the next filtered data page.
	•	Reviews Web Page
		This web page displays all the ratings and reviews by the employees of the selected company. 
		It also allow employee users to submit ratings and reviews for a company. 
		It involves interesting database operations due to the various steps required for submitting a review and ensuring data integrity:
		1. Verify that the user is an employee of the company by checking that their employee IDs and company names exist. 
		This operation involves a SELECT query with a WHERE clause that considers both the user ID and the company ID.
		2. Generate a unique review ID for the submitted review. 
		This process involves creating a random review ID and then verifying its uniqueness by querying the database to ensure there is no existing review with the same ID.
		3. Update ‘review’ table and ‘staff’ table with the new review information. 
		This operation involves an INSERT statement with generated review ID, company name, rating and review content.
		For displaying reviews, a JOIN operation is performed between the 'review' and 'company' tables to fetch all the reviews related to a specific company. 
		This operation requires a SELECT query with a JOIN clause based on the company name and a WHERE clause that considers the company ID. 
		The results are then displayed in a table format on the page.



