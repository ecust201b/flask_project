from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import Required, Length, EqualTo
from wtforms import ValidationError
from ..models import User, Role, Factory, Eqp
from ..util.wtf.wtf_field import MultiCheckboxField
from ..util.db.mongo import mongo_service
from ..util.form.form_util import eqp_find


class LoginForm(Form):
    username = StringField('用户名', validators=[Required(), Length(1, 64)])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField('登录')


class RegisterForm(Form):
    username = StringField('用户名', validators=[Required(), Length(1, 64)])
    password = PasswordField('密码',
                             validators=[Required(),
                                         EqualTo('confirm',
                                         message='密码错误')])
    confirm = PasswordField('确认密码', validators=[Required()])
    factory = SelectField('工厂号', coerce=str)
    role = SelectField('登录权限', coerce=int)
    submit = SubmitField('注册')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        factorys = [f.FID for f in Factory.objects]
        self.factory.choices = [(factory, factory) for factory, factory in zip(factorys, factorys)]
        self.role.choices = [(role.RID, role.name) for role in Role.objects.order_by("+RID")]

    def validate_ID(self, field):
        if User.objects(UID=field.data).first():
            raise ValidationError('工号已被注册')


class UserEdit(Form):
    username = StringField('用户名', validators=[Required(), Length(1, 64)])
    role = SelectField('登录权限', coerce=int)
    eqp_list = MultiCheckboxField('可操作设备')
    submit = SubmitField('确认修改')

    def __init__(self, current_user, *args, **kwargs):
        super(UserEdit, self).__init__(*args, **kwargs)
        self.role.choices = [(role.RID, role.name) for role in Role.objects.order_by("+RID")]
        self.eqp_list.choices = [(e.EID, e.EID) for e in eqp_find(current_user)]