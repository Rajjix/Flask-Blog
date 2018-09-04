from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import login_user,current_user,logout_user,login_required
from mysite import db
from mysite.models import User,BlogPost
from mysite.users.forms import RegistrationForm,LoginForm,UpdateUserForm
from mysite.users.picture_handler import add_profile_pic
from mysite.token import generate_confirmation_token, confirm_token
from mysite.email import send_email


users = Blueprint('users',__name__)


###Register###
@users.route('/register',methods=['GET','POST'])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():
        if form.username.data != db.session.query(User.username).filter_by(username=form.username.data).scalar():
            if form.email.data != db.session.query(User.email).filter_by(email=form.email.data).scalar():
                user = User(email=form.email.data,
                            username = form.username.data,
                            password = form.password.data,
                            is_active=False)

                db.session.add(user)
                db.session.commit()
                token = generate_confirmation_token(user.email)
                confirm_url = url_for('users.confirm_email', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url)
                subject = "Please confirm your email"
                send_email(form.email.data, subject, html)
                #login_user(user)
                flash('A confirmation email has been sent via email.', 'success')
                return redirect(url_for('users.login'))
            else:
                flash("Email Already Registered")
        else:
            flash("Username Already Exists")
    return render_template('register.html',form=form)

###login###
@users.route('/login',methods=['GET','POST'])
def login():
    
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == db.session.query(User.email).filter_by(email=form.email.data).scalar():
            user = User.query.filter_by(email=form.email.data).first()
            if user.check_password(form.password.data):
                if user.is_active:
                    login_user(user)
                    flash('Log in success')

                    next = request.args.get('next')

                    if next == None or not next[0]=='/':
                        next = url_for('core.index')

                    return redirect(next)
                else:
                    flash("User not activated")
            else:
                flash("Invalid Password!")
        else:
            flash("Email Not Registered!")
    return render_template('login.html',form=form)

###Logout###
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))

###Account
@users.route('/account',methods=['GET','POST'])
@login_required
def account():

    form = UpdateUserForm()
    if form.validate_on_submit():

        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data,username)
            current_user.profile_image=pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('User Account Update')
        #return redirect(url_for('users.account'))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email


    profile_image = url_for('static',filename='profile_pics/'+current_user.profile_image)
    return render_template('account.html',profile_image=profile_image,form=form)

@users.route('/confirm/<token>')
#@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.is_active:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('core.index'))


@users.route('/<username>')
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()

    blog_posts = BlogPost.query.filter_by(author=user).order_by(BlogPost.date.desc()).paginate(page=page,per_page=5)
    return render_template('user_blog_posts.html',blog_posts=blog_posts,user=user)
