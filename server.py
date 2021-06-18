from flask import Flask, render_template, request, redirect, send_file
from datetime import datetime
import sqlite3, os

now = datetime.now()

SAFE_FOLDER = '/home/pedro/Desktop/av_project/photos/'
app = Flask(__name__)

 
#DATABASE
TABLE_USERS = '''
CREATE TABLE "EMPLOYEES" ("name" TEXT, "email" TEXT, "age" INTEGER, "salary" INTEGER)
'''
TABLE_IMPROVEMENT_SUGESTIONS = '''
CREATE TABLE "SUGESTIONS" ("sugestion" TEXT, "date" TEXT)
'''
EMPLOYEES = '''INSERT INTO "EMPLOYEES" VALUES 
("Pedro", "pedro@google.com", "23", "1000"),
("Paulo", "paulo@sec.pt", "35", "1500"),
("João", "joão@markting.eu", "40", "1000"),
("Boris", "boris.hacker@proton.ru", "55", "2000"),
("Catarina", "catarina@hr.co.uk", "24", "1000") '''

try:
    conn = sqlite3.connect('av.sqlite')
    conn.execute(TABLE_USERS)
    conn.execute(TABLE_IMPROVEMENT_SUGESTIONS)
    conn.execute(EMPLOYEES)
    conn.commit()
except sqlite3.OperationalError:
    pass

#INDEX
@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')

#XSS STORED
@app.route('/xss_stored', methods=['GET'])
def xss_stored():

    conn = sqlite3.connect('av.sqlite')
    cursor = conn.cursor()
    read = ''' SELECT * FROM SUGESTIONS '''
    data = list(cursor.execute(read))

    return render_template('xss_stored.html', data=data )


@app.route('/xss_stored/vulnerable', methods=['GET', 'POST'])
def xss_stored_vul():

    date = now.strftime("%d/%m/%Y %H:%M:%S")
    
    #READ DATA
    conn = sqlite3.connect('av.sqlite')
    cursor = conn.cursor()
    read = ''' SELECT * FROM SUGESTIONS '''
    data = list(cursor.execute(read))
    print(data)
    #WRITE DATA
    if request.method == 'POST':

        sugestion = request.form['sugestion']
        INSERT = f'''
                INSERT INTO "SUGESTIONS" 
                VALUES("{sugestion}", "{date}")
                '''
        cursor.execute(INSERT)
        conn.commit()

    return render_template('xss_stored.html', data=data)


@app.route('/xss_stored/nonvulnerable', methods=['GET', 'POST'])
def xss_stored_nonvul():

    date = now.strftime("%d/%m/%Y %H:%M:%S")
    
    #READ DATA
    conn = sqlite3.connect('av.sqlite')
    cursor = conn.cursor()
    read = ''' SELECT * FROM SUGESTIONS '''
    data = list(cursor.execute(read))
    print(data)
    #WRITE DATA
    if request.method == 'POST':

        sugestion = request.form['sugestion2']
        INSERT = f'''
                INSERT INTO "SUGESTIONS" 
                VALUES("{sugestion}", "{date}")
                '''
        cursor.execute(INSERT)
        conn.commit()

    return render_template('xss_stored.html', data=data)


# XSS REFLECTED
@app.route('/xss_reflected', methods=['GET'])
def xss_reflected():
    return render_template('xss_reflected.html')

@app.route('/xss_reflected/vulnerable', methods=['GET'])
def xss_reflected_vul():

    query = None

    if request.method == 'GET':
        query = request.args.get('sugestion2')

    return render_template('xss_reflected.html', query=query)


@app.route('/xss_reflected/nonvulnerable', methods=['GET', 'POST'])
def xss_reflected_nonvul():

    query = None

    if request.method == 'POST':
        query = request.form['query']
    
    return render_template('xss_reflected.html', query2=query)

#XSS DOM
@app.route('/xss_dom', methods=['GET'])
def xss_dom():
    return render_template('xss_dom.html')


@app.route('/xss_dom/vulnerable', methods=['GET'])
def xss_dom_vul():

    query = None

    if request.method == 'GET':
        query = request.args.get('query')

    return render_template('xss_dom.html', query=query)


@app.route('/xss_dom/nonvulnerable', methods=['GET', 'POST'])
def xss_dom_nonvul():

    query = None

    if request.method == 'POST':
        query = request.form['query']
    
    return render_template('xss_dom.html', query2=query)

#SQLI
@app.route('/sqli', methods=['GET', 'POST'])
def sqli():

    return render_template('sqli.html')


@app.route('/sqli/vulnerable', methods=['GET', 'POST'])
def sqli_vul():
    #Example Query: "  UNION SELECT "salary" FROM EMPLOYEES WHERE "name"= "Pedro"  -- 
    result = None

    if request.method == 'POST':
        conn = sqlite3.connect('av.sqlite')
        cursor = conn.cursor()
        name = request.form['name']
        query = f''' SELECT email FROM EMPLOYEES WHERE name = "{name}" '''
        result = list(cursor.execute(query))

    return render_template('sqli.html', result=result, name=name)


@app.route('/sqli/nonvulnerable', methods=['GET', 'POST'])
def sqli_nonvul():
    pass



#DIRTRAV
@app.route('/dirtrav', methods=['GET', 'POST'])
def dirtrav():

    return render_template('dirtrav.html')


@app.route('/dirtrav/vulnerable/', methods=['GET', 'POST'])
def dirtrav_vul():

    name = request.args.get('image')
    return send_file(SAFE_FOLDER + name)


@app.route('/dirtrav/nonvulnerable/', methods=['GET', 'POST'])
def dirtrav_nonvul():
    pass


if __name__ == "__main__":
    app.run(debug=True)