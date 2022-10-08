# Django-Rest-API
This is a complete Django Rest Framework with lots of the permissions and access permissions. A complete setup of a program with API.

# Access Permissions
The project is devided in different access level like the unauthentiate user has no permissions to access the data while super user can view all user data and only active user can view his own data only.

# Groups and Schools
Also there is a concept of Group and Schools.
If the user belong to a school and his profife is Teacher then he is able to see his own data while if profile is Coach then he is able to see all the teachers of the same school not other schools also not other Coach data.

# Reset Password via Email
If the user forgot his password he can reset his password via his email address. Also checking if the Email is existing to our database or not.
If Email exists to our database we are send a mail to the user and reset his password.
If email is not in database then send his a error message.

# Change Password functionality.
Chage password functionality require user should be login.
You should have old password and then have to type password twice to confirm password.
If old password is wrong or confirm password does not match to password then show his error message according to error condition.

# Test Cases
The project is complete with all the test cases also. All test cases are there according to user profile as well as role.

# Pagination
The project also contains proper pagination format it will show only five(5) record at a time.

# Database
The project is set up with MySQL Database.

# filter and search
The project has concept of Search record with name, id and email.

# Requirements
The project uses lot of python libraries which are in "Requirement.txt" file.