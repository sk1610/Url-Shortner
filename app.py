from flask import *
from mysql.connector import connect
from flask_mail import Mail,Message
import random
import string
app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='shubhamkhandelwal16102001@gmail.com',
    MAIL_PASSWORD='shubham@63760'
)
app.secret_key='shubhamhmk'

mail=Mail(app)

@app.route('/')
def hello_world():
     return render_template('index3.html')

@app.route('/<url>')
def dynamicurl(url):
    print(url)
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur=connection.cursor()
    query1 = "select * from urlinfo where encryptedurl='{}'".format(url)
    cur.execute(query1)
    originalurl = cur.fetchone()
    if originalurl == None:
        return render_template('index3.html')
    else:
        print(originalurl[1])
        return redirect(originalurl[1])


@app.route('/urlshortner')
def urlshortner():
    url=request.args.get('link')
    custom = request.args.get('customurl')
    print(custom)
    print("planetech")
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur = connection.cursor()
    encryptedurl=''
    if custom=='':
        while True:
          encryptedurl = createencryptedurl()
          query1="select * from urlinfo where encryptedurl='{}'".format(encryptedurl)
          cur.execute(query1)
          xyz=cur.fetchone()
          if xyz==None:
              break
        print(encryptedurl)
        if 'userid' in session:
            id=session['userid']
            query="insert into urlinfo(originalurl,encryptedurl,is_active,created_by) values('{}','{}',1,{})".format(url,encryptedurl,id)
        else:
            query = "insert into urlinfo(originalurl,encryptedurl,is_active) values('{}','{}',1)".format(url,encryptedurl)
        cur=connection.cursor()
        cur.execute(query)
        connection.commit()
        finalencryptedurl='sd.in/'+encryptedurl
    else:
        query1="select * from urlinfo where encryptedurl='{}'".format(custom)
        cur.execute(query1)
        xyz = cur.fetchone()
        if xyz == None:
            if 'userid' in session:
                id = session['userid']
                query="insert into urlinfo(originalurl,encryptedurl,is_active,created_by) values('{}','{}',1,'{}')".format(url,custom,id)
            else:
                query = "insert into urlinfo(originalurl,encryptedurl,is_active) values('{}','{}',1)".format(url,custom,1)
            cur=connection.cursor()
            cur.execute(query)
            connection.commit()
            finalencryptedurl ='sd.in/'+custom
        else:
            return "url already exist"
    if 'userid' in session:
        return redirect('/home')
    else:
        return render_template('index3.html', finalencryptedurl= finalencryptedurl , url=url)


def createencryptedurl():
    letter = string.ascii_letters + string.digits
    encryptedurl = ''
    for i in range(6):
        encryptedurl = encryptedurl + ''.join(random.choice(letter))
    print(encryptedurl)
    return encryptedurl



@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/signup')
def signup():
    return render_template('signUp.html')


@app.route('/checkLoginIn')
def checkLogIn():
    email=request.args.get('email')
    password=request.args.get('pwd')
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur = connection.cursor()
    query1 = "select * from userdetails where emailId='{}'".format(email)
    cur.execute(query1)
    xyz = cur.fetchone()
    print(xyz)
    if xyz == None:
        return render_template('Login.html', xyz='you are not registered')

    else:
        if password==xyz[3]:
            session['email']=email
            session['userid']=xyz[0]
            vp=xyz[1]
            #return render_template('userhome.html')
            return redirect('/home')
        else:
            return render_template('login.html', xyz='your password is not correct')

@app.route('/register', methods=['post'])
def register():
    email = request.form.get('email')
    username = request.form.get('uname')
    password = request.form.get('pwd')
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur = connection.cursor()
    query1 = "select * from userdetails where emailid='{}'".format(email)
    cur.execute(query1)
    xyz = cur.fetchone()
    if xyz == None:
        query = "insert into userdetails(emailid,username,password,is_active,created_Date) values('{}','{}','{}',1,now())".format(email,username,password)
        cur = connection.cursor()
        cur.execute(query)
        connection.commit()
        return render_template('login.html')
    else:
        return 'already registered'

@app.route('/google')
def google():
    path='F:/files/user-icon.png'
    return send_file(path, mimetype='image/png', as_attachment=true)

@app.route('/home')
def home():
    if 'userid' in session:
        email=session['email']
        id=session['userid']
        print(id)
        connection = connect(host="localhost", database="student", user="root", password="admin123")
        cur = connection.cursor()
        query1 = "select * from urlinfo where created_by={}".format(id)
        cur.execute(query1)
        data = cur.fetchall()
        print(data)
        return render_template('updateurl.html',data=data)
    return render_template('login.html')

@app.route('/editurl')
def editurl():
    if 'userid' in session:
        email=session['email']
        print(email)
        id=request.form.get("id")
        url=request.form.get("originalurl")
        encrypted=request.form.get("encrypted")
        return render_template("editurl.html", url=url, encrypted=encrypted, id=id)
    return render_template('login.html')

@app.route('/updateurl',methods=['post'])
def updateurl():
    if 'userid' in session:
        id = request.form.get('id')
        url = request.form.get('originalurl')
        encrypted = request.form.get('encrypted')
        connection = connect(host="localhost", database="student", user="root", password="admin123")
        cur = connection.cursor()
        query="select * from urlinfo where encryptedurl='{}'and pk_urlid!={}".format(encrypted, id)
        cur.execute(query)
        data=cur.fetchone()
        if data==None:
           query1="update urlinfo set originalurl='{}',encryptedurl='{}' where pk_urlid={}".format(url,encrypted,id)
           cur.execute(query1)
           connection.commit()
           return redirect('/home')
        else:
            return render_template("editurl.html", url=url, encrypted=encrypted, id=id, error='short url already exist')
    return render_template('login.html')


@app.route('/deleteurl' , methods=['post'])
def deleteurl():
    if 'userid' in session:
        id=request.form.get('id')
        connection = connect(host="localhost", database="student", user="root", password="admin123")
        cur = connection.cursor()
        query1 = "delete from urlinfo where pk_urlid="+id
        cur.execute(query1)
        connection.commit()
        return redirect('/home')
    return render_template('login.html')

@app.route('/sendmail')
def sendmail():
    msg=Message(subject='mail sender', sender='shubhamkhandelwal16102001@gmail.com', recipients=['shubhamkhandelwal.cse23@jecrc.ac.in'], body="this is my first email through python")
    msg.cc=['shivanikhandelwalbtp@gmail.com']
    msg.html=render_template('index3.html')
    with app.open_resource("E:/files/merge/favicon.jpg") as f:
        msg.attach("favicon.jpg", "image/jpg", f.read())
    mail.send(msg)
    return "mail sent!!!"

@app.route('/logout')
def logout():
    session.pop('userid',None)
    return render_template('index3.html')



@app.route('/xyzlogin',methods=['post'])
def api():
    abc=request.get_json()
    print(abc)
    list=[]
    da={}
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur = connection.cursor()
    query = "select * from urlinfo"
    cur.execute(query)
    data = cur.fetchall()
    for i in data:
        da["name"]=i[0]
        da["email"]=i[1]
        list.append(da)
    return jsonify(list)





if __name__ == "__main__":
    app.run()


