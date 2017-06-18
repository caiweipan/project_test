#coding=utf-8
#上传到正式七牛服务器
import sys,os
from qiniu import Auth
from qiniu import BucketManager
import qiniu
import uuid
import os.path
from datetime import date
from datetime import datetime
from datetime import timedelta

from flask import request, current_app
from werkzeug import FileStorage, secure_filename

def extension(filename):
    return filename.rsplit('.', 1)[-1]


def lowercase_ext(filename):
    if '.' in filename:
        main, ext = filename.rsplit('.', 1)
        return main + '.' + ext.lower()
    else:
        return filename.lower()


def addslash(url):
    if url.endswith('/'):
        return url
    return url + '/'


def file_allowed(storage, allowed):
    """
    判断文件类型是否允许上传
    @return boolean
    """
    basename = lowercase_ext(secure_filename(storage.filename))
    ext = extension(basename)
    return (ext in allowed)


class QiNiuOSS(object):
    """七牛文件存储"""
    def __init__(self, category, push_type=1, save_path='/data/upload/'):
        """初始化函数
        :param category 类型名称，如:avatar, gallery
        :param save_path 保存文件路径
        """
        self.category      = category
        self.save_path     = save_path
        self.target_folder = ''
        self.target        = ''
        self.key_name      = ''
        self.url           = ''
        self.push_type     = push_type

        # 文件类型
        self.IMAGES = ['jpg' , 'jpeg', 'png', 'bmp', 'gif']
        self.VIDEO = ['flv', 'avi', 'wmv',  'asf', 'dat', 'vob', 'mpg', 'mpeg','rm', 'rmvb', 'mp4', '3gp', 'mkv', 'ogg', 'ogv', 'mov']
        self.TEXT = ['txt']
        self.AUDIO = ['wav', 'mp3', 'aac', 'ogg', 'oga', 'flac']
        self.DOCUMENTS = ['rtf', 'odf', 'ods', 'gnumeric', 'abw', 'doc', 'docx', 'xls', 'xlsx']
        self.DATA = ['csv', 'ini', 'json', 'plist', 'xml', 'yaml', 'yml']
        self.SCRIPTS = ['js', 'php', 'pl', 'py', 'rb', 'sh']
        self.ARCHIVES = ['gz', 'bz2', 'zip', 'tar', 'tgz', 'txz', '7z']
        self.EXECUTABLES =['so', 'exe', 'dll']

        # 七牛配置
        self.access_key            = current_app.config['ACCESS_KEY']
        self.secret_key            = current_app.config['SECRET_KEY']
        self.bucket_name           = current_app.config['BUCKET_NAME']
        self.bucket_domain         = ''

    def save(self, storage):
        """保存文件
        :param storage werkzeug.FileStorage
        :param allowed 允许上传的文件类型，默认为图片类型
        :return
        """
        self.storage = storage

        if not isinstance(storage, FileStorage):
            raise TypeError("storage must be a werkzeug.FileStorage")

        folder = "%s" % date.today()
        name = "%s" % uuid.uuid4()
        self.basename = lowercase_ext(secure_filename(storage.filename))

        print u'### self.basename:%s'% self.basename
        basename = name + '.' + extension(self.basename)

        #输出扩张名
        print extension(basename)

        if self.push_type == 2:
            allowed = self.VIDEO
        elif self.push_type == 3:
            allowed = self.AUDIO
        elif self.push_type == 4:
            allowed = self.DOCUMENTS
        else:
            allowed = self.IMAGES

        if not file_allowed(storage, allowed):
            raise IOError("storage input error")

        # 目标目录不存在，则创建
        target_folder = os.path.join(self.save_path, self.category, folder)
        self.target_folder = target_folder
        print u'### target_folder:%s'% self.target_folder
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        target = os.path.join(target_folder, basename)
        self.key_name = os.path.join(self.category, folder, basename)

        headers = request.headers.get('User-Agent')
        if headers and 'Windows' in headers:
            target_folder = os.path.join(self.save_path, self.category) + '/'+ folder
            target = target_folder + '/' + basename
            self.key_name = self.category + '/' + folder + '/' + basename

        print u'### key_name:%s'% self.key_name
        try:
            storage.save(target)
            self.target = target
        except Exception, e:
            raise e

        self.q = Auth(self.access_key, self.secret_key)
        self.bucket = BucketManager(self.q)
        self.extension = os.path.splitext(self.storage.filename)[1]
        self.token = self.q.upload_token(self.bucket_name, self.key_name)

        return self.target


    def put_to_oss(self):
        """上传图片至七牛oss"""

        # push_type 1.图片 2.视频 3.音频 4.文档
        info , self.extension = '', self.extension[1:]
        if self.push_type == 2:
            extension = self.VIDEO
        elif self.push_type == 3:
            extension = self.AUDIO
        elif self.push_type == 4:
            extension = self.DOCUMENTS
        else:
            extension = self.IMAGES

        if self.extension in extension:
            if self.push_type == 1:
                ret, info = qiniu.put_file(self.token, self.key_name, self.target, mime_type="image/*", check_crc=True)
            else:
                ret, info = qiniu.put_file(self.token, self.key_name, self.target, check_crc=True)
            assert ret['key'] == self.key_name
            assert ret['hash'] == qiniu.etag(self.target)

        if info and info.status_code != 200:
            print 'info.status:%s'% info.status_code
            return ''

        self.url = 'http://qiniu.i-shan.com/' + self.key_name
        return self.url


    def get_token(self, basename):
        """获取token"""

        folder = "%s" % date.today()
        name = "%s" % uuid.uuid4()
        self.basename = basename
        print u'### basename:%s'% self.basename
        basename = name + '.' + extension(self.basename)

        self.key_name = os.path.join(self.category, folder, basename)

        print u'### key_name:%s'% self.key_name

        self.q = Auth(self.access_key, self.secret_key)
        # self.bucket = BucketManager(self.q)
        self.token = self.q.upload_token(self.bucket_name, self.key_name)

        return self.token


    # def headers(self):
    #     """设置S3文件过期时间"""
    #     meta = {}

    #     five_year = datetime.now() + timedelta(days=365*5)

    #     # HTTP/1.0 (5 years)
    #     meta['Expires'] = '%s GMT+0800' % five_year.strftime('%a %b %d %Y %H:%M:%S')

    #     # HTTP/1.1 (5 years)
    #     five_year_sec = 5*365*24*60*60
    #     meta['Cache-Control'] = 'max-age=%d' % five_year_sec
    #     return meta


    # def thumb(self, width=0, height=0, quality=100):
    #     """生成缩略图
    #     http://imgs-storage.cdn.aliyuncs.com/help/oss/OSS%E5%9B%BE%E7%89%87%E5%A4%84%E7%90%86%E6%9C%8D%E5%8A%A1API.pdf?spm=5176.7150518.1996836753.5.DzoRET&file=OSS%E5%9B%BE%E7%89%87%E5%A4%84%E7%90%86%E6%9C%8D%E5%8A%A1API.pdf
    #     """

    #     thumb_params = '@%dQ' % quality
    #     if width > 0:
    #         thumb_params += '_%dw' % width

    #     if height > 0:
    #         thumb_params += '_%dh' % height

    #     return self.url + thumb_params


    # def size(self):
    #     """获取图片宽度和高度
    #     :return (width, height)
    #     """
    #     import Image
    #     im = Image.open(self.target)
    #     return im.size


    # def traverse_dir(theDir):
    #   for f in os.listdir(theDir):
    #       afile = os.path.join(theDir,f)
    #       if os.path.isfile(afile):
    #           prefix = os.path.basename(theDir)
    #           if prefix == 'qiniu':
    #               key = f
    #           else:
    #               key = prefix + '/' + f
    #           print key
    #           # img_upload(afile,key)
    #       elif os.path.isdir(afile):
    #           traverse_dir(afile)
    #           pass


    # traverse_dir(adir)

    # def scanDir():
    #     count = 0
    #     for parent,dirnames,filenames in os.walk(adir):
    #         print '-----------------------'
    #         print "parent is:" + parent
    #         print '-----------------------'
    #         count += len(filenames)
    #         for filename in filenames:
    #             filepath = os.path.join(parent,filename)
    #             key = filepath.replace(adir,'')
    #             print "key is:" + key
    #             img_upload(filepath,key)
    #     print count
    # scanDir()
