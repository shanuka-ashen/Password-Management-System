# Import necessary modules
from asyncio.windows_events import NULL
from ssl import Purpose
import pymysql, os, base64
from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


# Create an instance of the flask app
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pmstc'

# Initialize MySQL
mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'],
    cursorclass=pymysql.cursors.DictCursor
)

# Define your secret key and initialization vector (IV)
secret_key = b'YourSecretKey123'
iv = b'YourIV1234567890'

# Function to encrypt a password
def encrypt_password(password):
    # Convert the password string to bytes
    password_bytes = password.encode('utf-8')
    
    # Pad the password bytes to the AES block size
    padded_password = pad(password_bytes, AES.block_size)
    
    # Create AES cipher object with CBC mode
    cipher = AES.new(secret_key, AES.MODE_CBC, iv)
    
    # Encrypt the password
    encrypted_password = cipher.encrypt(padded_password)
    
    # Convert the encrypted password to base64-encoded string
    encrypted_password_base64 = base64.b64encode(encrypted_password).decode('utf-8')
    
    return encrypted_password_base64

def decrypt_password(encrypted_password_base64):
    try:
        # Convert the base64-encoded string to bytes
        encrypted_password = base64.b64decode(encrypted_password_base64)
        
        # Create AES cipher object with CBC mode
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        
        # Decrypt the password
        decrypted_password = unpad(cipher.decrypt(encrypted_password), AES.block_size).decode('utf-8')
        
        return decrypted_password
    except Exception as e:
        # Log the error for debugging
        print("Error during password decryption:", e)
        return None



# Define a route for the home page
@app.route("/login")
@app.route("/")
def home():
    # Render the login.html template
    return render_template("login.html")

@app.route("/signup")
def signup():
    # Render the login.html template
    return render_template("signup.html")



# Add this route for registration
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("register-username")
    password = request.form.get("register-password")
    source_url = request.form.get("source_url")

    with mysql.cursor() as cursor:
        # Check if the username already exists
        query = "SELECT * FROM login WHERE username=%s"
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            if source_url == "/admin/dashboard":
                flash("Username already exists.", "error")  # Flash the error message
                return redirect(url_for('admin_dashboard'))
            elif source_url == "/signup":
                return render_template("signup.html", error="Username already exists.")


        # Hash the password before storing it
        password = generate_password_hash(password, method='pbkdf2:sha256')

        insert_query = "INSERT INTO login (username, password) VALUES (%s, %s)"
        cursor.execute(insert_query, (username, password))
        mysql.commit()

    # Redirect to different URL based on the source
    if source_url == "/admin/dashboard":
        return redirect(url_for('admin_dashboard'))
    elif source_url == "/signup":
        return redirect(url_for('home'))
    else:
        # Default redirect if source_url is not recognized
        return redirect(url_for('home'))

    



# Update the login route
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    with mysql.cursor() as cursor:
        # Check if the user exists and get their role
        query = "SELECT username, password, role, attempts FROM login WHERE username=%s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["username"] = user["username"]
            session["role"] = user["role"]

            # Reset login attempts to 3
            update_query = "UPDATE login SET attempts=3 WHERE username=%s"
            cursor.execute(update_query, (username,))
            mysql.commit()

            # Redirect based on user role
            if user["role"] == "A":
                return redirect(url_for("admin_dashboard"))
            elif user["role"] == "TL":
                return redirect(url_for("team_lead_dashboard"))
            elif user["role"] == "TM":
                return redirect(url_for("team_member_dashboard"))
            elif user["role"] == "U":
                return redirect(url_for("user_dashboard"))
            elif user["role"] == "":
                return render_template("login.html", error="User Role Is Not Assigned")
            elif user["role"] == "B":
                return render_template("login.html", error="User Is Blocked")
        else:
            # Check if the user exists in the login table
            if user:
                attempts = user["attempts"]
                if attempts > 1:
                    remaining_attempts = attempts - 1
                    error_message = f"Invalid credentials. {remaining_attempts} attempts remaining."
                    # Update the login attempts
                    update_query = "UPDATE login SET attempts=%s WHERE username=%s"
                    cursor.execute(update_query, (remaining_attempts, username))
                    mysql.commit()
                    return render_template("login.html", error=error_message)
                else:
                    # Block the user by updating the role to "B"
                    update_query = "UPDATE login SET role='B' WHERE username=%s"
                    cursor.execute(update_query, (username,))
                    mysql.commit()
                    return render_template("login.html", error="User Is Blocked")
            else:
                return render_template("login.html", error="Invalid credentials")


        

@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")


@app.route("/reset_password_page", methods=["GET", "POST"])
def reset_password_page():
    return render_template("reset_password.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        # Render the password reset form
        return render_template("reset_password.html", error="")

    elif request.method == "POST":
        username = session['username']
        old_password = request.form.get("old-password")
        new_password = request.form.get("new-password")

        print(username)
        print(old_password)

        with mysql.cursor() as cursor:
            # Check if the username exists
            query = "SELECT * FROM login WHERE username=%s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()

            if not user:
                error_message = "User not found."
                return render_template("reset_password.html", error=error_message)

            # Check if the old password matches
            if not check_password_hash(user["password"], old_password):
                error_message = "Old password is incorrect."
                return render_template("reset_password.html", error=error_message)

            # Hash the new password before updating it
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

            # Update the password in the database
            update_query = "UPDATE login SET password=%s WHERE username=%s"
            cursor.execute(update_query, (hashed_password, username))
            mysql.commit()

            session.clear()
            error_message = "Password reset successful. Please log in with your new password."
            return render_template("login.html", success=error_message)
        


# Add these routes for the Admin Module
# Update the admin_dashboard route in your Flask application
@app.route("/admin/dashboard")
def admin_dashboard():
    if 'username' in session and 'role' in session and session['role'] == 'A':
        error_messages = get_flashed_messages(category_filter=["error"])  # Retrieve error messages
        if error_messages:
            error = error_messages[0]  # Assuming you only flash one error message at a time
        else:
            error = ""

        username = session['username']
        with mysql.cursor() as cursor:
            # Fetch users
            query_users = "SELECT username, role FROM login"
            cursor.execute(query_users)
            users = cursor.fetchall()

            # Fetch projects
            query_projects = "SELECT name FROM project"
            cursor.execute(query_projects)
            projects = cursor.fetchall()

            # Fetch assigned projects for each user
            query_assigned_projects = "SELECT username, projectname FROM userprojects"
            cursor.execute(query_assigned_projects)
            assigned_projects = cursor.fetchall()

            # Fetch passwords assigned to each project
            query_passwords = "SELECT projectname, purpose, password FROM passwords"
            cursor.execute(query_passwords)
            project_passwords = cursor.fetchall()

            # Decrypt passwords
            for password in project_passwords:
                encrypted_password_base64 = password['password']
                decrypted_password = decrypt_password(encrypted_password_base64)
                password['password'] = decrypted_password

            # Group passwords by projectname
            grouped_passwords = {}
            for password in project_passwords:
                project_name = password['projectname']
                purpose = password['purpose']
                password_value = password['password']

                if project_name not in grouped_passwords:
                    grouped_passwords[project_name] = []

                grouped_passwords[project_name].append({'purpose': purpose, 'password': password_value})

            # Fetch passwords assigned to the current user
            query_passwords = "SELECT purpose, password FROM userpasswords WHERE username = %s"
            cursor.execute(query_passwords, (username,))
            user_passwords = cursor.fetchall()

            # Decrypt passwords
            for password in user_passwords:
                encrypted_password_base64 = password['password']
                decrypted_password = decrypt_password(encrypted_password_base64)
                password['password'] = decrypted_password    

        return render_template("admin.html", users=users, projects=projects, assigned_projects=assigned_projects, grouped_passwords=grouped_passwords, error=error, user_passwords=user_passwords)
    else:
        return render_template("login.html")
    
    


@app.route("/team_lead/dashboard")
def team_lead_dashboard():
    if 'username' in session and 'role' in session and session['role'] == 'TL':
        error_messages = get_flashed_messages(category_filter=["error"])  # Retrieve error messages
        if error_messages:
            error = error_messages[0]  # Assuming you only flash one error message at a time
        else:
            error = ""

        username = session['username']
        with mysql.cursor() as cursor:
            # Fetch users
            query_users = "SELECT username, role FROM login"
            cursor.execute(query_users)
            users = cursor.fetchall()

            # Fetch projects
            query_projects = "SELECT name FROM project"
            cursor.execute(query_projects)
            projects = cursor.fetchall()

            # Fetch assigned projects for each user
            query_assigned_projects = "SELECT username, projectname FROM userprojects"
            cursor.execute(query_assigned_projects)
            assigned_projects = cursor.fetchall()

            # Fetch passwords assigned to each project
            query_passwords = "SELECT projectname, purpose, password FROM passwords"
            cursor.execute(query_passwords)
            project_passwords = cursor.fetchall()

            # Decrypt passwords
            for password in project_passwords:
                encrypted_password_base64 = password['password']
                decrypted_password = decrypt_password(encrypted_password_base64)
                password['password'] = decrypted_password

            # Group passwords by projectname
            grouped_passwords = {}
            for password in project_passwords:
                project_name = password['projectname']
                purpose = password['purpose']
                password_value = password['password']

                if project_name not in grouped_passwords:
                    grouped_passwords[project_name] = []

                grouped_passwords[project_name].append({'purpose': purpose, 'password': password_value})

            # Fetch passwords assigned to the current user
            query_passwords = "SELECT purpose, password FROM userpasswords WHERE username = %s"
            cursor.execute(query_passwords, (username,))
            user_passwords = cursor.fetchall()

            # Decrypt passwords
            for password in user_passwords:
                encrypted_password_base64 = password['password']
                decrypted_password = decrypt_password(encrypted_password_base64)
                password['password'] = decrypted_password 

        return render_template("TL.html", users=users, projects=projects, assigned_projects=assigned_projects, grouped_passwords=grouped_passwords, error=error, user_passwords=user_passwords)
    else:
        return render_template("login.html")        




@app.route("/team_member/dashboard")
def team_member_dashboard():
    if 'username' in session and 'role' in session and session['role'] == 'TM':
        username = session['username']
        error_messages = get_flashed_messages(category_filter=["error"])  # Retrieve error messages
        if error_messages:
            error = error_messages[0]  # Assuming you only flash one error message at a time
        else:
            error = ""

        username = session['username']
        with mysql.cursor() as cursor:

            # Fetch passwords assigned to the current user
            query_passwords = "SELECT purpose, password FROM userpasswords WHERE username = %s"
            cursor.execute(query_passwords, (username,))
            user_passwords = cursor.fetchall()

            # Decrypt passwords
            for password in user_passwords:
                encrypted_password_base64 = password['password']
                decrypted_password = decrypt_password(encrypted_password_base64)
                password['password'] = decrypted_password

            # Fetch assigned projects for the current user
            query_assigned_projects = "SELECT projectname FROM userprojects WHERE username = %s"
            cursor.execute(query_assigned_projects, (username,))
            assigned_projects = [row['projectname'] for row in cursor.fetchall()]

            if assigned_projects:
                # Fetch passwords assigned to the user's projects
                query_passwords = "SELECT projectname, purpose, password FROM passwords WHERE projectname IN %s"
                cursor.execute(query_passwords, (tuple(assigned_projects),))
                project_passwords = cursor.fetchall()

                # Decrypt passwords
                for password in project_passwords:
                    encrypted_password_base64 = password['password']
                    decrypted_password = decrypt_password(encrypted_password_base64)
                    password['password'] = decrypted_password

                # Group passwords by projectname
                grouped_passwords = {}
                for password in project_passwords:
                    project_name = password['projectname']
                    purpose = password['purpose']
                    password_value = password['password']

                    if project_name not in grouped_passwords:
                        grouped_passwords[project_name] = []

                    grouped_passwords[project_name].append({'purpose': purpose, 'password': password_value})
            else:
                grouped_passwords = {}

        return render_template("TM.html", assigned_projects=assigned_projects, grouped_passwords=grouped_passwords, error=error, user_passwords=user_passwords)
    else:
        return render_template("login.html")
    


@app.route("/user/dashboard")
def user_dashboard():
    if 'username' in session and 'role' in session and session['role'] == 'U':
        username = session['username']
        error_messages = get_flashed_messages(category_filter=["error"])  # Retrieve error messages
        if error_messages:
            error = error_messages[0]  # Assuming you only flash one error message at a time
        else:
            error = ""

        with mysql.cursor() as cursor:
            # Fetch passwords assigned to the current user
            query_passwords = "SELECT purpose, password FROM userpasswords WHERE username = %s"
            cursor.execute(query_passwords, (username,))
            user_passwords = cursor.fetchall()

            # Decrypt passwords
            for password in user_passwords:
                encrypted_password_base64 = password['password']
                decrypted_password = decrypt_password(encrypted_password_base64)
                password['password'] = decrypted_password

        return render_template("U.html", user_passwords=user_passwords, error=error)
    else:
        return render_template("login.html")




@app.route("/add_project", methods=["POST"])
def add_project():
    new_project_name = request.form.get("project-name")
    source_url = request.form.get("source_url") 

    with mysql.cursor() as cursor:
        # Check if the username already exists
        query = "SELECT name FROM project WHERE name=%s"
        cursor.execute(query, (new_project_name,))
        existing_user = cursor.fetchone()
        if existing_user:
            if source_url == "/admin/dashboard":
                flash("Project name already exists.", "error")  # Flash the error message
                return redirect(url_for('admin_dashboard'))
            elif source_url == "/team_lead/dashboard":
                flash("Project name already exists.", "error")  # Flash the error message
                return redirect(url_for('team_lead_dashboard'))

        # Insert new project into the database
        insert_query = "INSERT INTO project (name) VALUES (%s)"
        cursor.execute(insert_query, (new_project_name,))
        mysql.commit()    

    # Redirect back to the admin dashboard
    if source_url == "/admin/dashboard":
        return redirect(url_for('admin_dashboard'))
    elif source_url == "/team_lead/dashboard":
        return redirect(url_for('team_lead_dashboard'))
    

@app.route("/admin/edit_user/<string:username>")
def admin_edit_user(username):
    with mysql.cursor() as cursor:
        query = "SELECT username, role FROM login WHERE username=%s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

    return render_template("admin.html", user=user)

@app.route("/admin/delete_user/<string:username>", methods=["POST"])
def admin_delete_user(username):
    with mysql.cursor() as cursor:
        query = "DELETE FROM login WHERE username=%s"
        cursor.execute(query, (username,))
        mysql.commit()

        query = "DELETE FROM userprojects WHERE username=%s"
        cursor.execute(query, (username,))
        mysql.commit()

    return redirect(url_for('admin_dashboard'))

@app.route("/admin/update_user/<string:username>", methods=["POST"])
def admin_update_user(username):
    new_username = request.form.get("edit-username")
    new_role = request.form.get("edit-role")

    with mysql.cursor() as cursor:
        query = "UPDATE login SET username=%s, role=%s WHERE username=%s"
        cursor.execute(query, (new_username, new_role, username))
        mysql.commit()

    return redirect(url_for('admin_dashboard'))




@app.route("/delete_project", methods=["POST"])
def delete_project():
    project_name = request.form.get("delete-project-name")
    source_url = request.form.get("source_url") 

    with mysql.cursor() as cursor:
        # Delete the project from the database
        delete_query = "DELETE FROM project WHERE name=%s"
        cursor.execute(delete_query, (project_name,))
        mysql.commit()

        delete_query = "DELETE FROM passwords WHERE projectname=%s"
        cursor.execute(delete_query, (project_name,))
        mysql.commit()

    # Redirect back to the admin dashboard or wherever appropriate
    if source_url == "/admin/dashboard":
        return redirect(url_for('admin_dashboard'))
    elif source_url == "/team_lead/dashboard":
        return redirect(url_for('team_lead_dashboard'))


# Grant permission route
@app.route("/admin/grant_permission/<string:projectname>", methods=["POST"])
def grant_permission(projectname):
    if 'username' in session and 'role' in session and (session['role'] == 'A' or session['role'] == 'TL'):
        username_to_grant = request.form.get("grant-username")
        source_url = request.form.get("source_url") 

        with mysql.cursor() as cursor:
            # Check if the user already has permission
            query_check_permission = "SELECT * FROM userprojects WHERE username=%s AND projectname=%s"
            cursor.execute(query_check_permission, (username_to_grant, projectname))
            existing_permission = cursor.fetchone()

            if not existing_permission:
                # Grant permission
                query_grant_permission = "INSERT INTO userprojects (username, projectname) VALUES (%s, %s)"
                cursor.execute(query_grant_permission, (username_to_grant, projectname))
                mysql.commit()

    if source_url == "/admin/dashboard":
        return redirect(url_for('admin_dashboard'))
    elif source_url == "/team_lead/dashboard":
        return redirect(url_for('team_lead_dashboard'))

# Revoke permission route
@app.route("/admin/revoke_permission/<string:projectname>", methods=["POST"])
def revoke_permission(projectname):
    if 'username' in session and 'role' in session and (session['role'] == 'A' or session['role'] == 'TL'):
        username_to_revoke = request.form.get("revoke-username")
        source_url = request.form.get("source_url")

        with mysql.cursor() as cursor:
            # Check if the user has permission
            query_check_permission = "SELECT * FROM userprojects WHERE username=%s AND projectname=%s"
            cursor.execute(query_check_permission, (username_to_revoke, projectname))
            existing_permission = cursor.fetchone()

            if existing_permission:
                # Revoke permission
                query_revoke_permission = "DELETE FROM userprojects WHERE username=%s AND projectname=%s"
                cursor.execute(query_revoke_permission, (username_to_revoke, projectname))
                mysql.commit()

    if source_url == "/admin/dashboard":
        return redirect(url_for('admin_dashboard'))
    elif source_url == "/team_lead/dashboard":
        return redirect(url_for('team_lead_dashboard'))


@app.route("/admin/add_password", methods=["POST"])
def admin_add_password():
    project_name = request.form.get("project-name")
    purpose = request.form.get("add-password-purpose")
    password = request.form.get("add-password-value")
    source_url = request.form.get("source_url")
    username = session['username']
    table_name = request.form.get("table_name")

    # Encrypt the password
    encrypted_password_base64 = encrypt_password(password)

    if table_name == 'ProjectPassword':                                                                                    
        with mysql.cursor() as cursor:
            # Insert new password into the database
            insert_query = "INSERT INTO passwords (projectname, purpose, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (project_name, purpose, encrypted_password_base64))
            mysql.commit()

    elif table_name == 'UserPassword':
        with mysql.cursor() as cursor:
            # Insert the new password into the database
            insert_query = "INSERT INTO userpasswords (username, purpose, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (username, purpose, encrypted_password_base64))
            mysql.commit()   

    # Redirect back to the admin dashboard
    if source_url == "/admin/dashboard":
        return redirect(url_for('admin_dashboard'))
    elif source_url == "/team_lead/dashboard":
        return redirect(url_for('team_lead_dashboard'))
    elif source_url == "/team_member/dashboard":
        return redirect(url_for('team_member_dashboard'))
    elif source_url == "/user/dashboard":
        return redirect(url_for('user_dashboard'))



@app.route("/admin/edit_password/<string:project_name>/<string:purpose>", methods=["POST"])
def admin_edit_password(project_name, purpose):
    new_purpose = request.form.get("edit-password-purpose")
    new_password = request.form.get("edit-password-value")
    source_url = request.form.get("source_url")
    username = session['username']
    table_name = request.form.get("table_name")

    # Encrypt the password
    encrypted_password_base64 = encrypt_password(new_password)

    if table_name == 'ProjectPassword':   
        with mysql.cursor() as cursor:
            # Update password in the database
            update_query = "UPDATE passwords SET purpose=%s, password=%s WHERE projectname=%s AND purpose=%s"
            cursor.execute(update_query, (new_purpose, encrypted_password_base64, project_name, purpose))
            mysql.commit()

    elif table_name == 'UserPassword':  
        with mysql.cursor() as cursor:
            # Update the password in the database
            update_query = "UPDATE userpasswords SET purpose = %s, password = %s WHERE username = %s AND purpose = %s"
            cursor.execute(update_query, (new_purpose, encrypted_password_base64, username, purpose))
            mysql.commit()        

    # Redirect back to the admin dashboard
    if source_url == "/admin/dashboard":
        return redirect(url_for('admin_dashboard'))
    elif source_url == "/team_lead/dashboard":
        return redirect(url_for('team_lead_dashboard'))
    elif source_url == "/team_member/dashboard":
        return redirect(url_for('team_member_dashboard'))
    elif source_url == "/user/dashboard":
        return redirect(url_for('user_dashboard'))

@app.route("/admin/delete_password/<string:project_name>/<string:purpose>", methods=["POST"])
def admin_delete_password(project_name, purpose):
    source_url = request.form.get("source_url")
    username = session['username']
    table_name = request.form.get("table_name")

    if table_name == 'ProjectPassword':   
        with mysql.cursor() as cursor:
            # Delete password from the database
            delete_query = "DELETE FROM passwords WHERE projectname=%s AND purpose=%s"
            cursor.execute(delete_query, (project_name, purpose))
            mysql.commit()
    elif table_name == 'UserPassword':
        with mysql.cursor() as cursor:
            # Delete the password from the database
            delete_query = "DELETE FROM userpasswords WHERE username = %s AND purpose = %s"
            cursor.execute(delete_query, (username, purpose))
            mysql.commit()

    # Redirect back to the admin dashboard
    if source_url == "/admin/dashboard":
        return redirect(url_for('admin_dashboard'))
    elif source_url == "/team_lead/dashboard":
        return redirect(url_for('team_lead_dashboard'))
    elif source_url == "/team_member/dashboard":
        return redirect(url_for('team_member_dashboard'))
    elif source_url == "/user/dashboard":
        return redirect(url_for('user_dashboard'))



# Define a route for the result page
# @app.route("/result")
# def result():
#     Your existing result route logic here

# Run the app in debug mode
if __name__ == "__main__":
    app.secret_key = 'Secret321'  # Replace 'your_secret_key' with a secret key of your choice
    app.run(debug=True)
