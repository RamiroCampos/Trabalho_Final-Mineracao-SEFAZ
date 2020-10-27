from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
import os
import time
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

import re
import string

from joblib import load


import pdfplumber


app = Flask(__name__)

app.config["PDF_UPLOADS"] = r".\static\upload"
app.config["ALLOWED_PDF_EXTENSIONS"] = ["PDF", "pdf"]
app.config['SECRET_KEY'] = 'random secret key'    
[diciToLabel, pipe] = load('modelo.joblib')

def allowed_pdf(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_PDF_EXTENSIONS"]:
        return True
    else:
        return False

def clearText(text):
    tokens = [w for w in re.findall("[a-záéíóúçâêôãõà]+(?:[-'][a-záéíóúçâêôãõà]+)*", str(text).lower().strip()) if w not in stopwords.words('portuguese') + ['n', 'nº', 'º']]
    return ' '.join(tokens)

def firstPage(pathFile):
    file = pdfplumber.open(pathFile)
    pageOne = file.pages[0]

    return pageOne.extract_text()
        
@app.route('/', methods=['GET', 'POST'])
def index():   
    if request.method == "POST":

        if request.files:

            pdf = request.files["pdfFile"]

            if pdf.filename == "":
  
                return redirect(request.url)

            if allowed_pdf(pdf.filename):
  
                filename = secure_filename(pdf.filename)
                pdfName,ext = filename.rsplit(".", 1)
                Filename = pdfName + '.' + ext

  
                pdf.save(os.path.join(app.config["PDF_UPLOADS"], Filename)) # salva o  arquivo
                print("Caminho = ",os.path.join(app.config["PDF_UPLOADS"], Filename))
                
                alvo = firstPage(os.path.join(app.config["PDF_UPLOADS"], Filename))
                alvo = clearText(alvo)
                df = pd.DataFrame([alvo], columns=['Content'])

                pred = pipe.predict(df['Content'])
                
                label = diciToLabel[pred[0]]
                
                time.sleep(1)
                
                # corBotao = [
                #     "primary",
                #     "danger",
                #     "secundary",
                # ]
                print("veredito = ",label)
                result = "O documento " + pdfName + " pertence a classe \"" + str(label) + "\"."
                return render_template('results.html', veredito = result )

            else:
                flash("Extensão não permitida, apenas .JPG, .JPEG, ou .PNG")
                # print()
                return render_template('home.html')

    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)


   