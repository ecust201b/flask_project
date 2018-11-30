# wtf.html 的改动

## WTF.html 源码中的改动
在 util.wtf 中加入了一个自定义的 multicheckboxfield, 用于管理员修改工程师的设备查看权限

同时, 在 /usr/local/python3.5/lib/python3.5/site-packages/flask_bootstrap/templates/bootstrap/wtf.html 中做出如下修改

在 84 行之后加入

```html
{%- elif 'Multi' in field.type  -%}
  <div class="multiField">
    <label>{{ field.label }}</label><br/>
    {% for item in field -%}
      {% call _hz_form_wrap(horizontal_columns, form_type, True, required=required) %}
        {{form_field(item,form_type,horizontal_columns,button_map)}}
      {% endcall %}
    {% endfor %}
  </div>
```

同时将 42 行改为

```html
<div class="checkbox-inline">
```

## wtform 中 FormField 和 FieldList 连用

需求描述: 工程师创建新设备时需要输入传感器的初始值，每个设备的传感器数量不同，因此传感器初始值数量列表需要可变。

解决方案: 参考[动态变化表单](https://gist.github.com/kageurufu/6813878#file-flask-py-L51)的实现思路

1. 在 engineer blueprint 的 forms.py 中 创建如下两个 Form: 

```python
class SencerForm(Form):
    sencer_name = StringField('传感器位号：', validators=[Required()], render_kw={"placeholder": "位号"})
    no_load = StringField('传感器无负载读数：', validators=[Required()], render_kw={"placeholder": "无负载读数(mV)"})
    standard_load = StringField('传感器标定读数：', validators=[Required()], render_kw={"placeholder": "标定读数(mV)"})
    zero_point = StringField('传感器零点：', validators=[Required()], render_kw={"placeholder": "零点"})
    empty_load = StringField('传感器空载读数：', validators=[Required()], render_kw={"placeholder": "空载读数(mV)"})    
    exec_v = StringField('激励电压(mV)：', validators=[Required()], render_kw={"placeholder": "激励电压(mV)"})
    sensitivity = StringField('传感器灵敏度(mV)：', validators=[Required()], render_kw={"placeholder": "灵敏度(mV/V)"})
    resistance = StringField('传感器阻抗(Ω)：', validators=[Required()], render_kw={"placeholder": "传感器阻抗(Ω)"})


class SencerFormNoCsrf(SencerForm):
    def __init__(self, *args, **kwargs):
        super(SencerFormNoCsrf, self).__init__(meta={'csrf':False}, *args, **kwargs)


class SetForm(Form):
    eqp_name = StringField('设备号：', validators=[Required()])
    eqp_location = StringField('设备所处工段：', validators=[Required()])
    supplier = StringField('供应商：', validators=[Required()])
    supplier_info = StringField('供应商信息：', validators=[Required()])
    supplier_con = StringField('供应商联系方式：', validators=[Required()])
    num = StringField('传感器数量：', validators=[Required()])
    temperature = StringField('记录时环境温度(℃)：', validators=[Required()])
    wet = StringField('记录时环境湿度(%)：', validators=[Required()])
    sencer_info = FieldList(FormField(SencerFormNoCsrf), min_entries=1)
    submit = SubmitField('提交信息')

    def __init__(self, *args, **kwargs):
        super(SetForm, self).__init__(*args, **kwargs)
```

2. 由于该表单用 wtf.quick_form 直接渲染格式不正确，所以自定义 jinja2 渲染函数 template/macro.html, 文件太长这里不贴进来了

3. 前端交互文件，通过增加和删除按钮，增加/删除传感器，文件在 static/engineer/SetPoint.js

4. 在 engineer/view.py 中加入渲染路由

**tips:**

* 注意 wtf 表单为保证表单的数据安全会给每一个表单做 CSRF 保护, 其中 FormField 中用到的表单也同样会做保护, 因此需要创建一个禁用该功能的表单, 即示例中的 SencerFormNoCsrf 表单。同时外层表单的 CSRF 保护不取消，这样依旧能保证 CSRF 保护起作用。

* 在 debug 调试表单过程中，可以在 view.py 的对应路由函数中用 flash(form.errors) 来把表单提交的错误打印到前端，方便调试

参考资料:

[动态变化表单](https://gist.github.com/kageurufu/6813878#file-flask-py-L51), js里面有几个小错误

[表单 CSRF 功能禁用](https://stackoverflow.com/questions/15649027/wtforms-csrf-flask-fieldlist)
