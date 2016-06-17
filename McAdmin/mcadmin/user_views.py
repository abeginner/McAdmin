# coding=utf-8

from django.shortcuts import render
from django.contrib.auth import *
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.views.generic.base import View

import os
import ImageFont,Image,ImageDraw,random
import cStringIO
import time

from mcadmin_forms import *

class CheckCodeView(View):

    def get(self, request, *args, **kwargs):
        "通过PIL生成验证码"
        #规格参数设定
        check_code = 4
        img_width = 80
        img_height = 40
        background = (random.randrange(230,255),random.randrange(230,255),random.randrange(230,255))
        line_color = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
        font_color =  ['black','darkblue','darkred']
        font_size = 19
        font = ImageFont.truetype(os.path.join(os.path.abspath(__file__), 'tmp/msyh.ttf'), font_size)
        
        #生成验证码字符串
        code = '123456789ACEFGHKMNPRTUVWXY'
        code_len = len(code)
        str = ''
        for i in xrange(0, check_code):
            str += code[random.randrange(0, code_len)]
    
        #新建画布，画笔对象
        img = Image.new('RGB', (img_width, img_height), background)
        draw = ImageDraw.Draw(img)
    
        #划干扰线
        for i in range(random.randrange(3,5)):
            xy = (random.randrange(0,img_width),random.randrange(0,img_height),
                random.randrange(0,img_width),random.randrange(0,img_height))
            draw.line(xy,fill=line_color,width=1)
    
        #生成验证码图片
        x = 2
        for i in str:
            y = random.randrange(0,10)
            draw.text((x,y), i, font=font, fill=random.choice(font_color))
            x += font_size
        del x
    
        request.session['checkcode'] = str
    
        buf = cStringIO.StringIO()
        img.save(buf,'jpeg')
        buf.seek(0)
        return HttpResponse(buf.getvalue(),'image/jpg')
    

class LoginView(View):
    form_class = LoginForm
    template_name = 'login.html'
    
    def get(self, request, error_message='', *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/index/')
        c = {}
        c.update(csrf(request))
        c.update({'error_message': error_message})
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
        
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/index/')
        error_message = ''
        c = {}
        c.update(csrf(request))
        username = request.POST['username']
        password = request.POST['password']
        check_code = request.POST['check_code']
        real_check_code = request.session['checkcode']
        if check_code != real_check_code:
            error_message += '验证码错误，'
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            userinfo = get_userinfo(username = username)
            request.session['my_username'] = userinfo['username']
            request.session['my_nickname'] = userinfo['nickname']
            request.session['my_user_id'] = userinfo['user_id']
            return HttpResponse('登录成功')
        else:
            error_message = '用户名或密码错误'
        return self.get(request, error_message)

