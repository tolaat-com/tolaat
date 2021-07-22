from flask_wtf import FlaskForm, RecaptchaField
from wtforms import HiddenField, IntegerField, RadioField, StringField, PasswordField
from wtforms import widgets, SelectMultipleField, BooleanField
from wtforms import FileField

class CaseForm(FlaskForm):
    case_type = HiddenField('case_type')
    view_id = HiddenField('view_id')
    recaptcha = RecaptchaField()


class ScrapForm(FlaskForm):
    case_type = RadioField('תיק', choices=[('בית משפט', 'בית משפט'), ('תעבורה', 'תעבורה')])
    number = IntegerField('מספר')
    month = IntegerField('חודש')
    year = IntegerField('שנה')
    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    email = StringField('דוא"ל')
    password = PasswordField('סיסמא')
    next = HiddenField('הבא')
    recaptcha = RecaptchaField()


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class CensorshipForm(FlaskForm):
    key = HiddenField('key')
    censored = BooleanField('להסתיר')
    pages =  StringField('הסתר')
    recaptcha = RecaptchaField()



class FaxForm(FlaskForm):
    fax =  FileField('הסתר')
    recaptcha = RecaptchaField()
    faxnumer = StringField('מספר')
    agree = BooleanField('הסכמם')


class FaxConfirmForm(FlaskForm):
    fax_id = HiddenField('מספר')
    recaptcha = RecaptchaField()


class EmailForm(FlaskForm):
    email =  StringField('דוא"ל')
    recaptcha = RecaptchaField()
