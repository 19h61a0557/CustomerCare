
from flask import Flask, render_template, request, redirect, session, url_for
import ibm_db
import re

app = Flask(__name__)
app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b70af05b-76e4-4bca-a1f5-23dbb4c6a74e.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32716;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA (5).crt;UID=wln74818;PWD=2VOjd0gekddLy1tu", '', '')
print("connected")
# routes
# home
@app.route("/", methods=['GET', "POST"])
def home():
    # print(session['user'])
    if ('user' not in session.keys()) or (session['user'] == None):
        return redirect(url_for('login'))
    else:
        sql = "SELECT * FROM USER WHERE ID ="+str(session['user'])
        stmt=ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        userdetails=ibm_db.fetch_tuple(stmt)
        print(userdetails)

        if userdetails[3] == 2:
            return render_template("home.html", user=userdetails)
        
        elif userdetails[3] == 1:
            user1=[]
            sql1 = "SELECT * FROM tickets"  #WHERE id=+str(session['user'])
            stmt1=ibm_db.prepare(conn, sql1)
            ibm_db.execute(stmt1)
            all_users=ibm_db.fetch_tuple(stmt1)
            user1.append(all_users)
            print(user1)
            return render_template("home.html", user=userdetails,tickets=user1)    
           

        else:
            if userdetails[3] == 0:
                if request.method == "POST":
                    title = request.form['title']
                    description = request.form['description']

                    insert_sql = 'INSERT INTO tickets VALUES (?,?,NULL,?,?,NULL)'
                    prep_stmt = ibm_db.prepare(conn, insert_sql)
                    ibm_db.bind_param(prep_stmt, 1, userdetails[4])
                    ibm_db.bind_param(prep_stmt, 2, userdetails[0])
                    ibm_db.bind_param(prep_stmt, 3, title)
                    ibm_db.bind_param(prep_stmt, 4, description)
                    ibm_db.execute(prep_stmt)
                       
                    sql ='SELECT* FROM user WHERE id=' +str(session['user'])
                    stmt=ibm_db.prepare(conn, sql)
                    ibm_db.execute(stmt)
                    account=ibm_db.fetch_tuple(stmt)
                    print(account)
                    
                    sql1="SELECT * FROM tickets"
                    stmt1=ibm_db.prepare(conn, sql1)
                    ibm_db.execute(stmt1)
                    data1 = ibm_db.fetch_tuple(stmt1)
                    print(data1)
                    # print('gajanan')
                    # print(type(data1))
                    row1=[]
                    while data1!= False:
                        row1.append(data1)
                        data1 = ibm_db.fetch_tuple(stmt1)
                    print(row1)
                    return render_template("home.html", msg="Ticket Filed", user=account, tickets=row1)
                                         
        return render_template("home.html", user=userdetails)
       
          
 # user account registration
@app.route("/register", methods=["GET", "POST"])
def register_account():
    # msg=''
    if request.method == "POST":
        USERNAME = request.form['username']
        EMAIL = request.form['email']
        PASSWORD = request.form['password']
        ROLE = 0
        # id = 0
        sql = "SELECT* FROM user WHERE EMAIL= ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, EMAIL)
        ibm_db.execute(stmt)
        userdetails = ibm_db.fetch_assoc(stmt)
        print(userdetails)
        if userdetails:
            # msg = 'Account already exists !'
            return render_template("login.html")

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', EMAIL):
            # msg = 'Invalid email address !'
            return render_template("register.html")
        else:
            sql2 = "SELECT count(*) FROM user"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.execute(stmt2)
            length = ibm_db.fetch_assoc(stmt2)
            print(length)
            insert_sql = "INSERT INTO USER VALUES (?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, USERNAME)
            ibm_db.bind_param(prep_stmt, 2, EMAIL)
            ibm_db.bind_param(prep_stmt, 3, PASSWORD)
            ibm_db.bind_param(prep_stmt, 4, ROLE)
            ibm_db.bind_param(prep_stmt, 5, length['1']+1)
            ibm_db.execute(prep_stmt)
            return redirect(url_for("login"))

    return render_template("register.html")

# login


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        sql1 = "SELECT * FROM user WHERE email=?"
        stmt = ibm_db.prepare(conn, sql1)
        ibm_db.bind_param(stmt, 1, email)
        # ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        userdetails = ibm_db.fetch_tuple(stmt)
        print(userdetails)
        if userdetails:
            # if pbkdf2_sha256.verify(password,userdetails[2]):
            session['user'] =userdetails[4]
            return redirect(url_for("home"))
        else:
            msg = "Incorrect Password"
        # else:
        #     msg = "User does not exist"
            return render_template("login.html", msg=msg)
    return render_template("login.html")

# logout


@app.route("/logout")
def logout():
    session['user'] = None
    return redirect(url_for("home"))


# ticket detail
@app.route("/ticket/<int:id>", methods=["GET", "POST"])
def ticket_detail(id):
    sql= "SELECT * FROM tickets WHERE id = ?" #+str(id)
    stmt = ibm_db.prepare(conn, sql)
    id=str(id)
    ibm_db.bind_param(stmt, 1, id)
    ibm_db.execute(stmt)
    ticket = ibm_db.fetch_tuple(stmt)
    # ticket=ibm_db.fetch_tuple(stmt)
    # cursor = mysql.connection.cursor()
    # cursor.execute("SELECT * FROM Tickets WHERE id=%s", [id])
    # ticket = cursor.fetchone()
    sql = "SELECT * FROM User WHERE id =" +str(ticket[0])
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    customer=ibm_db.fetch_tuple(stmt)
    # cursor.execute("SELECT * FROM User WHERE id=%s", [ticket[1]])
    # customer = cursor.fetchone()
    sql = "SELECT * FROM User WHERE id =" +str(session['user'])
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    user=ibm_db.fetch_tuple(stmt)
    print(user)
    # cursor.execute("SELECT * FROM User WHERE id=%s", [session['user']])
    # user = cursor.fetchone()
    userlist=[]
    sql = "SELECT * FROM user WHERE role=1"
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    all_users=ibm_db.fetch_tuple(stmt)
    print(all_users)
    userlist.append(all_users)
    print(userlist)
    print('hello')
    # cursor.execute("SELECT * FROM User WHERE role=1")
    # all_users = cursor.fetchall()
    sql = "SELECT * FROM User WHERE id =" +str(session['user'])
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    agent=ibm_db.fetch_tuple(stmt)
    print(agent)
    # cursor.execute("SELECT * FROM User WHERE id=%s", [ticket[2]])
    # agent = cursor.fetchone()
    if agent is None:
        agent = [None, None]
    if user is None:
        return redirect(url_for("login"))

    if request.method == "POST":
        agent = request.form['agent']
        sql1="UPDATE tickets SET agent=? WHERE id =" +str(id)
        stmt1=ibm_db.prepare(conn, sql1)
        ibm_db.bind_param(stmt1, 1, all_users[0])
        ibm_db.execute(stmt1)
        # cursor.execute(
        #     "UPDATE Tickets SET agent= %s WHERE id = %s", (agent, id))
        sql="UPDATE tickets SET progress='assigned' WHERE id =" +str(id)
        stmt=ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
             
      
        return redirect(url_for("panel"))
    return render_template("details.html", ticket=ticket, agent=agent, customer=customer, user=user, all_users=userlist)


# admin register # 

@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = 2
        id = 0
        secret_key = request.form['secret']
        if secret_key == "12345":
            sql2 = "SELECT count(*) FROM user"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.execute(stmt2)
            length = ibm_db.fetch_assoc(stmt2)
            print(length)
            insert_sql = "INSERT INTO user VALUES (?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.bind_param(prep_stmt, 4, role)
            ibm_db.bind_param(prep_stmt, 5, id)
            ibm_db.execute(prep_stmt)
            return redirect(url_for("login"))
        else:
            return render_template("admin_register.html", msg="Invlaid Secret")

    return render_template("admin_register.html")

# promote agent
@app.route("/panel", methods=['GET', 'POST'])
def panel():
    id = session['user']
    if id is None:
        return redirect("login")

    sql = "SELECT * FROM user WHERE id =" +str(session['user'])
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    user_details=ibm_db.fetch_tuple(stmt)
    print(user_details)

    if user_details[3] != 2:
        return "You do not have administrator privileges"
    else:
        all_users=[]
        sql="SELECT * FROM User WHERE role=0"
        stmt=ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        all_users1 =ibm_db.fetch_tuple(stmt)
        all_users.append(all_users1)
        print(all_users)
        # sql="SELECT * FROM Tickets WHERE progress IS NULL"
        # stmt=ibm_db.prepare(conn, sql)
        # ibm_db.execute(stmt)
        # tickets =ibm_db.fetch_assoc(stmt)
        sql1="SELECT * FROM tickets"
        stmt1=ibm_db.prepare(conn, sql1)
        ibm_db.execute(stmt1)
        data1 = ibm_db.fetch_tuple(stmt1)
        print(data1)
        tickets=[]
        while data1!= False:
            tickets.append(data1)
            data1 = ibm_db.fetch_tuple(stmt1)
        print(tickets)
     
        if request.method == "POST":
            user_id = request.form['admin-candidate']
            sql="UPDATE User SET role=1 WHERE id = "+str(user_id)
            stmt=ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt)

            '''cursor.execute("SELECT * FROM User WHERE id = %s", [user_id])
            promoted_agent = cursor.fetchone()
            msg = Message('Promoted to Agent', sender=config.email,
                          recipients=[promoted_agent[1]])
            msg.body = """
                Dear User,
                You have been promoted to an Agent in the Customer-Care-Registry.
                You will be able to handle tickets for the customer from now on.
                Congratulations.
            """
            mail.send(msg)'''
            return redirect(url_for("panel"))
        return render_template("panel.html", all_users=all_users, user=user_details, tickets=tickets)

# accept ticket

@app.route("/accept/<int:ticket_id>/<int:user_id>")
def accept(ticket_id, user_id):

    sql = "SELECT * FROM User WHERE id =" +str(user_id)
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    agent=ibm_db.fetch_tuple(stmt)
    print(agent)
    print('gajju')
   
    sql= "SELECT * FROM tickets WHERE id =" +str(ticket_id)
    stmt1 = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt1)
    ticket = ibm_db.fetch_tuple(stmt1)
    print(ticket)
    print('gajju2')
    # cursor.execute("SELECT * FROM Tickets WHERE id=%s", [ticket_id])
    # ticket = cursor.fetchone()

    # sql='SELECT email FROM User WHERE id=?' [ticket[1]]
    # stmt = ibm_db.prepare(conn, sql)
    # ibm_db.bind_param(stmt, 1, id)
    # ibm_db.execute(stmt)
    # customer = ibm_db.fetch_tuple(stmt)
    # cursor.execute("SELECT email FROM User WHERE id=%s", [ticket[1]])
    # customer = cursor.fetchone()
    
    # if agent[0] == ticket[2]:
    if ticket[5] == "assigned" :
        sql="UPDATE tickets SET progress='accepted' WHERE id =" +str(ticket_id)
        stmt=ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        print('accepted')
  
        # cursor.execute(
        #     "UPDATE Tickets SET progress='accepted' WHERE id=%s", [ticket_id])
        # mysql.connection.commit()
       
        # msg = Message('Ticket Progress', sender=config.email,
        #               recipients=[customer[0]])
        # msg.body = f"""
        #     Dear User,
        #     Your Ticket has been accepted by {agent[1]}
        # """
        # mail.send(msg)
    return redirect(url_for("home"))


# close ticket
@app.route("/delete/<int:ticket_id>/<int:user_id>")
def delete(ticket_id, user_id):

    sql = "SELECT * FROM User WHERE id =" +str(user_id)
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    agent=ibm_db.fetch_tuple(stmt)
    print(agent)
    print('ganga')
  
    # cursor = mysql.connection.cursor()
    # cursor.execute("SELECT * FROM User WHERE id = %s", [user_id])
    # agent = cursor.fetchone()
    sql= "SELECT * FROM tickets WHERE id =" +str(ticket_id)
    stmt1 = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt1)
    ticket = ibm_db.fetch_tuple(stmt1)
    print(ticket)
    print('ganga1')
  
    # if agent[0] == ticket[2]:
    if ticket[5] == "accepted":
        sql='DELETE FROM tickets WHERE id =' +str(ticket_id)
        stmt = ibm_db.prepare(conn, sql)
        # ibm_db.bind_param(stmt, 1,id)
        ibm_db.execute(stmt) 
        print('DELETED')

        # cursor.execute("DELETE FROM Tickets WHERE id=%s", [ticket_id])
        # mysql.connection.commit()
        # sql= "SELECT * FROM Tickets WHERE id = ?" 
        # stmt = ibm_db.prepare(conn, sql)
        # ibm_db.bind_param(stmt, 1, id)
        # ibm_db.execute(stmt)
        # customer=ibm_db.fetch_tuple(stmt)
        # cursor.execute("SELECT * FROM User WHERE id=%s", [ticket[1]])
        # customer = cursor.fetchone()
    ''' msg = Message('Ticket Progress', sender=config.email,
                      recipients=[customer[1]])
        msg.body = f"""
            Dear User,
            Your Ticket has been Closed by {agent[1]}
            Thanks For using Customer Care Registry.
        """
        mail.send(msg)'''
    return redirect(url_for("home"))


# run server
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
