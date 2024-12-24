from flask import Flask, render_template, request, redirect, url_for, session
import requests
import hmac
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = "BESTSECRETKEYINTHISWORLD"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['TELEGRAM_BOT_TOKEN'] = '7603091100:AAEPdzTz9pBZm5WEx_PBGJhnaRgsNyRZ60U'

VKID = "52878743" #ID приложения на vk.com/editapp?id=АйдиПриложения&section=options
REDIRECTURI = "https://yuliana.pythonanywhere.com" # Редирект посетителя после авторизации
VKSECRET = "HfWOvVZ35TKxJmsKRAPu" # Секретный ключ, найти можно на vk.com/editapp?id=АйдиПриложения&section=options и найти Защищенный ключ

app.jinja_env.globals.update(VKID = VKID) #айди приложения
app.jinja_env.globals.update(REDIRECTURI = REDIRECTURI) #редирект

@app.before_request
def make_session_permanent():
    session.permanent = True

def template(tmpl_name, **kwargs):
    vk = False
    user_id = session.get('user_id')
    first_name = session.get('first_name')
    photo = session.get('photo')

    if user_id:
        vk = True

    return render_template(tmpl_name,
                           vk = vk,
                           user_id = user_id,
                           name = first_name,
                           photo = photo,
                           **kwargs)

@app.route("/")
def index1():
    return template("index.html")

@app.route("/logout")
def logout():
    session.pop('user_id')
    session.pop('first_name')
    session.pop('last_name')
    session.pop('screen_name')
    session.pop('photo')

    return redirect(url_for('index'))

@app.route("/login")
def login():
    code = request.args.get("code")

    response = requests.get(f"https://oauth.vk.com/access_token?client_id={VKID}&redirect_uri={REDIRECTURI}&client_secret={VKSECRET}&code={code}")

    params = {
        "v": "5.101",
        "fields": "uid,first_name,last_name,screen_name,sex,bdate,photo_big",
        "access_token": response.json()['access_token']
    }

    get_info = requests.get(f"https://api.vk.com/method/users.get", params=params)
    get_info = get_info.json()['response'][0]

    session['user_id'] = get_info['id']
    session['first_name'] = get_info['first_name']
    session['last_name'] = get_info['last_name']
    session['screen_name'] = get_info['screen_name']
    session['photo'] = get_info['photo_big']


    return redirect(url_for('template', filename='index'))

@app.route('/')
def index():
    return '''
    <body>
        <script async
            src="https://telegram.org/js/telegram-widget.js?16"
            data-telegram-login="lublu_pitsu_bot"
            data-size="large"
            data-auth-url="http://your_domain.ngrok.io/login/telegram"
            data-request-access="write">
        </script>
    </body>
    '''


def check_response(data):
    d = data.copy()
    del d['hash']
    d_list = []
    for key in sorted(d.keys()):
        if d[key] != None:
            d_list.append(key + '=' + d[key])
    data_string = bytes('\n'.join(d_list), 'utf-8')

    secret_key = hashlib.sha256(app.config['TELEGRAM_BOT_TOKEN'].encode('utf-8')).digest()
    hmac_string = hmac.new(secret_key, data_string, hashlib.sha256).hexdigest()
    if hmac_string == data['hash']:
        return True
    return False


@app.route('/login/telegram')
def login_telegram():
    data = {
        'id': request.args.get('id', None),
        'first_name': request.args.get('first_name', None),
        'last_name': request.args.get('last_name', None),
        'username': request.args.get('username', None),
        'photo_url': request.args.get('photo_url', None),
        'auth_date': request.args.get('auth_date', None),
        'hash': request.args.get('hash', None)
    }

    if check_response(data):
        # Authorize user
        return template("index_1.html")
    else:
        return 'Authorization failed'


if __name__ == "__main__":
    app.run("0.0.0.0", debug = True)
