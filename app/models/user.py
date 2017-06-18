#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db
from app.models.MyModel import MyModelService

class User(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user'

    uid = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(15), default='')
    username = db.Column(db.String(32), default='')
    nickname = db.Column(db.String(32), default='')
    realname = db.Column(db.String(32), default='')
    avatar = db.Column(db.String(128), default='')
    gender = db.Column(db.Integer, default=0)
    birthday = db.Column(db.Integer, default=0)
    mobile_status = db.Column(db.Integer, default=0)
    pushtoken = db.Column(db.String(255), default='')
    usercode = db.Column(db.String(20), default='')

    def __str__(self):
        return "User => { \
uid:%d, mobile:'%s', username:'%s', nickname:'%s', realname:'%s',  \
avatar:'%s', gender:%d, birthday:%d, mobile_status:%d, pushtoken:'%s',  \
usercode:'%s'}" % (
self.uid, self.mobile, self.username, self.nickname, self.realname,
self.avatar, self.gender, self.birthday, self.mobile_status, self.pushtoken,
self.usercode)

    __repr__ = __str__


class UserCheckCode(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_check_code'

    ucc_id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(15), default='')
    check_code = db.Column(db.String(6), default='')
    expire_time = db.Column(db.Integer, default=0)
    check_type = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserCheckCode => { \
ucc_id:%d, mobile:'%s', check_code:'%s', expire_time:%d, check_type:%d}" % (
self.ucc_id, self.mobile, self.check_code, self.expire_time, self.check_type)

    __repr__ = __str__


class UserCheckHistory(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_check_history'

    uch_id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(15), default='')
    code = db.Column(db.String(6), default='')
    check_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserCheckHistory => { \
uch_id:%d, mobile:'%s', code:'%s', check_time:%d}" % (
self.uch_id, self.mobile, self.code, self.check_time)

    __repr__ = __str__


class UserDevice(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_device'

    ud_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    device_id = db.Column(db.String(64), default=None)
    device_name = db.Column(db.String(64), default='')
    device_vendor = db.Column(db.String(64), default='')
    device_os = db.Column(db.String(16), default='')
    device_os_version = db.Column(db.String(16), default='')
    device_model = db.Column(db.String(32), default='')
    app_version = db.Column(db.String(255), default='')

    def __str__(self):
        return "UserDevice => { \
ud_id:%d, uid:%d, device_id:'%s', device_name:'%s', device_vendor:'%s',  \
device_os:'%s', device_os_version:'%s', device_model:'%s', app_version:'%s'}" % (
self.ud_id, self.uid, self.device_id, self.device_name, self.device_vendor,
self.device_os, self.device_os_version, self.device_model, self.app_version)

    __repr__ = __str__


class UserLastTime(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_last_time'

    ult_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    last_type = db.Column(db.Integer, default=0)
    last_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserLastTime => { \
ult_id:%d, uid:%d, last_type:%d, last_time:%d}" % (
self.ult_id, self.uid, self.last_type, self.last_time)

    __repr__ = __str__


class UserLike(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_like'

    ul_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    nickname = db.Column(db.String(32), default='')
    avatar = db.Column(db.String(128), default='')
    desc = db.Column(db.String(255), default='')
    like_type = db.Column(db.Integer, default=0)
    like_id = db.Column(db.Integer, default=0)
    like_name = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserLike => { \
ul_id:%d, uid:%d, nickname:'%s', avatar:'%s', desc:'%s',  \
like_type:%d, like_id:%d, like_name:'%s', add_time:%d}" % (
self.ul_id, self.uid, self.nickname, self.avatar, self.desc,
self.like_type, self.like_id, self.like_name, self.add_time)

    __repr__ = __str__


class UserLocation(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_location'

    uid = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(64), default='')
    province = db.Column(db.String(64), default='')
    city = db.Column(db.String(64), default='')
    district = db.Column(db.String(64), default='')
    address = db.Column(db.String(128), default='')
    longitude = db.Column(db.Float, default=None)
    latitude = db.Column(db.Float, default=None)

    def __str__(self):
        return "UserLocation => { \
uid:%d, country:'%s', province:'%s', city:'%s', district:'%s',  \
address:'%s', longitude:%0.2f, latitude:%0.2f}" % (
self.uid, self.country, self.province, self.city, self.district,
self.address, self.longitude, self.latitude)

    __repr__ = __str__


class UserLog(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_log'

    ul_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=None)
    log_type = db.Column(db.Integer, default=0)
    log_message = db.Column(db.String(255), default='')
    ip = db.Column(db.Integer, default=None)

    def __str__(self):
        return "UserLog => { \
ul_id:%d, uid:%d, add_time:%d, log_type:%d, log_message:'%s',  \
ip:%d}" % (
self.ul_id, self.uid, self.add_time, self.log_type, self.log_message,
self.ip)

    __repr__ = __str__


class UserThirdBind(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_third_bind'

    utb_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    type = db.Column(db.Integer, default=0)
    third_user_id = db.Column(db.String(255), default='')
    third_res_text = db.Column(db.Text, default=None)

    def __str__(self):
        return "UserThirdBind => { \
utb_id:%d, uid:%d, add_time:%d, type:%d, third_user_id:'%s',  \
third_res_text:'%s'}" % (
self.utb_id, self.uid, self.add_time, self.type, self.third_user_id,
self.third_res_text)

    __repr__ = __str__


class UserPassword(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_password'

    uid = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(64), default='')
    salt = db.Column(db.String(32), default='')
    type = db.Column(db.Integer, primary_key=True)

    def __str__(self):
        return "UserPassword => { \
uid:%d, password:'%s', salt:'%s', type:%d}" % (
self.uid, self.password, self.salt, self.type)

    __repr__ = __str__


class UserAccount(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_account'

    uid = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.00)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserAccount => { \
uid:%d, balance:%0.2f, add_time:%d, update_time:%d}" % (
self.uid, self.balance, self.add_time, self.update_time)

    __repr__ = __str__


class UserAccountDetail(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_account_detail'

    uad_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    prev_balance = db.Column(db.Float, default=0.00)
    balance = db.Column(db.Float, default=0.00)
    amount = db.Column(db.Float, default=0.00)
    in_or_out = db.Column(db.Integer, default=0)
    action = db.Column(db.Integer, default=0)
    remark_for_user = db.Column(db.String(255), default='')
    remark_for_sys = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserAccountDetail => { \
uad_id:%d, uid:%d, prev_balance:%0.2f, balance:%0.2f, amount:%0.2f,  \
in_or_out:%d, action:%d, remark_for_user:'%s', remark_for_sys:'%s', add_time:%d}" % (
self.uad_id, self.uid, self.prev_balance, self.balance, self.amount,
self.in_or_out, self.action, self.remark_for_user, self.remark_for_sys, self.add_time)

    __repr__ = __str__


class UserAddress(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_address'

    ua_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    name = db.Column(db.String(32), default='')
    mobile = db.Column(db.String(15), default='')
    province = db.Column(db.String(32), default='')
    city = db.Column(db.String(32), default='')
    district = db.Column(db.String(32), default='')
    address = db.Column(db.String(255), default='')
    zip = db.Column(db.String(8), default='')
    is_default = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserAddress => { \
ua_id:%d, uid:%d, name:'%s', mobile:'%s', province:'%s',  \
city:'%s', district:'%s', address:'%s', zip:'%s', is_default:%d}" % (
self.ua_id, self.uid, self.name, self.mobile, self.province,
self.city, self.district, self.address, self.zip, self.is_default)

    __repr__ = __str__


class UserBillTitle(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_bill_title'

    ubt_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    bill_title = db.Column(db.String(64), default='')
    is_default = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserBillTitle => { \
ubt_id:%d, uid:%d, bill_title:'%s', is_default:%d, add_time:%d}" % (
self.ubt_id, self.uid, self.bill_title, self.is_default, self.add_time)

    __repr__ = __str__


class UserShoppingCart(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_shopping_cart'

    usc_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    gs_id = db.Column(db.Integer, default=0)
    buy_num = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserShoppingCart => { \
usc_id:%d, uid:%d, goods_id:%d, gs_id:%d, buy_num:%d,  \
add_time:%d, update_time:%d}" % (
self.usc_id, self.uid, self.goods_id, self.gs_id, self.buy_num,
self.add_time, self.update_time)

    __repr__ = __str__


class UserTroy(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_troy'

    uid = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), default='')
    cookies_obj = db.Column(db.Text, default=None)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserTroy => { \
uid:%d, password:'%s', cookies_obj:'%s', add_time:%d}" % (
self.uid, self.password, self.cookies_obj, self.add_time)

    __repr__ = __str__


class UserAdmin(db.Model, MyModelService):
    __bind_key__ = 'i-shan'
    __tablename__ = 'user_admin'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    role_id = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "UserAdmin => { \
id:%d, uid:%d, role_id:%d, add_time:%d}" % (
self.id, self.uid, self.role_id, self.add_time)

    __repr__ = __str__



