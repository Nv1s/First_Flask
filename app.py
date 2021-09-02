from flask import Flask, render_template, request, escape, session
from DBcm import UseDataBase
from checker import check_log_in


app = Flask(__name__)
app.config['dbconfig'] = {'host': 'localhost',
     'user': 'root',
     'password': 'admin',
     'database': 'vsearchlogDB', }
app.secret_key = 'Unreal'


def log_request(req: 'flask_request', res: str) -> None:
    dbconfig = {'host': 'localhost',
     'user': 'root',
     'password': 'admin',
     'database': 'vsearchlogDB', }
    with UseDataBase(dbconfig) as cursor:
        _SQL = """insert into log
         (phrase, letters, ip, browser_string, results)
         values
         (%s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              req.user_agent.browser,
                              res, ))


def search4letters(phrase: str, letters: str = 'aeiou') -> str:
    return set(letters).intersection(set(phrase))


@app.route('/search4', methods=['POST'])
def do_search() -> str:
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))
    try:
        log_request(request, results)
    except Exception as err:
        print('**** Logging failed with this error:', str(err))
    return render_template('results.html', the_results=results,
                           the_title='Here are you results', the_phrase=phrase, the_letters=letters)


@app.route('/')
@app.route('/entry')
def entry() -> 'html':
    return render_template('entry.html', the_title='Welcome to search4letters on the web!')


@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'You are now logged in'


@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'You are not logged in'


@app.route('/viewlog')
@check_log_in
def view_log() -> 'HTML':
    with UseDataBase(app.config['dbconfig']) as cursor:
        _SQL = """select phrase, letters, ip, browser_string, results from log"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
    titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=contents
                           )


if __name__ == '__main__':
    app.run(debug=True)
