from flask import Flask, url_for, redirect, render_template, request, flash, Blueprint
from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext import admin, login
import wtforms as wtf
from flask.ext.admin import helpers, expose
import models
from .forms import RegistrationForm, LoginForm
from flask.ext.admin.actions import action

# Create customized model view class
class PrivateModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


class AdminModelView(ModelView):
    def is_accessible(self):
        return hasattr(login.current_user, 'admin') and login.current_user.admin


class CMTextAreaWidget(wtf.widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs['class'] = kwargs.get("class", "") + ' cmeditor'
        return super(CMTextAreaWidget, self).__call__(field, **kwargs)


class CMTextAreaField(wtf.fields.TextAreaField):
    widget = CMTextAreaWidget()


class EuTemplateView(PrivateModelView):
    column_filters = ['name']

    column_exclude_list = ("text", )

    create_template = 'edit.html'
    edit_template = 'edit.html'

    form_overrides = dict(text=CMTextAreaField)

    form_args = dict(column_class="col-md-6")

    form_widget_args = {
        'usedTimes': {
            'disabled': True
        },
    }

    def is_accessible(self):
        return login.current_user.is_authenticated()


class EuFormatView(PrivateModelView):
    column_filters = ['name']
    form_overrides = dict(description=wtf.fields.TextAreaField)

    def is_accessible(self):
        return login.current_user.is_authenticated()


class TranslationRequestView(AdminModelView):
    column_default_sort = ('requested', True)
    @action('clean_files', 'Clean files',
            'Are you sure you want to delete the associated files?')
    def action_clean_files(self, ids):
        reqs = models.TranslationRequest.objects(pk__in=ids)
        for req in reqs:
            req.clean_files()

# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = models.User()
            form.populate_obj(user)
            user.save()
            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


class UserView(AdminModelView):
    column_exclude_list = form_excluded_columns = ('password', )
    form_extra_fields = {
        "password": wtf.fields.PasswordField('New Password')
    }

    def update_model(self, form, model):
        if not form.password.data:
            flash('Password unchanged')
            form.password.data = model.password
        super(UserView, self).update_model(form, model)


def make_admin(app):
    myadmin = Admin(app, index_view=MyAdminIndexView(),
                    base_template='my_master.html',)
                    #template_mode='bootstrap3')
    myadmin.add_view(EuFormatView(models.EuFormat))
    myadmin.add_view(EuTemplateView(models.EuTemplate))
    myadmin.add_view(TranslationRequestView(models.TranslationRequest))
    myadmin.add_view(UserView(models.User))
    return myadmin

