#!/usr/bin/env python
#coding=utf-8

import json, urllib2, re

from flask import current_app, request, session

from codingabc.database import db
from codingabc.ext.aliyun import AliyunOSS, UploadNotAllowed
from codingabc.helpers import log_debug, log_info, log_error, toint

from app.helpers.date_time import current_timestamp
from app.models.news import News


class SaveNewsService(object):
    """ 保存资讯service """

    def __init__(self, form, news_id=0):
        self.errmsg       = {}
        self.form         = form
        self.news_id      = news_id
        self.current_time = current_timestamp()
        self.is_new       = False
        self.news         = None
        self.news_img     = ''

    def check(self):
        """ 检查 """
        # 资讯主图
        status       = toint(self.form.get('status'), 0)
        is_top       = toint(self.form.get('is_top'), 0)
        _news_img = request.files.get('news_img', None)

        # 是否创建资讯
        self.is_new = True if self.news_id == 0 else False

        # 检查 - 必填项
        # required_arr = ['title', 'detail', 'status', 'jingdu_weidu', 'nc_id']
        required_arr = ['title', 'detail', 'status', 'is_top', 'nc_id']
        for key in required_arr:
            value = self.form.get(key, '').strip()
            if not value:
                self.errmsg[key] = u'必填项'

        # 检查 - 新建资讯是否上传资讯主图
        if self.is_new and not _news_img:
            self.errmsg['news_img'] = u'必填项'

        # 检查 - 资讯是否存在
        if not self.is_new:
            self.news = News.get(self.news_id)
            if not self.news:
                self.errmsg['submit'] = u'资讯不存在'

        if status == -1:
            self.errmsg['status'] = u'请选择显示状态'

        if is_top == -1:
            self.errmsg['is_top'] = u'请选择是否推荐到首页'

        # 检查 - 资讯主图是否合法
        if _news_img:
            oss = AliyunOSS('news', current_app.config['SAVE_TARGET_PATH'])
            try:
                oss.save(_news_img)
                self.news_img = oss.put_to_oss()
            except UploadNotAllowed, e:
                self.errmsg['news_img'] = u'资讯主图只允许是图片文件'
            except Exception, e:
                self.errmsg['news_img'] = u'资讯主图上传失败'

        if len(self.errmsg) > 0:
            return False

        return True

    def save(self):
        """ 保存 """

        title        = self.form.get('title', '').strip()
        desc         = self.form.get('desc', '').strip()
        detail       = self.form.get('detail', '').strip()
        author_name  = self.form.get('author_name', '').strip()
        news_video   = self.form.get('news_video', '').strip()
        sort_order   = toint(self.form.get('sort_order', 0))
        status       = toint(self.form.get('status', 0))
        is_top       = toint(self.form.get('is_top', -1))
        nc_id        = toint(self.form.get('nc_id', 0))
        # jingdu_weidu = self.form.get('jingdu_weidu', None)
        # longitude, latitude = None, None
        # if jingdu_weidu:
        #     jingdu_weidu_arr = jingdu_weidu.split(',')
        #     if len(jingdu_weidu_arr) == 2:
        #         longitude = jingdu_weidu_arr[0]
        #         latitude = jingdu_weidu_arr[1]

        if self.is_new:
            self.news = News.create(add_time=self.current_time)

        # 资讯主图
        if self.news_img:
            self.news.update(news_img=self.news_img)

        # self.news.update(title=title, desc=desc, detail=detail,longitude=longitude, latitude=latitude,
        #                 sort_order=sort_order, status=status,nc_id=nc_id, commit=True)

        # 正则匹配出图片地址
        reg      = 'src="([^ >]+\.(?:jpeg|jpg|png))"'
        imgre    = re.compile(reg)
        imglist  = re.findall(imgre, detail)
        img_list = json.dumps(imglist)


        video_html = '<p><iframe webkitallowfullscreen="" mozallowfullscreen="" allowfullscreen="" frameborder="0" height="498" width="510" src="%s" class="note-video-clip"></iframe><br></p>'% news_video if news_video else self.news.video_html
        self.news.update(title=title,
                        desc=desc,
                        detail=detail,
                        sort_order=sort_order,
                        news_video=news_video,
                        video_html=video_html,
                        author_name=author_name,
                        is_top=is_top,
                        status=status,
                        nc_id=nc_id,
                        img_list=img_list,
                        commit=True)
        return True




