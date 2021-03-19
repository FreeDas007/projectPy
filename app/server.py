import codecs
import sqlite3
import os,sys
from datetime import datetime
import traceback
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash

# конфигурация
DATABASE = '/lesson.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

if True:
    app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'Lessons.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    tema='Python',
    logged_in=False,
    login='NoName',
    listLessons=[]))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

conn=sqlite3.connect(app.config['DATABASE'])
cur=conn.cursor()
cur.execute("""create table IF NOT EXISTS Users (
id integer primary key autoincrement,
login text not null, psw text not null,
email text not null, sex text not null,
PS text not null
); """)
conn.commit()

cur.execute("""create table IF NOT EXISTS Lessons (
id integer primary key autoincrement,
numLesson integer not null, lesson text not null,
FullName text not null, tema text not null, PS text not null
); """)
conn.commit()

cur.execute("""create table IF NOT EXISTS History (
id integer primary key autoincrement,
Dt text not null, login text not null, lesson text not null,
points integer not null, maxpoints integer not null,
trueExc integer not null, maxExc integer not null,
Ended integer not null, history text not null,
tema text not null, PS text not null
); """)
conn.commit()

cur.execute("""create table IF NOT EXISTS SetUp (
id integer primary key autoincrement,
keySet text not null, valueSet text not null
); """)
conn.commit()

#cur.execute("""drop table LogUser;""")
#conn.commit()

cur.execute("""create table IF NOT EXISTS LogUser (
id integer primary key autoincrement,
Dt text, login text, what text, what2 text,
nExc integer, timeExc integer,
nError integer, nPoint integer, nPointAll integer,
CountExc integer, SubStep integer); """)
conn.commit()

def connect_db():
    # ''' Соединяет с указанной базой данных.'''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Если ещё нет соединения с базой данных, открыть новое - для текущего контекста приложения """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def DeCode(e):
    e=e.replace('^1',"'")
    e=e.replace('^2','"')
    e=e.replace('^3',"/")
    e=e.replace('^4',"#")
    e=e.replace('^5',"\\")
    e=e.replace('^6',"?")
    e=e.replace('^7',",")
    e=e.replace('^8',".")
    e=e.replace('^9',"%")
    return e


@app.route('/')
def index():    # Вызов начальной страницы
    if 'login' in session:
        login=session['login']
    else:
        session['login']='NoName'
    session['tema']=app.config['tema']
    db=get_db()
    cur=db.execute("select numLesson,lesson,FullName,tema from Lessons where tema='Python' order by numLesson")
    listLessons=cur.fetchall()
    listX=[]; 
    objOfLessons=[]
    for e in listLessons:
        lesson=e[1] # lesson from Lessons
        FullName=e[2]
        wL=[lesson,FullName]
        listX.append(lesson)
        objOfLessons.append(wL)
    app.config['listLessons']=listX
    session['listLessons']=listX
    session['objOfLessons']=objOfLessons
    return render_template('index2.html')    #,listLessons=listLessons)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':	# вызов из формы ВОЙТИ 
        conn=sqlite3.connect(app.config['DATABASE'])
        cur=conn.cursor()
        cur.execute("select psw,sex from Users where login='"+request.form['username']+"';")
        result=cur.fetchall()
        if len(result)==0:
            error = 'Ошибка в логине:'+request.form['username']
        elif result[0][0] != request.form['password']:
            error = 'Ошибка в пароле:'+request.form['password']
        else:
            session['logged_in'] = True
            app.config['login']=request.form['username']
            session['login']=request.form['username']
            app.config['logged_in']=True
            #flash('You were logged in')
            return redirect(url_for('index'))  # Ок. На главную страницу
        return render_template('loginLesson.html', error=error) # при наличии ошибки
    else:	# нажата кнопка ВОЙТИ (GET)
        return render_template('loginLesson.html', error=error)

@app.route('/registr', methods=['GET', 'POST'])
def registr():
    error = None
    if request.method == 'POST':
        conn=sqlite3.connect(app.config['DATABASE'])
        cur=conn.cursor()
        cur.execute("select psw,sex from Users where login='"+app.config['login']+"';")
        result=cur.fetchall()
        if len(result)!=0:
            error = 'Такой логин уже есть:'+request.form['username']
        #elif result[0][0] != request.form['password']:
        #    error = 'Ошибка в пароле:'+request.form['password']
        else:
            session['logged_in'] = True
            app.config['login']=request.form['username']
            session['login']=request.form['username']
            app.config['logged_in']=True
            #app.config['PASSWORD']=request.form['password']
            #flash('You were logged in')
            cur.execute("insert into Users (login,psw,email,sex,PS) values('"+ \
                request.form['username']+"','"+request.form['password']+"','"+ \
                request.form['email']+"','s','PS');")
            conn.commit()
            return redirect(url_for('index'))  #show_entries'))
        return render_template('registrLesson.html', error=error)
    else:
        return render_template('registrLesson.html', error=error)
        
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index')) # show_entries'))

@app.route('/session')
def index2():
    return render_template('error.html', error=session)

@app.route('/config')
def Show_config():
    return render_template('error.html', error=app.config)

@app.route('/users')
def Show_users():
    conn=sqlite3.connect(app.config['DATABASE'])
    cur=conn.cursor()
    cur.execute("select * from Users order by id;")
    result=cur.fetchall()
    return render_template('Show2D.html', error=result,title='Users')

@app.route('/addlesson', methods=['GET', 'POST'])
def Add_Lesson():
    error = None
    if request.method == 'POST':
        conn=sqlite3.connect(app.config['DATABASE'])
        cur=conn.cursor()
        cur.execute("select lesson,FullName from Lessons where lesson='"+request.form['lesson'] \
            +"' and tema=='"+app.config['tema']+"';")
        result=cur.fetchall()
        if len(result)!=0:
            error = 'Такой урок уже есть:'+request.form['lesson']+' / '+request.form['FullName']
        else:
            session['listLessons'].append(request.form['lesson']) #+=","+request.form['lesson']
            app.config['listLessons']=session['listLessons']
            #flash('You were logged in')
            cur.execute("insert into Lessons (numLesson,lesson,FullName,tema,PS) values("+ \
                request.form['numLesson']+",'"+request.form['lesson']+"','"+ \
                request.form['FullName']+"','"+app.config['tema']+"','PS');")
            conn.commit()
            return redirect(url_for('index')) 
        return render_template('addLesson.html', error=error)
    else:
        return render_template('addLesson.html', error=error)

@app.route('/lessons')
def Show_Lessons():
    conn=sqlite3.connect(app.config['DATABASE'])
    cur=conn.cursor()
    cur.execute("select * from Lessons order by id;")
    result=cur.fetchall()
    return render_template('Show2D.html', error=result,title='Lessons')

@app.route('/lesson/<lesson>/', methods=['GET', 'POST'])
def Run_Lesson(lesson):
    session['CurrLesson']=lesson
    fileW=open(lesson+'.txt','r',encoding="utf-8")
    txtObj=fileW.read()
    fileW.close()
    return render_template('lesson.html', txtObj=txtObj)

@app.route('/practica/<practica>/', methods=['GET', 'POST'])
def Run_Practica(practica):
    session['CurrPractica']=practica
    fileW=open(practica+'.txt','r',encoding="utf-8")
    txtObj=fileW.read()
    fileW.close()
    return render_template('practica.html', txtObj=txtObj,how='app')

@app.route('/pdf/<pdf>') #the url you'll send the user to when he wants the pdf
def pdfviewer(pdf):
    return redirect("/static/"+pdf+".pdf")

@app.route('/script2/<txt>/', methods=['GET', 'POST'])
def RunScript2(txt):	
    errTrace=''
    txt=DeCode(txt)
    if txt=='Lesson1':  # DELETE
        # находим задание для Lesson1
        Task='Объявите пару переменных и выведите их сумму.'
        Run=[''];  out=''; Ok=''; Result=''
        return render_template('Run.html', Task=Task,Run=Run,out=out,Ok=Ok,Result=Result)
    else:
        q=1
        temp=sys.stdout
        file=open('Trace.txt','w',encoding='UTF-8')
        sys.stdout=file		#open('Trace.txt','w')
        try: 
            fileS=open('myScript.py','w',encoding='UTF-8')
            iReadWrite=False
            obj=txt.split('|||')
            for e in obj:
                fileS.write(e+'\n')
            fileS.close()
            fff='myScript.py'
            iReadWrite=True
            #exec(open(fff).read())
            fileS=open('myScript.py','r',encoding='UTF-8')
            ww=fileS.read()
            exec(ww)
            fileS.close()
            #z=compile(e,'test','exec')
            #exec(z)
        except:   # Exception as ex:
            errTrace=traceback.format_exc()  #e='????'
            #print('\n error:'+e+' \n')
        Ok='Ok'
        Task='???'
        ###if iReadWrite==True: obj=eval(txt)
        #Run=obj  #obj=eval(txt)
        ##obj=eval(txt)
        ##Run=obj
        Run=''
        Result='? ? ?'
        out='А что вы хотели?'
        #sys.stdout.close()
        file.close()
        sys.stdout=temp
        file=open('Trace.txt','r',encoding='UTF-8')
        Result=''
        ListX=file.readlines()
        for e in ListX:
            Result+=e   #+'\n'  # <br>'     #\n'
        file.close()
        for i in range(len(Run)-1):
            Run[i]=Run[i].replace('\t','')
        #Run.replace('\t','')
        return render_template('practica.html', Task=Task,Run=Run,out=out,Ok=Ok,Result=Result,
            errTrace=errTrace,how='script')   
        #return render_template('error.html', error=txt)

@app.route('/logUser/<fields>/', methods=['GET', 'POST'])
def logUser(fields):
    #return render_template('error.html', error=fields)
    LR=fields.split(',')
    LR1=str(LR)
    LR2=LR1.strip('[]')
    conn=sqlite3.connect(app.config['DATABASE'])
    cur=conn.cursor()
    DTnow=str(datetime.now())[:19]
    #DTnow = datetime.now()
    login=session['login']
    w="insert into LogUsers (login,Dt,what,what2,nExc,timeExc,nError,nPoint,nPointAll) values ('"
    w+=login+"','"+DTnow+"',";          #+LR2+");"
    w+="'"+LR[0]+"','"+LR[1]+"',"+LR[2]+","+LR[3]+","+LR[4] \
         +","+LR[5]+","+LR[6]+");"
    #return render_template('error.html', error=w)
    cur.execute(w)
    conn.commit()
    return 'Ok: '+w

    
@app.route('/logUser2/<fields>/', methods=['GET', 'POST'])
def logUser2(fields):
    #return render_template('error.html', error=fields)
    LR=fields.split(',')
    LR1=str(LR)
    LR2=LR1.strip('[]')
    conn=sqlite3.connect(app.config['DATABASE'])
    cur=conn.cursor()
    DTnow=str(datetime.now())[:19]
    #DTnow = datetime.now()
    login=session['login']
    w="insert into LogUser (login,Dt,what,what2,nExc,timeExc,nError,nPoint,nPointAll,CountExc,SubStep) values ('"
    w+=login+"','"+DTnow+"',";          #+LR2+");"
    w+="'"+LR[0]+"','"+LR[1]+"',"+LR[2]+","+LR[3]+","+LR[4] \
         +","+LR[5]+","+LR[6]+","+LR[7]+","+LR[8]+");"
    #return render_template('error.html', error=w)
    cur.execute(w)
    conn.commit()
    return 'Ok: '+w

@app.route('/ShowLogUser')
def Show_LogUser():
    conn=sqlite3.connect(app.config['DATABASE'])
    cur=conn.cursor()
    cur.execute("select * from LogUser order by id;")
    result=cur.fetchall()
    return render_template('Show2D.html', error=result,title='LogUser')

@app.route('/table/<name>/', methods=['GET', 'POST'])
def printTable(name):
    conn=sqlite3.connect(app.config['DATABASE'])
    cur=conn.cursor()
    fileX=open('PrintTable.txt','w')
    sql='select * from '+name+';'
    cur.execute(sql)
    RS=cur.description
    listNames=[]
    #print('имена полей:')
    for i,e in enumerate(RS):
        #print(i,e,e[0])
        listNames.append(e[0])
    #print('имена полей:')
    for e in listNames:
        if e=='Dt': print(e,end='\t\t\t',file=fileX)
        elif e=='what': print(e,end='\t',file=fileX)
        else: print(e,end='\t',file=fileX)
    print('',file=fileX)
    print(' ',file=fileX)

    L=cur.fetchall()
    #loginX=''; whatX=''
    for i,line in enumerate(L):
        #print(line)
        if i==0: loginX=line[2]; whatX=line[3]
        if loginX!=line[2] or whatX!=line[3]:
            loginX=line[2]; whatX=line[3]
            print(' ')
        for e in line:
            print (e,end='\t',file=fileX)
        print('',file=fileX)
        if line[4]=='Total':
            print(' ',file=fileX)
    conn.close()
    fileX.close()
    fileX=open('PrintTable.txt','r')
    ListLines=fileX.readlines()
    w=''
    for e in ListLines:
        w+=e+'\n'+'<br>'
    fileX.close()
    return w

@app.route('/run', methods=['GET', 'POST'])
def Run():
    objParams=request.args.get('lesson')
    strParam=str(objParams)
    return render_template('error.html', error=strParam)

if __name__ == "__main__":
    app.run()