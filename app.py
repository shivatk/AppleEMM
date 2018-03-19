from flask import Flask, render_template, url_for, redirect, request, flash, send_file
from jinja2 import Template
from logging import DEBUG
from vppsync import SyncAssets, getVPPLicensesBySerial
from vppsync import vpprevokelicense, vpprevoke
from dep import getDEPSession, DEPFetch, getDeviceDetails
import random
import psycopg2
import os

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.logger.setLevel(DEBUG)
app.config['SECRET_KEY'] = 'alskdfnals;djfha;sd'

@app.route('/')
def get():
    return render_template('dep.html')

@app.route('/dep', methods = ['GET','POST'])
def dep():
    if request.method == 'POST':

        CK = request.form['CK']
        CS = request.form['CS']
        AT = request.form['T']
        AS = request.form['TS']
        SerialNumber = request.form['SerialNumber']
        if CK != '' and CS != '' and AT != '' and AS != '' and SerialNumber == '':
            DEPToken = {"CK":CK,"CS":CS,"AT":AT,"AS":AS}
            SessionKey = random.randint(0,5000000)
            flash(SessionKey)

            Records = DEPFetch(SessionKey,DEPToken,'')
            if Records == 'Invalid':
                flash('invalid')
                return render_template('dep.html')
            if Records == 'Token Expired':
                flash('expired')
                return render_template('dep.html')
            Count = len(Records)
            return render_template('deprecords.html',Records=Records,Count=Count)
        if CK == '' or CS == '' or AT == '' or AS == '' and SerialNumber == '':
            flash('notcomplete')
            return render_template ('dep.html')
        if CK == '' or CS == '' or AT == '' or AS == '' and SerialNumber != '':
            flash('notcomplete')
            return render_template ('dep.html')
        if CK != '' and CS != '' and AT != '' and AS != '' and SerialNumber != '':
            DEPToken = {"CK":CK,"CS":CS,"AT":AT,"AS":AS}
            SessionKey = random.randint(0,5000000)
            flash(SessionKey)
            Record = getDeviceDetails(SessionKey,SerialNumber,DEPToken)
            if Record == 'Invalid':
                flash('invalid')
                return render_template('dep.html')
            if Record == 'Token Expired':
                flash('expired')
                return render_template('dep.html')
            if Record == 'Null':
                flash('nodevice')
                return render_template('dep.html')
            return render_template('deprecords.html',Record=Record)


    return render_template('dep.html')

@app.route('/vpp', methods = ['GET','POST'])
def vpp():
    if request.method == 'POST':
        sToken = request.form['sToken']
        serialNumber = request.form['SerialNumber']
        if sToken == '':
            flash('Null sToken')
            return render_template('vpp.html')
        if serialNumber == '':
            SessionKey = random.randint(0,5000000)
            flash(SessionKey)
            Assets = SyncAssets(sToken,SessionKey)
            if Assets == 'LoginFailed':
                flash('LoginFailed')
                return render_template('vpp.html')
            return render_template('vppsyncassets.html',SyncAssets=Assets)
        if sToken != '' and serialNumber != '':
            SessionKey = random.randint(0,5000000)
            flash(SessionKey)
            assignedApps = getVPPLicensesBySerial(sToken,serialNumber,'',SessionKey)
            if assignedApps == 'LoginFailed':
                flash('LoginFailed')
                return render_template('vpp.html')
            if assignedApps == []:
                flash('NoAppsAssigned')
                return render_template('vpp.html')
            return render_template('vppsyncassets.html',assignedApps=assignedApps)
    return render_template('vpp.html')

def main():
    app.run()

@app.route('/revoke', methods=['GET','POST'])
def revoke():
    if request.method == 'POST':
        sToken = request.form['sToken']
        if sToken == '':
            flash('Null sToken')
            return render_template('revoke.html')
        target = os.path.join(APP_ROOT, 'licensefiles/')
        if request.files.getlist("file") == []:
            flash('NoFile')
            return render_template('revoke.html')
        for file in request.files.getlist("file"):
            SessionKey = random.randint(0,5000000)
            flash(SessionKey)
            file_extension = os.path.splitext(file.filename)
            filename = str(SessionKey)+str(file_extension[1])
            destination = "/".join([target, filename])
            file.save(destination)
            vpprevoke(sToken,destination,SessionKey)
        return render_template('vpprevoke.html',file=SessionKey)

    return render_template('revoke.html')

@app.route("/download/<file>")
def DownloadLogFile(file):
    try:
        filename = file+'.log'
        target = os.path.join(APP_ROOT, 'licensefiles/')
        destination = "/".join([target, filename])
        return send_file(destination,as_attachment=True)
    except Exception as e:
        return render_template('vpprevoke.html')

@app.route("/download/sample")
def DownloadSample():
    try:
        filename = 'sample.csv'
        target = os.path.join(APP_ROOT, 'licensefiles/')
        destination = "/".join([target, filename])
        return send_file(destination,as_attachment=True)
    except Exception as e:
        return render_template('vpprevoke.html')

@app.route("/ioslogging")
def ioslogging():
    return render_template('ioslogging.html')

@app.route("/macoslogging")
def macoslogging():
    return render_template('maclogging.html')

@app.route('/iostraffic')
def iostraffic():
    return render_template('iostraffic.html')

if __name__ == '__main__':
    main()
