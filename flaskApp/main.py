from flask import Flask, render_template, request, session, url_for, redirect
from forms import FiltersForm
from dotenv import load_dotenv
from collections import OrderedDict 
import os

load_dotenv('.env')

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    
    form = FiltersForm()
    if form.validate_on_submit():
        filters = []
        filters.append(('min_price', form.min_price.data))
        filters.append(('max_price', form.max_price.data))
        filters.append(('min_units', form.min_units.data))
        filters.append(('min_units', form.min_units.data))
        
        session['filters'] = filters

        return redirect(url_for('results'))
    
    print(form.errors)
    
    return render_template('home.html', form=form)

@app.route('/results')
def results():
      
    return render_template('results.html')
    

if __name__ == "__main__":
    app.run(debug=True)