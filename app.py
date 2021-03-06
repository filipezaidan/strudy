from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from sqlalchemy import update
from config import bd
from controller.usuario import usuario_blueprint
from model.usuario import Usuario

TEMPLATES = './view'
STATIC = './static'

app = Flask(__name__, static_url_path='', template_folder=TEMPLATES, static_folder=STATIC)
app.register_blueprint(usuario_blueprint)

# Configuração do Banco de Dados
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./dados.db'
bd.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para ter acesso a plataforma!'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
   return Usuario.query.get(int(user_id))

with app.app_context():
    bd.create_all()

@app.route('/')
def login():
    if current_user.is_active == True:
        #CASO TENHA CONTRA LOGADA,REDIRECIONA AUTOMATICAMENTE PARA A ROTA HOME
        return redirect(url_for('home'))
    else:
        # CASO NÃP TENHA CONTA LOGADA, RENDERIZA A PAGINA "LOGIN"
        return render_template('login.html')

@app.route('/home')
def home():
    if current_user.is_active == False:
        print('nao tem conta')
        flash('Faça login para ter acesso a plataforma', 'error')
        return render_template('login.html')

    if current_user.email == "admin@admin.com":
        return redirect(url_for('admin'))
    return render_template('index.html', user=current_user)
@app.route('/admin')
def admin():
    if current_user.is_active == False:
        print('nao tem conta')
        flash('Faça login para ter acesso a plataforma', 'error')
        return redirect(url_for('login'))

    if current_user.is_active == True and current_user.email != 'admin@admin.com':
        # flash('Você não tem privilégios administrativos!', 'error')
        return redirect(url_for('home'))
    usuarios = Usuario.query.all()
    return render_template('mostraUsuarios.html', usuarios=usuarios)


@app.route('/dashboard', methods=['POST'])
def dashboard():
    email = request.form.get('email')
    password = request.form.get('password')

    user = Usuario.query.filter_by(email=email).first()

    if not user  or not check_password_hash(user.password, password):
        flash('Por favor, verifique suas credenciais e tente novamente!', 'error')
        return redirect(url_for('login'))
    
    if user.email == "admin@admin.com" and check_password_hash(user.password, "adminadmin"):
        login_user(user)
        return redirect(url_for('admin'))
    login_user(user)
    return redirect(url_for('home'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/savedLives')
def savedlives():
    return render_template('savedLives.html', user=current_user)

@app.route('/testsDone')
def testsDone():
    return render_template('testsDone.html', user=current_user)

@app.route('/testsPending')
def testsPending():
    return render_template('testsPending.html', user=current_user)

@app.route('/graphics')
def graphics():
    return render_template('graphics.html', user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    flash("Conta deslogada com sucesso!", 'success')
    return redirect(url_for('login'))

@app.route('/recoverPassword')
def recoverPassword():
    flash('Função em fase de desenvolvimento', 'info')
    return render_template('recoverPassword.html')

@app.route('/account')
def account():
    if current_user.is_active == False:
        print('nao tem conta')
        flash('Faça login para ter acesso a plataforma', 'error')
        return render_template('login.html')
    
    return render_template('account.html',user=current_user)

@app.route('/deleteAccount/<int:id>', methods=['POST'])
def deleteAccount(id):
    if current_user.is_active == False:
        print('nao tem conta')
        flash('Faça login para ter acesso a plataforma', 'error')
        return render_template('login.html')
    else:
        
        user = Usuario.query.filter_by(id=id).first()
        bd.session.delete(user)
        bd.session.commit()
        logout_user()
        flash("Conta deletada com sucesso!", "success")

        return redirect(url_for('login'))
@app.route('/deleteAccountAdmin/<int:id>', methods=['POST'])
def deleteAccountAdmin(id):
    if current_user.is_active == False:
        print('nao tem conta')
        flash('Faça login para ter acesso a plataforma', 'error')
        return render_template('login.html')
    else:
        
        user = Usuario.query.filter_by(id=id).first()
        bd.session.delete(user)
        bd.session.commit()
        
        return redirect(url_for('admin'))

@app.route('/profile')
def profile():
    if current_user.is_active == False:
        print('nao tem conta')
        flash('Faça login para ter acesso a plataforma', 'error')
        return render_template('login.html')
    
    return render_template('profile.html',user=current_user)
@app.route('/editProfile/<int:id>', methods=['POST'])
def editProfile(id):
    if current_user.is_active == False:
        print('nao tem conta')
        flash('Faça login para ter acesso a plataforma', 'error')
        return render_template('login.html')
    else:
    
        name = request.form.get('name')
        email = request.form.get('email')


        user = Usuario.query.filter_by(id=id).first()
        user.nome = name
        user.email = email
        bd.session.commit()
        flash("Perfil atualizado com sucesso!", "success")

        return redirect(url_for('profile'))
@app.route('/editProfileAdmin/<int:id>', methods=['POST'])
def editProfileAdmin(id):
    
    
        name = request.form.get('name')
        email = request.form.get('email')


        user = Usuario.query.filter_by(id=id).first()
        user.nome = name
        user.email = email
        bd.session.commit()
        flash("Perfil atualizado com sucesso!", "success")

        return redirect(url_for('admin'))

@app.route('/createAccount', methods=['POST'])
def createAccount():
    nome = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    user = Usuario.query.filter_by(email=email).first()

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Conta com esse endereço de e-mail já existe', 'info')
        return redirect(url_for('register'))
        #return render_template('register.html', msg='Email em uso')


    usuario = Usuario(nome, email, password=generate_password_hash(password, method='sha256'))
    bd.session.add(usuario)
    bd.session.commit()
    flash('Conta criada com sucesso!', 'success')
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# app.run(host='0.0.0.0', port=5000)