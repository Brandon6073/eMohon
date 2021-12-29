import MySQLdb.cursors
import os
import urllib.request
import zipfile
import shutil

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, app
from flask_mysqldb import MySQL
from datetime import date, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash



app = Flask(__name__)

# your secret key (can be anything including number and symbol)
app.secret_key = 'ThisIsTheSecretKey'

# Database connection---local host
app.config['MYSQL_HOST'] = 'localhost'    # host
app.config['MYSQL_USER'] = 'rootUser'         # db user
app.config['MYSQL_PASSWORD'] = 'rootPassword'     # db password
app.config['MYSQL_DB'] = 'emohon_projek_daerah_tambunan'# db name

# Intialize MySQL
mysql = MySQL(app)

# Upload files folder
UPLOAD_FOLDER_IMAGE = 'static/images'
UPLOAD_FOLDER_DOCUMENT = 'static/documents'
ZIP_FOLDER = 'static/zip'
MAIN_FOLDER = ''

app.config['UPLOAD_FOLDER_IMAGE'] = UPLOAD_FOLDER_IMAGE
app.config['UPLOAD_FOLDER_DOCUMENT'] = UPLOAD_FOLDER_DOCUMENT
app.config['ZIP_FOLDER'] = ZIP_FOLDER
app.config['MAIN_FOLDER'] = MAIN_FOLDER

# extention allowed for the files upload
ALLOWED_EXTENSIONS_IMAGE = set(['jpg', 'jpeg','png'])
ALLOWED_EXTENSIONS_DOCUMENT = set(['pdf'])

# process the file name and extentions 
def allowed_file_gambar_1(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMAGE

def allowed_file_gambar_2(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMAGE

def allowed_file_gambar_3(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMAGE

def allowed_file_dokumen_pdf(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_DOCUMENT

# Session timeout---------------------------------------------------------------------------
@app.before_request
def make_session_permanent():

    #session timeout is set to 4 hours
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=240)

# login page------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def logMasuk():

    cur = mysql.connection.cursor()
    # Fetch data from the database
    cur.execute("SELECT kampung_id,nama_kampung FROM kampung ORDER BY nama_kampung ASC")
    data = cur.fetchall()
    cur.close()



    # check userdetails
    if request.method == 'POST' and 'kampung_id' in request.form and 'ic_pengguna' in request.form and 'kata_laluan' in request.form:
        
        # Variables for easier access
        kampung_id = request.form['kampung_id']
        ic_pengguna = request.form['ic_pengguna']
        kata_laluan = request.form['kata_laluan']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#retrieve data in dictionary form(include column name) instead of tuple
        cursor.execute('SELECT * FROM pengguna WHERE kampung_id = %s AND ic_pengguna = %s ', (kampung_id, ic_pengguna))
        
        # Fetch a record and return result
        user = cursor.fetchone()
        cursor.close()
        #Check if user exist in the database
        if user:

            if check_password_hash(user['kata_laluan'], kata_laluan):
                # Create session data
                session['loggedin'] = True
                session['ic_pengguna'] = user['ic_pengguna']
                session['nama_pengguna'] = user['nama_pengguna']
                session['jenis_pengguna'] = user['jenis_pengguna']
                session['kampung_id'] = user['kampung_id']

                # Redirect based on the user type
                # user 1-(User/Pengguna) Only able to fill up the permohonan form 
                # user 2-(Management/Pengurus) Able to view the report, add and modify data in the system 
                # user 3-(Admin/Penyelengara) Able to do all user 2 task and delete data in the system

                if session['jenis_pengguna'] is 1:
                    return redirect(url_for('permohonan'))# redirect to permohonan form
                elif session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
                    return redirect(url_for('menu'))#redirect to a page with menu
                 
            else:
                flash('NO NIRC/KATA LALUAN TIDAK SAH', category='error')
                return render_template('logMasuk.html', data=data)

        else:
        # Account doesnt exist or username/password incorrect
            flash('LOG MASUK TIDAK BERJAYA', category='error')
                      
    return render_template('logMasuk.html', data=data)



#Register new users----------------------------------------------------------------------------------
@app.route('/daftar_pengguna', methods=['GET', 'POST'])
def daftar_pengguna():

    # retrieve kampung data from the database to be used as an input
    cur = mysql.connection.cursor()
    cur.execute("SELECT kampung_id,nama_kampung FROM kampung ORDER BY nama_kampung ASC")
    data_kampung = cur.fetchall()
    cur.close()

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    # Check user type
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:

        #check user type for different interface display
        if session['jenis_pengguna'] is 3 or session['jenis_pengguna'] is 2:
            user = True
        else: 
            user = False

        if request.method == 'POST' and 'kampung_id' in request.form and 'ic_pengguna' in request.form and 'nama_pengguna' in request.form and 'jenis_pengguna' in request.form:
            
            # Variable for easy access
            kampung_id = request.form['kampung_id']
            ic_pengguna = request.form['ic_pengguna']
            nama_pengguna = request.form['nama_pengguna']
            jenis_pengguna = request.form['jenis_pengguna']
            kata_laluan = request.form['kata_laluan']

            #change strings to uppercase
            kampung_id = kampung_id.upper()
            nama_pengguna = nama_pengguna.upper()
            #password using SHA256
            hashed_password = generate_password_hash(kata_laluan,method = 'sha256')
            
            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM pengguna WHERE ic_pengguna = %s', (ic_pengguna,))
            user = cursor.fetchone()
            cursor.close()

            # If account exists show error and validation checks
            if user:
               flash('PENGGUNA TELAH WUJUD', category='error')

            elif not kampung_id or not ic_pengguna or not nama_pengguna or not jenis_pengguna or not kata_laluan:
                flash('SILA ISI BORANG SEPENUHNYA', category='error')
            else:
                
                # If the user doen't not exist, add new user
                cursor.execute('INSERT INTO pengguna VALUES (%s, %s, %s, %s, %s)', (ic_pengguna ,kampung_id,  nama_pengguna, jenis_pengguna,hashed_password))
                mysql.connection.commit()
                cursor.close()
                flash('PENDAFTARAN TELAH BERJAYA', category='success')

        elif request.method == 'POST':
            # If the form is empty
            flash('SILA ISI BORANG', category='error')
  
        return render_template('daftar_pengguna.html', user=user, data_kampung = data_kampung)

    # User is not loggedin and invalid user type, redirect to unauthorized user page
    return redirect(url_for('akses_dinafikan'))  



#Register new kampung----------------------------------------------------------------------------------
@app.route('/daftar_kampung', methods=['GET', 'POST'])
def daftar_kampung():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

     # Check user type
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:

        if request.method == 'POST' and 'nama_kampung' in request.form and 'nama_mukim' in request.form:
            
            # Variable for easy access
            nama_kampung = request.form['nama_kampung']
            nama_mukim = request.form['nama_mukim']

            #change strings to uppercase
            nama_kampung = nama_kampung.upper()
            nama_mukim = nama_mukim.upper()
            
            # Check if account exists using MySQL
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM kampung WHERE nama_kampung = %s', (nama_kampung,))
            kampung = cur.fetchone()
            cur.close()
            
            # If account exists show error and validation checks
            if kampung:
               flash('KAMPUNG DENGAN NAMA YANG SAMA TELAH WUJUD', category='error')

            elif not nama_kampung or not nama_mukim:
                flash('SILA ISI BORANG SEPENUHNYA', category='error')
            else:
                # If the user doen't not exist, add new user
                cur.execute('INSERT INTO kampung VALUES (null, %s, %s)', (nama_kampung, nama_mukim))
                mysql.connection.commit()
                cur.close()
                flash('MAKLUMAT KAMPUNG TELAH DISIMPAN', category='success')

        elif request.method == 'POST':
            # If the form is empty
            flash('SILA ISI BORANG', category='error')
  
        return render_template('daftar_kampung.html')

    # User is not loggedin redirect to unauthorized user page
    return redirect(url_for('akses_dinafikan'))  
    


#Borang Permohonan-------------------------------------------------------------------------------
@app.route('/permohonan', methods=['GET', 'POST'])
def permohonan():

    cur = mysql.connection.cursor()
    cur.execute("SELECT kampung.kampung_id,kampung.nama_kampung FROM kampung JOIN pengguna on kampung.kampung_id = pengguna.kampung_id ORDER BY nama_kampung ASC")
    data_kampung = cur.fetchall()

    cur.execute("SELECT jenis_permohonan FROM jenispermohonan ORDER BY jenis_permohonan ASC")
    data_jenis_permohonan = cur.fetchall()
    cur.close()

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    # Check if user is loggedin and user type(user 1 and user 3)
    if 'loggedin' in session and session['jenis_pengguna'] is 1:

        if request.method == 'POST' and 'jenis_permohonan' in request.form and 'bil_ukuran_keluasan' in request.form and 'justifikasi' in request.form:

            # Create variables for easy access

            # id_permohonan is managed by database with increment and unique number
            # kampung and mukim from pengguna table
            bil_ukuran_keluasan = request.form['bil_ukuran_keluasan']
            justifikasi = request.form['justifikasi']
            #IC number is taken from the "pengguna" table
            jenis_permohonan = request.form['jenis_permohonan']

            tarikh = date.today()
            #tarikh is automatically set using today's date

            #change string to uppercase
            bil_ukuran_keluasan = bil_ukuran_keluasan.upper()
            justifikasi = justifikasi.upper()
            jenis_permohonan = jenis_permohonan.upper()

            #define the upload file taken from the input
            file1 = request.files.get('gambar_1')#  gambar 1
            file2 = request.files.get('gambar_2')#  gambar 2
            file3 = request.files.get('gambar_3')#  gambar 3
            file4 = request.files.get('dokumen_pdf')# dokument_pdf

            # Check if account exists using MySQl
            cur = mysql.connection.cursor()

            if not jenis_permohonan or not bil_ukuran_keluasan or not justifikasi or not tarikh or not file1 or not file2 or not file3 or not file4:
                flash('SILA ISI BORANG SEPENUHNYA', category='error')

            #if the format is incorrect, the file cannot be stored
            elif not allowed_file_gambar_1(file1.filename) or not allowed_file_gambar_2(file2.filename) or not allowed_file_gambar_3(file3.filename) or not allowed_file_dokumen_pdf(file4.filename):
                flash('SILA MASUKKAN FORMAT YANG BETUL', category='error')

            else:
                ic_pengguna= session['ic_pengguna'] 
                nama_pengguna = session['nama_pengguna']
                kampung_id = session['kampung_id']
                #the rename format is "IC_pengguna-tarikh_upload-[hadapan/belakang/sisi]-filename"
                #this is so it is easier for the system to find the target files in the server by name

                gambar_1 = ic_pengguna+"-"+ str(tarikh) + "-hadapan-" + secure_filename(file1.filename)#rename the image 1
                file1.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))
                gambar_2 = ic_pengguna+"-"+ str(tarikh) + "-belakang-" + secure_filename(file2.filename)#rename the image 2
                file2.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))
                gambar_3 = ic_pengguna +"-"+ str(tarikh) + "-sisi-" + secure_filename(file3.filename)#rename the image 3
                file3.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))

                dokumen_pdf =ic_pengguna+"-"+str(tarikh)+"-dokumen-"+ secure_filename(file4.filename)#rename the document
                file4.save(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))
                
                # If the data doen't exist and valid, add the data in the table
                cur.execute('INSERT INTO permohonan VALUES (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',\
                (nama_pengguna,kampung_id, jenis_permohonan, bil_ukuran_keluasan, justifikasi,ic_pengguna, tarikh,gambar_1,gambar_2,gambar_3,dokumen_pdf))

                mysql.connection.commit()
                cur.close()
                flash('PERMOHONAN ANDA TELAH BERJAYA DIHANTAR.', category='success')

        return render_template('permohonan.html',data_kampung=data_kampung,data_jenis_permohonan=data_jenis_permohonan)

    return redirect(url_for('akses_dinafikan'))   
    


#Laporan projek----------------------------------------------------------------------------------
@app.route("/laporan_projek",methods=['GET', 'POST'])
def laporan_projek():
    #select the data from database for filtering(no duplicate)
    cur = mysql.connection.cursor()
    tarikh_sekarang = date.today()
    tahun_sekarang = tarikh_sekarang.year
    
    cur.execute("SELECT DISTINCT YEAR(tarikh) FROM permohonan ORDER BY YEAR(tarikh) ASC")
    data_tahun = cur.fetchall()
    
    cur.execute("SELECT DISTINCT nama_mukim FROM kampung ORDER BY nama_mukim ASC")
    data_mukim = cur.fetchall()

    cur.execute("SELECT DISTINCT nama_kampung FROM kampung ORDER BY nama_kampung ASC")
    data_kampung = cur.fetchall()
    cur.close()

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

        # Check if user is loggedin
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
        # check user type for display
        if session['jenis_pengguna'] is 3 :
            user = True
        else: 
            user = False

        headings="ID PERMOHONAN","NAMA","KAMPUNG","MUKIM","JENIS PERMOHONAN","BIL/UKURAN/KELUASAN","JUSTIFIKASI PERMOHONAN","NO. KAD PENGENALAN","TARIKH","GAMBAR 1 (HADAPAN)","GAMBAR 2 (BELAKANG)","GAMBAR 3 (SISI","BORANG PDF"," "," "
        cur = mysql.connection.cursor()
        cur.execute("SELECT permohonan.id_permohonan,permohonan.nama_pengguna,kampung.nama_kampung, kampung.nama_mukim,permohonan.jenis_permohonan,permohonan.bil_ukuran_keluasan,permohonan.justifikasi,permohonan.ic,DATE_FORMAT(permohonan.tarikh, \"%d-%m-%Y\"), permohonan.gambar_1,permohonan.gambar_2,permohonan.gambar_3,permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id ORDER BY permohonan.id_permohonan ASC")
        data = cur.fetchall()
        cur.close()

        return render_template('laporan_projek.html',tahun_sekarang=tahun_sekarang,tarikh_sekarang=tarikh_sekarang,user=user,headings=headings, data=data , data_mukim = data_mukim, data_tahun= data_tahun, data_kampung = data_kampung)
 
    # User is not loggedin redirect to unauthorized page
    return redirect(url_for('akses_dinafikan')) 



#update senarai after filtering -----------------------------------------------------------
@app.route("/cari_laporan",methods=['GET', 'POST'])
def cari_laporan():

    cur = mysql.connection.cursor()
    tarikh_sekarang = date.today()
    tahun_sekarang = tarikh_sekarang.year

    #select the data from database for filtering(no duplicate)
    
    cur.execute("SELECT DISTINCT YEAR(tarikh) FROM permohonan ORDER BY YEAR(tarikh) ASC")
    data_tahun = cur.fetchall()

    cur.execute("SELECT DISTINCT nama_mukim FROM kampung ORDER BY nama_mukim ASC")
    data_mukim = cur.fetchall()
    
    cur.execute("SELECT DISTINCT nama_kampung FROM kampung ORDER BY nama_kampung ASC")
    data_kampung = cur.fetchall()
    cur.close()

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))
    
    # Check if user is loggedin and the user is type 2 or 3
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
        if session['jenis_pengguna'] is 3 :
            user = True
        else: 
            user = False

        cari_tahun = request.form['cari_tahun']
        cari_mukim = request.form['cari_mukim']
        cari_kampung = request.form['cari_kampung']

        #table heading
        headings="ID Permohonan","Nama","Kampung","Mukim","Jenis Permohonan","Bil/Ukuran/Keluasan","Justifikasi Permohonan","No. Kad Pengenalan","Tarikh","Gambar 1","Gambar 2","Gambar 3","Borang pdf","Muat Turun"
        cur = mysql.connection.cursor()

        if cari_mukim is not"" and cari_kampung is "" and cari_tahun is "":
            cur.execute("SELECT permohonan.id_permohonan,permohonan.nama_pengguna,kampung.nama_kampung, kampung.nama_mukim,permohonan.jenis_permohonan,permohonan.bil_ukuran_keluasan,permohonan.justifikasi,permohonan.ic,permohonan.tarikh, permohonan.gambar_1,permohonan.gambar_2,permohonan.gambar_3,permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id  WHERE nama_mukim = %s ORDER BY permohonan.id_permohonan ASC",(cari_mukim,))
        
            #Search based on mukim
            flash('MUKIM: '+cari_mukim, category='success')

        elif cari_kampung is not "" and cari_mukim is "" and cari_tahun is "":
            cur.execute("SELECT permohonan.id_permohonan,permohonan.nama_pengguna,kampung.nama_kampung, kampung.nama_mukim,permohonan.jenis_permohonan,permohonan.bil_ukuran_keluasan,permohonan.justifikasi,permohonan.ic,permohonan.tarikh, permohonan.gambar_1,permohonan.gambar_2,permohonan.gambar_3,permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id WHERE nama_kampung = %s ORDER BY permohonan.id_permohonan ASC",(cari_kampung,))
  
            #Search based on kampung
            flash('KAMPUNG: '+cari_kampung, category='success')

        elif cari_tahun is not "" and cari_mukim is "" and cari_kampung is "":
            cur.execute("SELECT permohonan.id_permohonan,permohonan.nama_pengguna,kampung.nama_kampung, kampung.nama_mukim,permohonan.jenis_permohonan,permohonan.bil_ukuran_keluasan,permohonan.justifikasi,permohonan.ic,permohonan.tarikh, permohonan.gambar_1,permohonan.gambar_2,permohonan.gambar_3,permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id WHERE YEAR(tarikh) = %s ORDER BY permohonan.id_permohonan ASC",(cari_tahun,))
  
            #Search based on year
            flash('TAHUN : '+cari_tahun, category='success')

        elif cari_kampung is not "" and cari_mukim is not "" and cari_tahun is "":
            cur.execute("SELECT permohonan.id_permohonan,permohonan.nama_pengguna,kampung.nama_kampung, kampung.nama_mukim,permohonan.jenis_permohonan,permohonan.bil_ukuran_keluasan,permohonan.justifikasi,permohonan.ic,permohonan.tarikh, permohonan.gambar_1,permohonan.gambar_2,permohonan.gambar_3,permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id WHERE nama_mukim = %s AND nama_kampung = %s ORDER BY permohonan.id_permohonan ASC",(cari_mukim,cari_kampung))
            #Search based on kampung and mukim
            flash('KAMPUNG: '+cari_kampung+', MUKIM: '+ cari_mukim, category='success')

        elif cari_kampung is not "" and cari_mukim is "" and cari_tahun is not "":
            cur.execute("SELECT permohonan.id_permohonan,permohonan.nama_pengguna,kampung.nama_kampung, kampung.nama_mukim,permohonan.jenis_permohonan,permohonan.bil_ukuran_keluasan,permohonan.justifikasi,permohonan.ic,permohonan.tarikh, permohonan.gambar_1,permohonan.gambar_2,permohonan.gambar_3,permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id WHERE nama_kampung = %s AND YEAR(tarikh) =%s ORDER BY permohonan.id_permohonan ASC",(cari_kampung, cari_tahun))
            
            #Search based on  kampung and year
            flash('KAMPUNG: '+cari_kampung+', TAHUN: '+ cari_tahun, category='success')

        elif cari_kampung is "" and cari_mukim is not "" and cari_tahun is not "":
            cur.execute("SELECT permohonan.id_permohonan,permohonan.nama_pengguna,kampung.nama_kampung, kampung.nama_mukim,permohonan.jenis_permohonan,permohonan.bil_ukuran_keluasan,permohonan.justifikasi,permohonan.ic,permohonan.tarikh, permohonan.gambar_1,permohonan.gambar_2,permohonan.gambar_3,permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id WHERE nama_mukim = %s AND YEAR(tarikh) =%s ORDER BY permohonan.id_permohonan ASC",(cari_mukim, cari_tahun))
              
            #Search based on mukim and year
            flash('MUKIM: '+cari_mukim+', TAHUN: '+ cari_tahun, category='success')

        elif cari_kampung is not "" and cari_mukim is not "" and cari_tahun is not "":
            cur.execute("SELECT permohonan.id_permohonan,permohonan.nama_pengguna,kampung.nama_kampung, kampung.nama_mukim,permohonan.jenis_permohonan,permohonan.bil_ukuran_keluasan,permohonan.justifikasi,permohonan.ic,permohonan.tarikh, permohonan.gambar_1,permohonan.gambar_2,permohonan.gambar_3,permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id WHERE nama_mukim = %s AND nama_kampung = %s  AND YEAR(tarikh) =%s ORDER BY permohonan.id_permohonan ASC",(cari_mukim,cari_kampung, cari_tahun))
          
            #Search based on mukim and year
            flash('MUKIM : '+cari_mukim+', KAMPUNG: '+ cari_kampung+', TAHUN: '+ cari_tahun, category='success')

        else:
            cur.execute("SELECT permohonan.id_permohonan,permohonan.nama_pengguna,kampung.nama_kampung, kampung.nama_mukim,permohonan.jenis_permohonan,permohonan.bil_ukuran_keluasan,permohonan.justifikasi,permohonan.ic,permohonan.tarikh, permohonan.gambar_1,permohonan.gambar_2,permohonan.gambar_3,permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id ORDER BY permohonan.id_permohonan ASC")
          
            #no searching

        data = cur.fetchall()
        cur.close()

        return render_template('laporan_projek.html',user=user,tahun_sekarang = tahun_sekarang,tarikh_sekarang=tarikh_sekarang,headings=headings, data=data, cari_kampung = cari_kampung, cari_mukim = cari_kampung, cari_tahun = cari_tahun, data_mukim = data_mukim, data_tahun= data_tahun, data_kampung = data_kampung)

    # User is not loggedin redirect to access denied
    return redirect(url_for('akses_dinafikan')) 



#page for kemaskini projek
@app.route('/kemaskini_permohonan', methods = ['POST', 'GET'])
def kemaskini_permohonan():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
        
        #retrieve the existing data
        id_permohonan = request.form['id_permohonan'] 

        cur = mysql.connection.cursor()
        cur.execute("SELECT kampung_id,nama_kampung FROM kampung ORDER BY nama_kampung ASC")
        data_kampung = cur.fetchall()

        cur.execute("SELECT jenis_permohonan FROM jenispermohonan ORDER BY jenis_permohonan ASC")
        data_jenis_permohonan = cur.fetchall()
         
        cur.execute("SELECT permohonan.id_permohonan, permohonan.ic,permohonan.nama_pengguna, kampung.kampung_id, kampung.nama_kampung, permohonan.jenis_permohonan, permohonan.tarikh, permohonan.bil_ukuran_keluasan, permohonan.justifikasi, permohonan.gambar_1, permohonan.gambar_2, permohonan.gambar_3, permohonan.dokumen_pdf FROM permohonan JOIN kampung ON permohonan.kampung_id = kampung.kampung_id  WHERE id_permohonan = %s" ,(id_permohonan,))
        data = cur.fetchall()
        cur.close()

        return render_template('kemaskini_permohonan.html', data = data,data_kampung=data_kampung,data_jenis_permohonan =data_jenis_permohonan)
    
    # User is not loggedin redirect to unauthorized page
    return redirect(url_for('akses_dinafikan')) 



#kemaskini permohonan
@app.route("/kemaskini_data_permohonan", methods=['GET', 'POST'])
def kemaskini_data_permohonan():
    #the zip files only updated if the user execute "Download_all" button.
    
    #update data
    id_permohonan = request.form['id_permohonan']
    kampung_id = request.form['kampung_id']    
    jenis_permohonan = request.form['jenis_permohonan']
    bil_ukuran_keluasan = request.form['bil_ukuran_keluasan']
    justifikasi = request.form['justifikasi']
    ic = request.form['ic']
    tarikh = date.today()

    #define the upload file taken from the input
    file1 = request.files.get('gambar_1')#  gambar 1
    file2 = request.files.get('gambar_2')#  gambar 2
    file3 = request.files.get('gambar_3')#  gambar 3
    file4 = request.files.get('dokumen_pdf')# dokument_pdf

    jenis_permohonan = jenis_permohonan.upper() 
    bil_ukuran_keluasan = bil_ukuran_keluasan.upper() 
    justifikasi = justifikasi.upper()
    
    #to delete existing files
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM permohonan WHERE id_permohonan = %s",(id_permohonan,))
    data = cur.fetchone()
    gambar_1_former = data['gambar_1']
    gambar_2_former = data['gambar_2']
    gambar_3_former = data['gambar_3']
    dokumen_pdf_former = data['dokumen_pdf']
    ic = data['ic']
    cur.close()

    cur = mysql.connection.cursor()

    #all possible combination
    if file1:#file1 and file2, file1 and file3, file1 and file4, file1

        if file1 and file2:#file1 and file2 and file3, file1 and file2 and file4, file1 and file2
           
            if file1 and file2 and file3 and file4:

                #delete and add new file
                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1_former))
                gambar_1 = ic+"-"+ str(tarikh) + "-hadapan-" + secure_filename(file1.filename)#rename the image
                file1.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2_former))
                gambar_2 = ic+"-"+ str(tarikh) + "-belakang-" + secure_filename(file2.filename)#rename the image
                file2.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3_former))
                gambar_3 = ic +"-"+ str(tarikh) + "-sisi-" + secure_filename(file3.filename)#rename the image
                file3.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf_former))
                dokumen_pdf =ic+"-"+str(tarikh)+"-dokumen-"+ secure_filename(file4.filename)#rename the document
                file4.save(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))

                cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_1 = %s, gambar_2 = %s,gambar_3 = %s,dokumen_pdf = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_1,gambar_2,gambar_3,dokumen_pdf, id_permohonan))

            elif file1 and file2 and file3:#file1 and file2 and file3, all

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1_former))
                gambar_1 = ic+"-"+ str(tarikh) + "-hadapan-" + secure_filename(file1.filename)#rename the image
                file1.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2_former))
                gambar_2 = ic+"-"+ str(tarikh) + "-belakang-" + secure_filename(file2.filename)#rename the image
                file2.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3_former))
                gambar_3 = ic +"-"+ str(tarikh) + "-sisi-" + secure_filename(file3.filename)#rename the image
                file3.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))

                cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_1 = %s, gambar_2 = %s,gambar_3 = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_1,gambar_2,gambar_3, id_permohonan))

            elif file1 and file2 and file4 and not file3:

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1_former))
                gambar_1 = ic+"-"+ str(tarikh) + "-hadapan-" + secure_filename(file1.filename)#rename the image
                file1.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2_former))
                gambar_2 = ic+"-"+ str(tarikh) + "-belakang-" + secure_filename(file2.filename)#rename the image
                file2.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf_former))
                dokumen_pdf =ic+"-"+str(tarikh)+"-dokumen-"+ secure_filename(file4.filename)#rename the document
                file4.save(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))

                cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_1 = %s, gambar_2 = %s,dokumen_pdf = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_1,gambar_2,dokumen_pdf, id_permohonan))

            else:
                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1_former))
                gambar_1 = ic+"-"+ str(tarikh) + "-hadapan-" + secure_filename(file1.filename)#rename the image
                file1.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2_former))
                gambar_2 = ic+"-"+ str(tarikh) + "-belakang-" + secure_filename(file2.filename)#rename the image
                file2.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))

                cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_1 = %s, gambar_2 = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_1,gambar_2,id_permohonan))


        elif file1 and file3: 
            
            if file1 and file3 and file4:
                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1_former))
                gambar_1 = ic+"-"+ str(tarikh) + "-hadapan-" + secure_filename(file1.filename)#rename the image
                file1.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3_former))
                gambar_3 = ic +"-"+ str(tarikh) + "-sisi-" + secure_filename(file3.filename)#rename the image
                file3.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf_former))
                dokumen_pdf =ic+"-"+str(tarikh)+"-dokumen-"+ secure_filename(file4.filename)#rename the document
                file4.save(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))

                cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_1 = %s, gambar_3 = %s,dokumen_pdf = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_1,gambar_3,dokumen_pdf, id_permohonan))

            else:
                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1_former))
                gambar_1 = ic+"-"+ str(tarikh) + "-hadapan-" + secure_filename(file1.filename)#rename the image
                file1.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))

                os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3_former))
                gambar_3 = ic +"-"+ str(tarikh) + "-sisi-" + secure_filename(file3.filename)#rename the image
                file3.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))

                cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_1 = %s, gambar_3 = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_1,gambar_3,id_permohonan))


        elif file1 and file4:
            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1_former))
            gambar_1 = ic+"-"+ str(tarikh) + "-hadapan-" + secure_filename(file1.filename)#rename the image
            file1.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))

            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf_former))
            dokumen_pdf =ic+"-"+str(tarikh)+"-dokumen-"+ secure_filename(file4.filename)#rename the document
            file4.save(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))

            cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_1 = %s, dokumen_pdf = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_1,dokumen_pdf,id_permohonan))


        else: 
            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1_former))
            gambar_1 = ic+"-"+ str(tarikh) + "-hadapan-" + secure_filename(file1.filename)#rename the image
            file1.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))

            cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_1 = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_1,id_permohonan))


    elif file2:#file2 and file3, file2 and file4, file2

        if file2 and file3 and not file4: 
            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2_former))
            gambar_2 = ic+"-"+ str(tarikh) + "-belakang-" + secure_filename(file2.filename)#rename the image
            file2.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))

            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3_former))
            gambar_3 = ic +"-"+ str(tarikh) + "-sisi-" + secure_filename(file3.filename)#rename the image
            file3.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))

            cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_2 = %s, gambar_3 = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_2,gambar_3,id_permohonan))
        
        elif file2 and file3 and file4: 
            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2_former))
            gambar_2 = ic+"-"+ str(tarikh) + "-belakang-" + secure_filename(file2.filename)#rename the image
            file2.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))

            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3_former))
            gambar_3 = ic +"-"+ str(tarikh) + "-sisi-" + secure_filename(file3.filename)#rename the image
            file3.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))
            
            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf_former))
            dokumen_pdf =ic+"-"+str(tarikh)+"-dokumen-"+ secure_filename(file4.filename)#rename the document
            file4.save(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))

            cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_2 = %s, gambar_3 = %s, dokumen_pdf = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_2,gambar_3,dokumen_pdf,id_permohonan))
        
        elif file2 and file4:
            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2_former))
            gambar_2 = ic+"-"+ str(tarikh) + "-belakang-" + secure_filename(file2.filename)#rename the image
            file2.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))

            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf_former))
            dokumen_pdf =ic+"-"+str(tarikh)+"-dokumen-"+ secure_filename(file4.filename)#rename the document
            file4.save(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))

            cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_2 = %s, dokumen_pdf = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_2,dokumen_pdf,id_permohonan))

        else: 
            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2_former))
            gambar_2 = ic+"-"+ str(tarikh) + "-belakang-" + secure_filename(file2.filename)#rename the image
            file2.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))

            cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_2 = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_2,id_permohonan))
    

    elif file3:#file3 and file4, file3

        if file3 and file4:

            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3_former))
            gambar_3 = ic +"-"+ str(tarikh) + "-sisi-" + secure_filename(file3.filename)#rename the image
            file3.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))

            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf_former))
            dokumen_pdf =ic+"-"+str(tarikh)+"-dokumen-"+ secure_filename(file4.filename)#rename the document
            file4.save(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))

            cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_3 = %s, dokumen_pdf = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_3,dokumen_pdf,id_permohonan))

        else: 
            os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3_former))
            gambar_3 = ic +"-"+ str(tarikh) + "-sisi-" + secure_filename(file3.filename)#rename the image
            file3.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))

            cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, gambar_3 = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,gambar_3,id_permohonan))


    elif file4:
        os.unlink(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf_former))
        dokumen_pdf =ic+"-"+str(tarikh)+"-dokumen-"+ secure_filename(file4.filename)#rename the document
        file4.save(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))

        cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s, dokumen_pdf = %s  WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh,dokumen_pdf,id_permohonan))


    else: 
        cur.execute('UPDATE permohonan SET kampung_id = %s, jenis_permohonan = %s, bil_ukuran_keluasan = %s, justifikasi = %s, tarikh = %s WHERE id_permohonan = %s',(kampung_id,jenis_permohonan,bil_ukuran_keluasan,justifikasi,tarikh ,id_permohonan))
                
    mysql.connection.commit()
    cur.close()
    flash("KEMASKINI TELAH BERJAYA",category='success')
    return redirect(url_for('laporan_projek')) 

 

#Delete project----------------------------------------------------------------------------------
@app.route("/hapus_permohonan",methods=['GET', 'POST'])
def hapus_permohonan():

    #delete the existing project data
    id_permohonan = request.form['id_permohonan']

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM permohonan WHERE id_permohonan = %s",(id_permohonan,))
    data = cur.fetchone()
    gambar_1 = data['gambar_1']
    gambar_2 = data['gambar_2']
    gambar_3 = data['gambar_3']
    dokumen_pdf = data['dokumen_pdf']
    ic = data['ic']
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM permohonan WHERE id_permohonan = %s',(id_permohonan,))
    
    #delete the actual file in the server
    os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1))
    os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2))
    os.unlink(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3))
    os.unlink(os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf))
    
    #if zip file haven't been created and doen't exist, continue without error
    try:
        os.unlink(os.path.join(app.config['ZIP_FOLDER'], id_permohonan+"-"+ic+".zip"))
    except:
        pass
    
    mysql.connection.commit()
    cur.close()
    
    flash('PERMOHONAN TELAH BERJAYA DIHAPUSKAN', category='success')

    return redirect(url_for('laporan_projek'))



#Menu page(For pernyelengara and pergurusan only only)----------------------------------------------------------------------------
@app.route('/menu')
def menu():
    
    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    # Check if user is loggedin
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
        # User is loggedin show them the home page

        return render_template('menu.html')

    return redirect(url_for('akses_dinafikan')) 
    


#page for unauthorized user----------------------------------------------------------------
@app.route("/akses_dinafikan")
def akses_dinafikan():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    #show return button for user 2 and 3
    if session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
        user = True
    else: 
        user = False
    
    return render_template('akses_dinafikan.html', user=user)



#check uploaded files-------------------------------------------------------------------------
@app.route("/periksa_fail",methods=['GET', 'POST'])
def periksa_fail():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    #check loggedin and the user type 
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
        
        #take the id_permohonan from table
        id_permohonan = request.form['periksa']

        #use dictCursor
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM permohonan WHERE id_permohonan = %s ', (id_permohonan,))
               
        # Fetch one record and return result
        permohonan_view = cursor.fetchone()
        cursor.close()

        #declare the files names from the database
        gambar_1 = permohonan_view['gambar_1']
        gambar_2 = permohonan_view['gambar_2']
        gambar_3 = permohonan_view['gambar_3']

        dokumen_pdf= permohonan_view['dokumen_pdf']
           
        #locate the storage of the file
        gambar1 = os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1)
        gambar2 = os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2)
        gambar3 = os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3)

        dokumenPdf = os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf)

        return render_template('periksa_fail.html',gambar1=gambar1,gambar2=gambar2,gambar3=gambar3,dokumenPdf=dokumenPdf) 
          
    return redirect(url_for('akses_dinafikan')) 





@app.route('/download_all',methods=['GET', 'POST'])
def download_all():

    #take the id_permohonan from table
    id_permohonan = request.form['periksa']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM permohonan WHERE id_permohonan = %s ', (id_permohonan,))

    # Fetch one record and return result
    permohonan_view = cursor.fetchone()
    cursor.close()

    #for file name
    ic_pengguna = permohonan_view['ic']

    #declare the files names from the database
    gambar_1 = permohonan_view['gambar_1']
    gambar_2 = permohonan_view['gambar_2']
    gambar_3 = permohonan_view['gambar_3']

    dokumen_pdf= permohonan_view['dokumen_pdf']  
    #locate the storage of the file
    gambar1 = os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_1)
    gambar2 = os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_2)
    gambar3 = os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], gambar_3)

    dokumenPdf = os.path.join(app.config['UPLOAD_FOLDER_DOCUMENT'], dokumen_pdf)

    file_List = [gambar1,gambar2,gambar3,dokumenPdf]
    
    #creating the zip files for the uploaded files
    #os.chdir(app.config['ZIP_FOLDER'] )
    with zipfile.ZipFile(str(id_permohonan)+'-'+str(ic_pengguna)+ '.zip', 'w') as myzip:
        for f in file_List:   
            myzip.write(f)
    #move the zip to a folder
    shutil.move(os.path.join(app.config['MAIN_FOLDER'],id_permohonan+'-'+ic_pengguna+'.zip'),os.path.join(app.config['ZIP_FOLDER'], id_permohonan+'-'+ic_pengguna+'.zip'))
    #locate the storage of the file
    download_all = os.path.join(app.config['ZIP_FOLDER'], id_permohonan+'-'+ic_pengguna+'.zip')

    return send_file (download_all,as_attachment= True)



#Muat Turun gambar 1-----------------------------------------------------------------------------
@app.route('/muat_turun_gambar_1',methods=['GET', 'POST'])
def muat_turun_gambar_1():
    gambar1 = request.form['gambar1']

    return send_file (gambar1,as_attachment= True)



#Muat Turun gambar 2-----------------------------------------------------------------------------
@app.route('/muat_turun_gambar_2',methods=['GET', 'POST'])
def muat_turun_gambar_2():
    gambar2 = request.form['gambar2']

    return send_file (gambar2,as_attachment= True)



#Muat Turun gambar 3-----------------------------------------------------------------------------
@app.route('/muat_turun_gambar_3',methods=['GET', 'POST'])
def muat_turun_gambar_3():
    gambar3 = request.form['gambar3']

    return send_file (gambar3,as_attachment= True)



#Muat Turun dokumen pdf-----------------------------------------------------------------------------
@app.route('/muat_turun_dokumen_pdf',methods=['GET', 'POST'])
def muat_turun_dokumen_pdf():
    dokumenPdf = request.form['dokumenPdf']

    return send_file (dokumenPdf,as_attachment= True)



#maklumat pengguna----------------------------------------------------------------------------------
@app.route("/maklumat_pengguna",methods=['GET', 'POST'])
def maklumat_pengguna():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    # Check if user is loggedin
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
        #check user type for display
        if session['jenis_pengguna'] is 3 :
            user = True
        else: 
            user = False

        headings="NO.","NO. KAD PENGENALAN","NAMA","KAMPUNG ID","NAMA KAMPUNG","NAMA MUKIM","JENIS PENGGUNA"," "
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT pengguna.ic_pengguna,pengguna.nama_pengguna,kampung.kampung_id,kampung.nama_kampung, kampung.nama_mukim,pengguna.jenis_pengguna FROM pengguna JOIN kampung ON kampung.kampung_id = pengguna.kampung_id ")
        data = cur.fetchall()
        cur.close()
        return render_template('maklumat_pengguna.html',user=user,headings=headings, data=data )

    # User is not loggedin redirect to unauthorized page
    return redirect(url_for('akses_dinafikan')) 



#page for kemaskini pengguna
@app.route('/kemaskini_pengguna', methods = ['POST', 'GET'])
def kemaskini_pengguna():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    if session['jenis_pengguna'] is 3 :
        user = True
    else: 
        user = False

    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
    
        #retrieve data for kemaskini pengguna
        ic_pengguna = request.form['id_pengguna'] 

        cur = mysql.connection.cursor()
        cur.execute("SELECT kampung_id,nama_kampung FROM kampung ORDER BY nama_kampung ASC")
        data_kampung = cur.fetchall()

        cur.execute("SELECT pengguna.ic_pengguna, pengguna.kampung_id, kampung.nama_kampung, pengguna.nama_pengguna, pengguna.jenis_pengguna FROM kampung JOIN pengguna ON kampung.kampung_id =pengguna.kampung_id WHERE ic_pengguna = %s",(ic_pengguna,))
        data = cur.fetchall()
        cur.close()

        return render_template('kemaskini_pengguna.html', user = user, data = data,data_kampung=data_kampung)
    
    # User is not loggedin redirect to unauthorized page
    return redirect(url_for('akses_dinafikan')) 



#kemaskini pengguna
@app.route("/kemaskini_data_pengguna", methods=['GET', 'POST'])
def kemaskini_data_pengguna():
    
    #update pengguna
    ic_pengguna = request.form['ic_pengguna']
    kampung_id = request.form['kampung_id']    
    nama_pengguna = request.form['nama_pengguna']
    jenis_pengguna = request.form['jenis_pengguna']
    kata_laluan_lama = request.form['kata_laluan_lama']
    kata_laluan_baru = request.form['kata_laluan_baru']

    nama_pengguna = nama_pengguna.upper()   

    if kata_laluan_lama and kata_laluan_baru:
        cur = mysql.connection.cursor() 
        cur.execute("SELECT kata_laluan FROM pengguna WHERE ic_pengguna = %s",(ic_pengguna,))
        user = cur.fetchone()
        cur.close()

        if check_password_hash(user[0], kata_laluan_lama):
            hashed_new_password = generate_password_hash(kata_laluan_baru,method = 'sha256')   
  
           # If the user doen't not exist, add new user
            cur = mysql.connection.cursor()
            cur.execute('UPDATE pengguna SET kata_laluan = %s WHERE ic_pengguna = %s', (hashed_new_password,ic_pengguna))
            mysql.connection.commit()
            cur.close()
        else:
            flash("NO NIRC/KATA LALUAN TIDAK SAH",category="error")
            return redirect(url_for('maklumat_pengguna')) 
    
    cur = mysql.connection.cursor()
    cur.execute('UPDATE pengguna SET kampung_id = %s, nama_pengguna = %s, jenis_pengguna = %s WHERE ic_pengguna = %s',(kampung_id,nama_pengguna,jenis_pengguna,ic_pengguna))
    mysql.connection.commit()
    cur.close()
    flash("KEMASKINI TELAH BERJAYA",category='success')
    return redirect(url_for('maklumat_pengguna')) 

 

#Hapus pengguna
@app.route("/hapus_pengguna",methods=['GET', 'POST'])
def hapus_pengguna():
    #delete pengguna 
    ic_pengguna = request.form['id_pengguna']

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM pengguna WHERE ic_pengguna = %s',(ic_pengguna,))
    mysql.connection.commit()
    cur.close()

    flash('PENGGUNA TELAH BERJAYA DIHAPUSKAN', category='success')

    return redirect(url_for('maklumat_pengguna'))



#maklumat kampung----------------------------------------------------------------------------------
@app.route("/maklumat_kampung",methods=['GET', 'POST'])
def maklumat_kampung():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    # Check if user is loggedin
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:

        #check user type for display
        if session['jenis_pengguna'] is 3 :
            user = True
        else: 
            user = False

        headings="NO.","KAMPUNG ID","NAMA KAMPUNG","NAMA MUKIM"," "
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM kampung ORDER BY kampung_id ASC")
        data = cur.fetchall()
        cur.close()
        return render_template('maklumat_kampung.html',user=user,headings=headings, data=data )

    # User is not loggedin redirect to unauthorized page
    return redirect(url_for('akses_dinafikan')) 



#page for kemaskini Kampung
@app.route('/kemaskini_kampung', methods = ['POST', 'GET'])
def kemaskini_kampung():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    #retrieve data from kampung table
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
    
        kampung_id = request.form['kampung_id']  
        cur = mysql.connection.cursor()
    
        cur.execute('SELECT * FROM kampung WHERE kampung_id = %s',(kampung_id,))
        data = cur.fetchall()
        cur.close()

        return render_template('kemaskini_kampung.html', data = data)
        
    # User is not loggedin redirect to unauthorized page
    return redirect(url_for('akses_dinafikan')) 


#kemaskini jenis permohonan
@app.route("/kemaskini_data_kampung", methods=['GET', 'POST'])
def kemaskini_data_kampung():
    
    #update kampung data
    kampung_id = request.form['kampung_id']
    nama_kampung = request.form['nama_kampung']    
    nama_mukim = request.form['nama_mukim']

    #change to uppercase
    nama_kampung = nama_kampung.upper()
    nama_mukim = nama_mukim.upper()         

    cur = mysql.connection.cursor()
    cur.execute('UPDATE kampung SET nama_kampung = %s, nama_mukim = %s WHERE kampung_id = %s',(nama_kampung,nama_mukim,kampung_id))
              
    mysql.connection.commit()
    cur.close()
    flash("KEMASKINI TELAH BERJAYA",category='success')
    return redirect(url_for('maklumat_kampung')) 
 


#Hapus kampung
@app.route("/hapus_kampung",methods=['GET', 'POST'])
def hapus_kampung():
    
    #delete kampung
    kampung_id = request.form['kampung_id']

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM kampung WHERE kampung_id = %s',(kampung_id,))
    mysql.connection.commit()
    cur.close()
    flash('KAMPUNG TELAH BERJAYA DIHAPUSKAN', category='success')

    return redirect(url_for('maklumat_kampung'))

#Register jenis permohonan----------------------------------------------------------------------------------
@app.route('/daftar_jenis_permohonan', methods=['GET', 'POST'])
def daftar_jenis_permohonan():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

     # Check user type
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:
        #check user type for display

        if request.method == 'POST' and 'jenis_permohonan' in request.form:
            
            # Variable for easy access
            jenis_permohonan = request.form['jenis_permohonan']

            #change strings to uppercase
            jenis_permohonan = jenis_permohonan.upper()

            # Check if jenis permohonan exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM jenispermohonan WHERE jenis_permohonan = %s', (jenis_permohonan,))
            users = cursor.fetchone()
            
            # If account exists show error and validation checks
            if users:
               cursor.close()
               flash('JENIS PERMOHONAN TELAH WUJUD', category='error')

            else:
                # If the user doen't not exist, add new user
                cursor.execute('INSERT INTO jenispermohonan VALUES (null,%s)', (jenis_permohonan,))
                mysql.connection.commit()
                cursor.close()
                flash('JENIS PERMOHONAN TELAH DISIMPAN', category='success')

        elif request.method == 'POST':
            # If the form is empty
            flash('SILA ISI BORANG', category='error')
  
        return render_template('daftar_jenis_permohonan.html')

    # User is not loggedin redirect to unauthorized user page
    return redirect(url_for('akses_dinafikan'))  

#jenis permohonan----------------------------------------------------------------------------------
@app.route("/jenis_permohonan",methods=['GET', 'POST'])
def jenis_permohonan():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))
    
    cur = mysql.connection.cursor()
    
        # Check if user is loggedin
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:

        #check user type for display
        if session['jenis_pengguna'] is 3 :
            user = True
        else: 
            user = False

        headings="NO.","ID JENIS PERMOHONAN","JENIS PERMOHONAN"," "
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM jenispermohonan ORDER BY id_jenis_permohonan ASC")
        data = cur.fetchall()
        
        return render_template('jenis_permohonan.html',user=user,headings=headings, data=data )

    # User is not loggedin redirect to unauthorized page
    return redirect(url_for('akses_dinafikan')) 

#page for kemaskini jenis permohonan
@app.route('/kemaskini_jenis_permohonan', methods = ['POST', 'GET'])
def kemaskini_jenis_permohonan():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:

        jenisPermohonan = request.form['jenis_permohonan']    
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM jenispermohonan WHERE jenis_permohonan = %s',(jenisPermohonan,))
        data = cur.fetchall()
        cur.close()

        return render_template('kemaskini_jenis_permohonan.html', data = data)
        # User is not loggedin redirect to unauthorized page

    return redirect(url_for('akses_dinafikan')) 



#kemaskini jenis permohonan
@app.route("/kemaskini_data_jenis_permohonan", methods=['GET', 'POST'])
def kemaskini_data_jenis_permohonan():
    
    jenisPermohonan = request.form['jenis_permohonan']    
    id_jenis_permohonan = request.form['id_jenis_permohonan']   

    jenisPermohonan = jenisPermohonan.upper()

    #the existance of id_jenis_permohonan is only for this moment. to update
    cur = mysql.connection.cursor()
    cur.execute('UPDATE jenispermohonan SET jenis_permohonan = %s WHERE id_jenis_permohonan = %s',(jenisPermohonan,id_jenis_permohonan))
              
    mysql.connection.commit()
    cur.close()
    flash("KEMASKINI TELAH BERJAYA",category='success')
    return redirect(url_for('jenis_permohonan')) 
 

#Hapus jenis permohonan----------------------------------------------------------------------------------
@app.route("/hapus_jenis_permohonan",methods=['GET', 'POST'])
def hapus_jenis_permohonan():
    
    #delete jenis permohonan
    jenis_permohonan = request.form['jenis_permohonan']

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM jenispermohonan WHERE jenis_permohonan = %s',(jenis_permohonan,))
    cur.close()
    mysql.connection.commit()

    flash('JENIS PERMOHONAN TELAH BERJAYA DIHAPUSKAN.', category='success')

    return redirect(url_for('jenis_permohonan'))



#log out------------------------------------------------------------------------------------
@app.route('/logKeluar')
def logKeluar():
    session.clear()

    return redirect(url_for('logMasuk'))





#Addition with the other system ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/input", methods=['GET', 'POST'])
def input():
    # fetch data from kampung database for the dropdown
    cur = mysql.connection.cursor()
    cur.execute('SELECT kampung_id, nama_kampung FROM kampung ORDER BY nama_kampung')
    kg = cur.fetchall()

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    #addition to the original code for user access limitation
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:

        # fetch data from input form
        if request.method == 'POST':
            sumber_peruntukan = request.form['sumber_peruntukan']
            kampung = request.form['kampung']
            sebutharga = request.form['sebutharga']
            suratkuasa_waran = request.form['suratkuasa_waran']
            nama_projek = request.form['nama_projek']
            rujukan = request.form['rujukan']
            kontraktor = request.form['kontraktor']
            peruntukan_diluluskan = request.form['peruntukan_diluluskan']
            bayar = request.form['bayar']
            tawaran = request.form['tawaran']
            milik_tapak = request.form['milik_tapak']
            tempoh_siap = request.form['tempoh_siap']
            jangkaan_siap = request.form['jangkaan_siap']
            sebenar_siap = request.form['sebenar_siap']
            status = request.form['status']

            # check if suratkuasa already exist in database
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM data WHERE No_Suratkuasa_Waran=%s', (suratkuasa_waran,))
            data = cur.fetchone()

            # if data exist show error
            if data:
                flash('MAKLUMAT TELAH WUJUD', category='error')
            # show error if information in form not complete
            elif not sumber_peruntukan or not kampung or not sebutharga or not suratkuasa_waran or not nama_projek or not rujukan or not kontraktor or not peruntukan_diluluskan or not bayar or not tawaran or not milik_tapak or not tempoh_siap or not jangkaan_siap or not sebenar_siap or not status:
                flash('SILA ISI MAKLUMAT SEPENUHNYA', category='error')
            else:
                # insert data to database
                baki = (int(peruntukan_diluluskan) - int(bayar))
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO data (Sumber_Peruntukan, Kampung_ID, No_SebutHarga, No_Suratkuasa_Waran,"
                            " Nama_Projek, No_Rujukan, Kontraktor, Peruntukan_Diluluskan, Bayar,"
                            " Baki, Tarikh_Tawaran, Tarikh_Milik_Tapak, Tempoh_Siap, Tarikh_Jangkaan_Siap, Tarikh_Sebenar_Siap,"
                            " Status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (sumber_peruntukan, kampung, sebutharga.upper(), suratkuasa_waran.upper(),
                             nama_projek.upper(), rujukan,
                             kontraktor.upper(), peruntukan_diluluskan, bayar, baki, tawaran, milik_tapak,
                             tempoh_siap.upper(), jangkaan_siap,
                             sebenar_siap, status))
                mysql.connection.commit()
                cur.close()
                flash("MAKLUMAT BERJAYA DISIMPAN")
        elif request.method == 'POST':
            flash('SILA ISI MAKLUMAT', category='error')
        return render_template('input.html', title="DAFTAR MAKLUMAT", kg=kg)
    return redirect(url_for('akses_dinafikan')) 



@app.route("/report_list", methods=['GET', 'POST'])
def report_list():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))
        
    #addition to the original code for user access limitation
    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:

        cur = mysql.connection.cursor()
        cur.execute("SELECT DISTINCT YEAR(Tarikh_Tawaran) FROM data ORDER BY YEAR(Tarikh_Tawaran) ASC")
        tahun = cur.fetchall()

        cur.execute("SELECT DISTINCT nama_kampung FROM kampung ORDER BY nama_kampung ASC")
        kampung = cur.fetchall()

        cur.execute("SELECT DISTINCT nama_mukim FROM kampung ORDER BY nama_mukim ASC")
        mukim = cur.fetchall()

        tarikh_sekarang = date.today()
        tahun_sekarang = tarikh_sekarang.year

        # fetch data from database
        cur = mysql.connection.cursor()
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id")
        report = cur.fetchall()
        return render_template('report_list.html', title="LAPORAN", report=report, tahun=tahun, kampung=kampung, mukim=mukim, tahun_sekarang=tahun_sekarang,tarikh_sekarang=tarikh_sekarang)

    return redirect(url_for('akses_dinafikan'))


@app.route("/federal", methods=['GET', 'POST'])
def federal():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    if session['jenis_pengguna'] is 3 :
        user = True
    else: 
        user = False

    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:

        cur = mysql.connection.cursor()
        cur.execute("SELECT DISTINCT YEAR(Tarikh_Tawaran) FROM data WHERE Sumber_Peruntukan='Persekutuan' ORDER BY YEAR(Tarikh_Tawaran) ASC")
        tahun = cur.fetchall()

        cur.execute("SELECT DISTINCT kampung.nama_kampung FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan='Persekutuan' ORDER BY kampung.nama_kampung ASC")
        kampung = cur.fetchall()

        cur.execute("SELECT DISTINCT kampung.nama_mukim FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan='Persekutuan' ORDER BY kampung.nama_mukim ASC")
        mukim = cur.fetchall()

        tarikh_sekarang = date.today()
        tahun_sekarang = tarikh_sekarang.year

        # fetch data from database and filtered by persekutuan
        cur = mysql.connection.cursor()
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek, kampung.nama_mukim, "
                    "kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor, data.Peruntukan_Diluluskan, "
                    "data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak, data.Tempoh_Siap, "
                    "data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE Sumber_Peruntukan = 'persekutuan' AND data.Kampung_ID = kampung.kampung_id")
        federal_list = cur.fetchall()
        return render_template('federal.html',user=user, title="PERSEKUTUAN", federal_list=federal_list, tahun=tahun, kampung=kampung, mukim=mukim, tahun_sekarang=tahun_sekarang,tarikh_sekarang=tarikh_sekarang)
    
    return redirect(url_for('akses_dinafikan'))


@app.route("/state", methods=['GET', 'POST'])
def state():

    try:
        session['jenis_pengguna']

    except KeyError:
        return redirect(url_for('logMasuk'))

    if session['jenis_pengguna'] is 3 :
        user = True
    else: 
        user = False

    if 'loggedin' in session and session['jenis_pengguna'] is 2 or session['jenis_pengguna'] is 3:

        cur = mysql.connection.cursor()
        cur.execute("SELECT DISTINCT YEAR(Tarikh_Tawaran) FROM data WHERE Sumber_Peruntukan='Negeri' ORDER BY YEAR(Tarikh_Tawaran) ASC")
        tahun = cur.fetchall()

        cur.execute("SELECT DISTINCT kampung.nama_kampung FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan='Negeri' ORDER BY kampung.nama_kampung ASC")
        kampung = cur.fetchall()

        cur.execute("SELECT DISTINCT kampung.nama_mukim FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan='Negeri' ORDER BY kampung.nama_mukim ASC")
        mukim = cur.fetchall()

        tarikh_sekarang = date.today()
        tahun_sekarang = tarikh_sekarang.year

        # fetch data from database and filtered by negeri
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek, kampung.nama_mukim, "
                    "kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor, data.Peruntukan_Diluluskan, "
                    "data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak, data.Tempoh_Siap, "
                    "data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE Sumber_Peruntukan = 'negeri' AND data.Kampung_ID = kampung.kampung_id")
        state_list = cur.fetchall()
        return render_template('state.html',user=user, title="NEGERI", state_list=state_list, tahun=tahun, kampung=kampung, mukim=mukim, tahun_sekarang=tahun_sekarang,tarikh_sekarang=tarikh_sekarang)

    return redirect(url_for('akses_dinafikan'))

@app.route("/update_federal", methods=['GET', 'POST'])
def update_federal():
    # fetch information from edit modal form
    if request.method == 'POST':
        data_ID = request.form.get('data_ID')
        peruntukan_diluluskan = request.form.get('peruntukan_diluluskan')
        bayar = request.form['bayar']
        baki = (int(peruntukan_diluluskan) - int(bayar))
        sebenar_siap = request.form.get('sebenar_siap')
        status = request.form.get('status')

        cur = mysql.connection.cursor()
        cur.execute("""
              UPDATE data 
              SET Bayar=%s, Baki=%s, Tarikh_Sebenar_Siap=%s, Status=%s WHERE data.data_ID=%s """,
                    (bayar, baki, sebenar_siap, status, data_ID))
        mysql.connection.commit()
        cur.close()
        flash("MAKLUMAT BERJAYA DIKEMASKINI")
    return redirect(url_for('federal'))



@app.route("/update_state", methods=['GET', 'POST'])
def update_state():
    # fetch information from edit modal form
    if request.method == 'POST':
        data_ID = request.form.get('data_ID')
        peruntukan_diluluskan = request.form.get('peruntukan_diluluskan')
        bayar = request.form['bayar']
        baki = (int(peruntukan_diluluskan) - int(bayar))
        sebenar_siap = request.form.get('sebenar_siap')
        status = request.form.get('status')

        cur = mysql.connection.cursor()
        cur.execute("""
              UPDATE data 
              SET Bayar=%s, Baki=%s, Tarikh_Sebenar_Siap=%s, Status=%s WHERE data.data_ID=%s""",
                    (bayar, baki, sebenar_siap, status, data_ID))
        mysql.connection.commit()
        cur.close()
        flash("MAKLUMAT BERJAYA DIKEMASKINI")
    return redirect(url_for('state'))



@app.route("/cari", methods=['GET', 'POST'])
def cari():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT YEAR(Tarikh_Tawaran) FROM data ORDER BY YEAR(Tarikh_Tawaran) ASC")
    tahun = cur.fetchall()

    cur.execute("SELECT DISTINCT nama_kampung FROM kampung ORDER BY nama_kampung ASC")
    kampung = cur.fetchall()

    cur.execute("SELECT DISTINCT nama_mukim FROM kampung ORDER BY nama_mukim ASC")
    mukim = cur.fetchall()

    tarikh_sekarang = date.today()
    tahun_sekarang = tarikh_sekarang.year

    cari_tahun = request.form['tahun']
    cari_no_projek = request.form['no_projek_waran']
    cari_kampung = request.form['kampung_id']
    cari_mukim = request.form['mukim_id']

    # filter by no suratkuasa and waran
    if cari_no_projek != "" and cari_tahun == "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND No_Suratkuasa_Waran=%s", (cari_no_projek,))

        flash('CARIAN BERDASARKAN NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by year
    elif cari_tahun != "" and cari_no_projek == "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND YEAR(Tarikh_Tawaran)=%s", (cari_tahun,))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun, category='success')

    # filter by kampung
    elif cari_kampung != "" and cari_no_projek == "" and cari_tahun == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND kampung.nama_kampung=%s", (cari_kampung,))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung, category='success')

    # filter by mukim
    elif cari_mukim != "" and cari_no_projek == "" and cari_tahun == "" and cari_kampung == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND kampung.nama_mukim=%s", (cari_mukim,))

        flash('CARIAN BERDASARKAN MUKIM : ' + cari_mukim, category='success')

    # filter by tahun and suratkuasa/waran
    elif cari_tahun != "" and cari_no_projek != "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND No_Suratkuasa_Waran=%s AND YEAR(Tarikh_Tawaran)=%s", (cari_no_projek, cari_tahun))

        flash('CARIAN BERDASARKAN TAHUN : '+cari_tahun+' DAN NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by tahun and kampung
    elif cari_tahun != "" and cari_kampung != "" and cari_no_projek == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND kampung.nama_kampung=%s AND YEAR(Tarikh_Tawaran)=%s", (cari_kampung, cari_tahun))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ' DAN KAMPUNG : ' + cari_kampung, category='success')

    # filter by tahun and mukim
    elif cari_tahun != "" and cari_mukim != "" and cari_kampung == "" and cari_no_projek == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND kampung.nama_mukim=%s AND YEAR(Tarikh_Tawaran)=%s", (cari_mukim, cari_tahun))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ' DAN MUKIM : ' + cari_mukim, category='success')

    # filter by kampung and mukim
    elif cari_kampung != "" and cari_mukim != "" and cari_tahun == "" and cari_no_projek == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s", (cari_kampung, cari_mukim))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung + ' DAN MUKIM : ' + cari_mukim, category='success')

    # filter by kampung and suratkuasa/waran
    elif cari_kampung != "" and cari_no_projek != "" and cari_tahun == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND kampung.nama_kampung=%s AND data.No_SuratKuasa_Waran=%s", (cari_kampung, cari_no_projek))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung + ' DAN NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by mukim and suratkuasa/waran
    elif cari_mukim != "" and cari_no_projek != "" and cari_tahun == "" and cari_kampung == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s", (cari_mukim, cari_no_projek))

        flash('CARIAN BERDASARKAN MUKIM : ' + cari_mukim + ' DAN NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

        # filter by tahun, kampung and mukim
    elif cari_mukim != "" and cari_tahun != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s",
                    (cari_tahun, cari_kampung, cari_mukim))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', KAMPUNG : ' + cari_kampung + ', MUKIM : ' + cari_mukim,
              category='success')

    # filter by kampung, mukim and suratkuasa/waran
    elif cari_mukim != "" and cari_no_projek != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_kampung, cari_mukim, cari_no_projek))

        flash(
            'CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung + ', MUKIM : ' + cari_mukim + ', NO. SURATKUASA/WARAN : ' + cari_no_projek,
            category='success')

    # filter by tahun, mukim, suratkuasa/waran
    elif cari_mukim != "" and cari_no_projek != "" and cari_tahun != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_tahun, cari_mukim, cari_no_projek))

        flash(
            'CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', MUKIM : ' + cari_mukim + ', NO. SURATKUASA/WARAN : ' + cari_no_projek,
            category='success')

    # filter by tahun, kampung, suratkuasa/waran
    elif cari_no_projek != "" and cari_tahun != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_kampung=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_tahun, cari_kampung, cari_no_projek))

        flash(
            'CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', KAMPUNG : ' + cari_kampung + ', NO. SURATKUASA/WARAN : ' + cari_no_projek,
            category='success')

    # filter by all
    elif cari_tahun != "" and cari_kampung != "" and cari_mukim != "" and cari_no_projek != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_tahun, cari_kampung, cari_mukim, cari_no_projek))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', KAMPUNG : ' + cari_kampung + ', MUKIM : ' + cari_mukim + ', NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    elif cari_tahun == "" and cari_no_projek == "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"    
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID "
                    "FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id")

    report = cur.fetchall()
    return render_template('report_list.html', report=report, tahun=tahun, kampung=kampung, mukim=mukim, tahun_sekarang=tahun_sekarang,tarikh_sekarang=tarikh_sekarang, cari_tahun=cari_tahun)



@app.route("/cari_federal", methods=['GET', 'POST'])
def cari_federal():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT YEAR(Tarikh_Tawaran) FROM data WHERE Sumber_Peruntukan='Persekutuan' ORDER BY YEAR(Tarikh_Tawaran) ASC")
    tahun = cur.fetchall()

    cur.execute("SELECT DISTINCT kampung.nama_kampung FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan='Persekutuan' ORDER BY kampung.nama_kampung ASC")
    kampung = cur.fetchall()

    cur.execute("SELECT DISTINCT kampung.nama_mukim FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan='Persekutuan' ORDER BY kampung.nama_mukim ASC")
    mukim = cur.fetchall()

    tarikh_sekarang = date.today()
    tahun_sekarang = tarikh_sekarang.year

    cari_tahun = request.form['tahun']
    cari_no_projek = request.form['no_projek_waran']
    cari_kampung = request.form['kampung_id']
    cari_mukim = request.form['mukim_id']

    # filter by no suratkuasa and waran
    if cari_no_projek != "" and cari_tahun == "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND No_Suratkuasa_Waran=%s", (cari_no_projek,))

        flash('CARIAN BERDASARKAN NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by year
    elif cari_tahun != "" and cari_no_projek == "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND YEAR(Tarikh_Tawaran)=%s", (cari_tahun,))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun, category='success')

    # filter by kampung
    elif cari_kampung != "" and cari_no_projek == "" and cari_tahun == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND kampung.nama_kampung=%s", (cari_kampung,))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung, category='success')

    # filter by mukim
    elif cari_mukim != "" and cari_no_projek == "" and cari_tahun == "" and cari_kampung == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND kampung.nama_mukim=%s", (cari_mukim,))

        flash('CARIAN BERDASARKAN MUKIM : ' + cari_mukim, category='success')

    # filter by tahun and suratkuasa/waran
    elif cari_tahun != "" and cari_no_projek != "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND No_Suratkuasa_Waran=%s AND YEAR(Tarikh_Tawaran)=%s",
                    (cari_no_projek, cari_tahun))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ' DAN NO. SURATKUASA/WARAN : ' + cari_no_projek,
              category='success')

    # filter by tahun and kampung
    elif cari_tahun != "" and cari_kampung != "" and cari_no_projek == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND kampung.nama_kampung=%s AND YEAR(Tarikh_Tawaran)=%s",
                    (cari_kampung, cari_tahun))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ' DAN KAMPUNG : ' + cari_kampung, category='success')

    # filter by tahun and mukim
    elif cari_tahun != "" and cari_mukim != "" and cari_kampung == "" and cari_no_projek == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND kampung.nama_mukim=%s AND YEAR(Tarikh_Tawaran)=%s",
                    (cari_mukim, cari_tahun))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ' DAN MUKIM : ' + cari_mukim, category='success')

    # filter by kampung and mukim
    elif cari_kampung != "" and cari_mukim != "" and cari_tahun == "" and cari_no_projek == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s",
                    (cari_kampung, cari_mukim))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung + 'DAN MUKIM : ' + cari_mukim, category='success')

    # filter by kampung and suratkuasa/waran
    elif cari_kampung != "" and cari_no_projek != "" and cari_tahun == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND kampung.nama_kampung=%s AND data.No_SuratKuasa_Waran=%s",
                    (cari_kampung, cari_no_projek))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung + ' DAN NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by tahun, kampung and mukim
    elif cari_mukim != "" and cari_tahun != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s",
                    (cari_tahun, cari_kampung, cari_mukim))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', KAMPUNG : ' + cari_kampung + ', MUKIM : ' + cari_mukim,
              category='success')

    # filter by kampung, mukim and suratkuasa/waran
    elif cari_mukim != "" and cari_no_projek != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_kampung, cari_mukim, cari_no_projek))

        flash(
            'CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung + ', MUKIM : ' + cari_mukim + ', NO. SURATKUASA/WARAN : ' + cari_no_projek,
            category='success')

    # filter by tahun, mukim, suratkuasa/waran
    elif cari_mukim != "" and cari_no_projek != "" and cari_tahun != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_tahun, cari_mukim, cari_no_projek))

        flash(
            'CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', MUKIM : ' + cari_mukim + ', NO. SURATKUASA/WARAN : ' + cari_no_projek,
            category='success')

    # filter by tahun, kampung, suratkuasa/waran
    elif cari_no_projek != "" and cari_tahun != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_kampung=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_tahun, cari_kampung, cari_no_projek))

        flash(
            'CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', KAMPUNG : ' + cari_kampung + ', NO. SURATKUASA/WARAN : ' + cari_no_projek,
            category='success')

    # filter by all
    elif cari_mukim != "" and cari_no_projek != "" and cari_tahun != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan' AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_tahun, cari_kampung, cari_mukim, cari_no_projek))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', KAMPUNG : ' + cari_kampung + ', MUKIM : ' + cari_mukim + ', NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    elif cari_tahun == "" and cari_no_projek == "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID "
                    "FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Persekutuan'")

    federal_list = cur.fetchall()
    return render_template('federal.html', federal_list=federal_list, tahun=tahun, kampung=kampung, mukim=mukim, tahun_sekarang=tahun_sekarang,tarikh_sekarang=tarikh_sekarang, cari_tahun=cari_tahun)



@app.route("/cari_state", methods=['GET', 'POST'])
def cari_state():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT YEAR(Tarikh_Tawaran) FROM data WHERE Sumber_Peruntukan='Negeri' ORDER BY YEAR(Tarikh_Tawaran) ASC")
    tahun = cur.fetchall()

    cur.execute("SELECT DISTINCT kampung.nama_kampung FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan='Negeri' ORDER BY kampung.nama_kampung ASC")
    kampung = cur.fetchall()

    cur.execute("SELECT DISTINCT kampung.nama_mukim FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan='Negeri' ORDER BY kampung.nama_mukim ASC")
    mukim = cur.fetchall()

    tarikh_sekarang = date.today()
    tahun_sekarang = tarikh_sekarang.year

    cari_tahun = request.form['tahun']
    cari_no_projek = request.form['no_projek_waran']
    cari_kampung = request.form['kampung_id']
    cari_mukim = request.form['mukim_id']

    # filter by no suratkuasa and waran
    if cari_no_projek != "" and cari_tahun != "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND No_Suratkuasa_Waran=%s",
                    (cari_no_projek,))

        flash('CARIAN BERDASARKAN NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by year
    elif cari_tahun != "" and cari_no_projek == "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND YEAR(Tarikh_Tawaran)=%s",
                    (cari_tahun,))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun, category='success')

    # filter by kampung
    elif cari_kampung != "" and cari_no_projek == "" and cari_tahun == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND kampung.nama_kampung=%s",
                    (cari_kampung,))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung, category='success')

    # filter by mukim
    elif cari_mukim != "" and cari_no_projek == "" and cari_tahun == "" and cari_kampung == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND kampung.nama_mukim=%s",
                    (cari_mukim,))

        flash('CARIAN BERDASARKAN MUKIM : ' + cari_mukim, category='success')

    # filter by tahun and suratkuasa/waran
    elif cari_tahun != "" and cari_no_projek != "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND No_Suratkuasa_Waran=%s AND YEAR(Tarikh_Tawaran)=%s",
                    (cari_no_projek, cari_tahun))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ' DAN NO. SURATKUASA/WARAN : ' + cari_no_projek,
              category='success')

    # filter by tahun and kampung
    elif cari_tahun != "" and cari_kampung != "" and cari_no_projek == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND kampung.nama_kampung=%s AND YEAR(Tarikh_Tawaran)=%s",
                    (cari_kampung, cari_tahun))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ' DAN KAMPUNG : ' + cari_kampung, category='success')

    # filter by tahun and mukim
    elif cari_tahun != "" and cari_mukim != "" and cari_kampung == "" and cari_no_projek == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND kampung.nama_mukim=%s AND YEAR(Tarikh_Tawaran)=%s",
                    (cari_mukim, cari_tahun))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ' DAN MUKIM : ' + cari_mukim, category='success')

    # filter by kampung and mukim
    elif cari_kampung != "" and cari_mukim != "" and cari_tahun == "" and cari_no_projek == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s",
                    (cari_kampung, cari_mukim))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung + ' DAN MUKIM : ' + cari_mukim, category='success')

    # filter by kampung and suratkuasa/waran
    elif cari_kampung != "" and cari_no_projek != "" and cari_tahun == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND kampung.nama_kampung=%s AND data.No_SuratKuasa_Waran=%s",
                    (cari_kampung, cari_no_projek))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung + ' DAN NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by mukim and suratkuasa/waran
    elif cari_mukim != "" and cari_no_projek != "" and cari_tahun == "" and cari_kampung == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_mukim, cari_no_projek))

        flash('CARIAN BERDASARKAN MUKIM : ' + cari_mukim + ' DAN NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by tahun, kampung and mukim
    elif cari_mukim != "" and cari_tahun != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s",
                    (cari_tahun, cari_kampung, cari_mukim))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', KAMPUNG : ' + cari_kampung + ', MUKIM : ' + cari_mukim, category='success')

    # filter by kampung, mukim and suratkuasa/waran
    elif cari_mukim != "" and cari_no_projek != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_kampung, cari_mukim, cari_no_projek))

        flash('CARIAN BERDASARKAN KAMPUNG : ' + cari_kampung + ', MUKIM : ' + cari_mukim + ', NO. SURATKUASA/WARAN : ' +cari_no_projek, category='success')

    # filter by tahun, mukim, suratkuasa/waran
    elif cari_mukim != "" and cari_no_projek != "" and cari_tahun != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_tahun, cari_mukim, cari_no_projek))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', MUKIM : ' + cari_mukim + ', NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by tahun, kampung, suratkuasa/waran
    elif cari_no_projek != "" and cari_tahun != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_kampung=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_tahun, cari_kampung, cari_no_projek))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', KAMPUNG : ' + cari_kampung + ', NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    # filter by all
    elif cari_mukim != "" and cari_no_projek != "" and cari_tahun != "" and cari_kampung != "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID FROM data, kampung "
                    "WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri' AND YEAR(Tarikh_Tawaran)=%s AND kampung.nama_kampung=%s AND kampung.nama_mukim=%s AND data.No_Suratkuasa_Waran=%s",
                    (cari_tahun, cari_kampung, cari_mukim, cari_no_projek))

        flash('CARIAN BERDASARKAN TAHUN : ' + cari_tahun + ', KAMPUNG : ' + cari_kampung + ', MUKIM : ' + cari_mukim + ', NO. SURATKUASA/WARAN : ' + cari_no_projek, category='success')

    elif cari_tahun == "" and cari_no_projek == "" and cari_kampung == "" and cari_mukim == "":
        cur.execute("SELECT data.No_SebutHarga, data.No_Suratkuasa_Waran, data.Nama_Projek,"
                    "kampung.nama_mukim, kampung.nama_kampung, data.Sumber_Peruntukan, data.Kontraktor,"
                    "data.Peruntukan_Diluluskan, data.Bayar, data.Baki, data.Tarikh_Tawaran, data.Tarikh_Milik_Tapak,"
                    "data.Tempoh_Siap, data.Tarikh_Jangkaan_Siap, data.Tarikh_Sebenar_Siap, data.Status, data.data_ID "
                    "FROM data, kampung WHERE data.Kampung_ID = kampung.kampung_id AND Sumber_Peruntukan = 'Negeri'")

    state_list = cur.fetchall()
    return render_template('state.html', state_list=state_list, tahun=tahun, kampung=kampung, mukim=mukim, tahun_sekarang=tahun_sekarang,tarikh_sekarang=tarikh_sekarang, cari_tahun=cari_tahun)



@app.route("/delete_federal/<int:data_ID>", methods=['GET'])
def delete_federal(data_ID):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM data WHERE data_ID=%s", (data_ID,))
    mysql.connection.commit()
    flash("MAKLUMAT TELAH DIHAPUSKAN")
    return redirect(url_for('federal'))



@app.route("/delete_state/<int:data_ID>", methods=['GET'])
def delete_state(data_ID):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM data WHERE data_ID=%s", (data_ID,))
    mysql.connection.commit()
    flash("MAKLUMAT TELAH DIHAPUSKAN")
    return redirect(url_for('state'))


if __name__ =='__main__':
    app.run(debug = True)
