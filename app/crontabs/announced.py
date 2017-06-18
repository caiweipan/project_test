#!/usr/bin/env python
#coding=utf-8

import time, datetime, random, string

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text, Date
from sqlalchemy.sql import func, or_

__all__ = ['db']
db = SQLAlchemy()


DB_CONNECT_STRING = 'mysql://root:123456@127.0.0.1/i-shan?charset=utf8mb4'
#DB_CONNECT_STRING = 'mysql://root:123456@192.168.199.253/i-shan?charset=utf8mb4'
Base = declarative_base()

engine      = create_engine(DB_CONNECT_STRING, echo=False)
DB_Session  = sessionmaker(bind=engine)
session     = DB_Session()
session._model_changes = {}


class User(Base):
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


class Order(Base):
    __tablename__ = 'order'

    order_id = db.Column(db.Integer, primary_key=True)
    tran_id = db.Column(db.Integer, default=0)
    uid = db.Column(db.Integer, default=0)
    order_type = db.Column(db.Integer, default=0)
    order_status = db.Column(db.Integer, default=0)
    order_desc = db.Column(db.String(255), default='')
    user_remark = db.Column(db.Text, default=None)
    goods_amount = db.Column(db.Float, default=0.00)
    goods_name_list = db.Column(db.Text, default=None)
    goods_img_list = db.Column(db.Text, default=None)
    goods_price_list = db.Column(db.Text, default=None)
    goods_num_list = db.Column(db.Text, default=None)
    lottery_id_list = db.Column(db.Text, default=None)
    lottery_name_list = db.Column(db.Text, default=None)
    lottery_img_list = db.Column(db.Text, default=None)
    section_number_list = db.Column(db.Text, default=None)
    order_amount = db.Column(db.Float, default=0.00)
    discount_amount = db.Column(db.Float, default=0.00)
    discount_desc = db.Column(db.String(255), default='')
    pay_amount = db.Column(db.Float, default=0.00)
    pay_method = db.Column(db.String(16), default='')
    pay_type = db.Column(db.Integer, default=0)
    pay_status = db.Column(db.Integer, default=0)
    pay_tran_id = db.Column(db.String(32), default='')
    paid_time = db.Column(db.Integer, default=0)
    paid_amount = db.Column(db.Float, default=0.00)
    shipping_id = db.Column(db.Integer, default=0)
    shipping_name = db.Column(db.String(32), default='')
    shipping_amount = db.Column(db.Float, default=0.00)
    shipping_sn = db.Column(db.String(32), default='')
    shipping_status = db.Column(db.Integer, default=0)
    shipping_time = db.Column(db.Integer, default=0)
    deliver_status = db.Column(db.Integer, default=0)
    deliver_time = db.Column(db.Integer, default=0)
    milestone_status = db.Column(db.Integer, default=0)
    milestone_text = db.Column(db.String(20), default='')
    is_comment = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Order => { \
order_id:%d, tran_id:%d, uid:%d, order_type:%d, order_status:%d,  \
order_desc:'%s', user_remark:'%s', goods_amount:%0.2f, goods_name_list:'%s', goods_img_list:'%s',  \
goods_price_list:'%s', goods_num_list:'%s', lottery_id_list:'%s', lottery_name_list:'%s', lottery_img_list:'%s',  \
section_number_list:'%s', order_amount:%0.2f, discount_amount:%0.2f, discount_desc:'%s', pay_amount:%0.2f,  \
pay_method:'%s', pay_type:%d, pay_status:%d, pay_tran_id:'%s', paid_time:%d,  \
paid_amount:%0.2f, shipping_id:%d, shipping_name:'%s', shipping_amount:%0.2f, shipping_sn:'%s',  \
shipping_status:%d, shipping_time:%d, deliver_status:%d, deliver_time:%d, milestone_status:%d,  \
milestone_text:'%s', is_comment:%d, add_time:%d, update_time:%d}" % (
self.order_id, self.tran_id, self.uid, self.order_type, self.order_status, 
self.order_desc, self.user_remark, self.goods_amount, self.goods_name_list, self.goods_img_list, 
self.goods_price_list, self.goods_num_list, self.lottery_id_list, self.lottery_name_list, self.lottery_img_list, 
self.section_number_list, self.order_amount, self.discount_amount, self.discount_desc, self.pay_amount, 
self.pay_method, self.pay_type, self.pay_status, self.pay_tran_id, self.paid_time, 
self.paid_amount, self.shipping_id, self.shipping_name, self.shipping_amount, self.shipping_sn, 
self.shipping_status, self.shipping_time, self.deliver_status, self.deliver_time, self.milestone_status, 
self.milestone_text, self.is_comment, self.add_time, self.update_time)

    __repr__ = __str__


class LotteryTemplate(Base):
    __tablename__ = 'lottery_template'

    lt_id = db.Column(db.Integer, primary_key=True)
    section_number = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    lottery_name = db.Column(db.String(255), default='')
    lottery_desc = db.Column(db.Text, default=None)
    lottery_img = db.Column(db.String(255), default='')
    lottery_price = db.Column(db.Float, default=0.00)
    finish_quantity = db.Column(db.Integer, default=0)
    max_quantity = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "LotteryTemplate => { \
lt_id:%d, section_number:%d, goods_id:%d, lottery_name:'%s', lottery_desc:'%s',  \
lottery_img:'%s', lottery_price:%0.2f, finish_quantity:%d, max_quantity:%d, status:%d,  \
add_time:%d}" % (
self.lt_id, self.section_number, self.goods_id, self.lottery_name, self.lottery_desc, 
self.lottery_img, self.lottery_price, self.finish_quantity, self.max_quantity, self.status, 
self.add_time)

    __repr__ = __str__


class Lottery(Base):
    __tablename__ = 'lottery'

    lottery_id = db.Column(db.Integer, primary_key=True)
    lt_id = db.Column(db.Integer, default=0)
    section_number = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    lottery_name = db.Column(db.String(255), default='')
    lottery_desc = db.Column(db.Text, default=None)
    lottery_img = db.Column(db.String(255), default='')
    lottery_price = db.Column(db.Float, default=0.00)
    lottery_status = db.Column(db.Integer, default=0)
    finish_quantity = db.Column(db.Integer, default=0)
    join_quantity = db.Column(db.Integer, default=0)
    remain_quantity = db.Column(db.Integer, default=0)
    max_quantity = db.Column(db.Integer, default=0)
    schedule = db.Column(db.Integer, default=0)
    announced_time = db.Column(db.Integer, default=0)
    prize_number = db.Column(db.Integer, default=0)
    prize_uid = db.Column(db.Integer, default=0)
    prize_nickname = db.Column(db.String(32), default='')
    prize_avatar = db.Column(db.String(128), default='')
    prize_goods_num = db.Column(db.Integer, default=0)
    prize_time = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "Lottery => { \
lottery_id:%d, lt_id:%d, section_number:%d, goods_id:%d, lottery_name:'%s',  \
lottery_desc:'%s', lottery_img:'%s', lottery_price:%0.2f, lottery_status:%d, finish_quantity:%d,  \
join_quantity:%d, remain_quantity:%d, max_quantity:%d, schedule:%d, announced_time:%d,  \
prize_number:%d, prize_uid:%d, prize_nickname:'%s', prize_avatar:'%s', prize_goods_num:%d,  \
prize_time:%d, add_time:%d}" % (
self.lottery_id, self.lt_id, self.section_number, self.goods_id, self.lottery_name, 
self.lottery_desc, self.lottery_img, self.lottery_price, self.lottery_status, self.finish_quantity, 
self.join_quantity, self.remain_quantity, self.max_quantity, self.schedule, self.announced_time, 
self.prize_number, self.prize_uid, self.prize_nickname, self.prize_avatar, self.prize_goods_num, 
self.prize_time, self.add_time)

    __repr__ = __str__


class LotteryNumber(Base):
    __tablename__ = 'lottery_number'

    ln_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    lottery_id = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    lottery_number = db.Column(db.Integer, default=0)
    is_prize = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "LotteryNumber => { \
ln_id:%d, uid:%d, lottery_id:%d, order_id:%d, lottery_number:%d,  \
is_prize:%d, add_time:%d}" % (
self.ln_id, self.uid, self.lottery_id, self.order_id, self.lottery_number, 
self.is_prize, self.add_time)

    __repr__ = __str__


class LotteryNumberPool(Base):
    __tablename__ = 'lottery_number_pool'

    lnp_id = db.Column(db.Integer, primary_key=True)
    lottery_id = db.Column(db.Integer, default=0)
    lottery_number = db.Column(db.Integer, default=0)

    def __str__(self):
        return "LotteryNumberPool => { \
lnp_id:%d, lottery_id:%d, lottery_number:%d}" % (
self.lnp_id, self.lottery_id, self.lottery_number)

    __repr__ = __str__


class LotteryCrontabTime(Base):
    __tablename__ = 'lottery_crontab_time'

    lct_id = db.Column(db.Integer, primary_key=True)
    exe_time = db.Column(db.Integer, default=0)

    def __str__(self):
        return "LotteryCrontabTime => { \
lct_id:%d, exe_time:%d}" % (
self.lct_id, self.exe_time)

    __repr__ = __str__


# 全局变量
current_time = int(time.time())


def toint(s, base=10):
    """
    字符串转换成整型，对于不能转换的返回0
    :param s: 需要转换的字符串
    :param base: 多少进制，默认是10进制。如果是16进制，可以写0x或者0X
    :return: int
    """
    try:
        ns = '%s' % s
        return string.atoi(ns, base)
    except ValueError:
        #忽略错误
        pass

    return 0


def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count


def model_to_dict(model):
    """ orm model转换成dict """

    ret = {}
    for c in model.__table__.columns:
        ret[c.name] = getattr(model, c.name)

    return ret


def save_exe_time():
    """ 记录定时脚本执行轨迹 """

    lct = LotteryCrontabTime()
    lct.exe_time = current_time
    session.add(lct)
    session.commit()

    return True


def get_prize(lottery_id):
    """ 获取中奖号码实例 """

    q     = session.query(LotteryNumber.ln_id).filter(LotteryNumber.lottery_id == lottery_id)
    count = get_count(q)
    rand  = random.randint(0, (count-1))

    lottery_number = session.query(LotteryNumber).filter(LotteryNumber.lottery_id == lottery_id).limit(1).offset(rand).first()

    return lottery_number


def create_lottery_number(lottery):
    """ 创建抽奖号码 """

    lottery_id      = lottery.lottery_id
    finish_quantity = toint(lottery.finish_quantity)

    if finish_quantity <= 0:
        print u'[CreateLotteryError] finish_quantity is error: %s' % finish_quantity
        return False

    try:
        lottery_number = 10000000
        for i in range(0, finish_quantity):
            lnp = LotteryNumberPool()
            lnp.lottery_id     = lottery_id
            lnp.lottery_number = lottery_number
            session.add(lnp)

            if (i%20) == 0:
                session.commit()

            lottery_number += 1

        if (i%20) != 0:
            session.commit()
    except Exception, e:
        print u'[CreateLotteryError] Exception Error: %s' % e
        return False

    return True


def create_lottery(template):
    """ 创建活动 """

    # 创建活动
    lottery = Lottery()
    lottery.lt_id           = template.lt_id
    lottery.section_number  = template.section_number
    lottery.goods_id        = template.goods_id
    lottery.lottery_name    = template.lottery_name
    lottery.lottery_desc    = template.lottery_desc
    lottery.lottery_img     = template.lottery_img
    lottery.lottery_price   = template.lottery_price
    lottery.lottery_status  = 0
    lottery.finish_quantity = template.finish_quantity
    lottery.remain_quantity = template.finish_quantity
    lottery.max_quantity    = template.max_quantity
    lottery.add_time        = current_time
    session.add(lottery)
    session.commit()

    # 创建抽奖号码
    ret = create_lottery_number(lottery)
    if not ret:
        return False

    # 发布活动
    lottery.lottery_status = 1
    session.commit()

    return True


def announced():
    """ 揭晓 """

    lottery_dict   = {}     # 模板的相关待揭晓活动列表
    lottery_list   = []     # 待揭晓活动列表
    lt_id_list     = []     # 模板ID列表

    # 获取待揭晓活动列表
    _lottery_list = session.query(Lottery).filter(Lottery.lottery_status == 2).all()
    
    # 模板的相关待揭晓活动列表
    for _lottery in _lottery_list:
        template_lottery_list = lottery_dict.get(_lottery.lt_id, [])
        template_lottery_list.append(_lottery)
        lottery_dict[_lottery.lt_id] = template_lottery_list

    # 风险检查 - 同一模板多个揭晓活动
    for (lt_id, _lottery_list) in lottery_dict.items():
        if len(_lottery_list) > 1:
            _lottery_id_list = []
            for _lottery in _lottery_list:
                _lottery_id_list.append(_lottery.lottery_id)

            print u'[RiskError] template s announced lottery more than 1: lt_id: %s _lottery_id_list: %s' % (lt_id, _lottery_id_list)
        else:
            lottery_list.append(_lottery_list[0])

    for lottery in lottery_list:
        __lottery = model_to_dict(lottery) if lottery else None
        print u'[LotteryInfo] lottery: %s' % __lottery

        # 风险检查 - 参与人次
        if (lottery.finish_quantity != lottery.join_quantity) or (lottery.remain_quantity != 0):
            print u'[RiskError] quantity error: %s' % __lottery
            continue

        # 风险检查 - 抽奖号码
        q     = session.query(LotteryNumber.ln_id).filter(LotteryNumber.lottery_id == lottery.lottery_id)
        count = get_count(q)
        if count != lottery.finish_quantity:
            print u'[PrizeError] lottery number is not eq finish_quantity: count: %s lottery: %s' % (count, __lottery)
            continue

        # 风险检查 - 抽奖号码池
        q     = session.query(LotteryNumberPool.lnp_id).filter(LotteryNumberPool.lottery_id == lottery.lottery_id)
        count = get_count(q)
        if count > 0:
            print u'[PrizeError] lottery number poor is not none: count: %s lottery: %s' % (count, __lottery)
            continue

        # 风险检查 - 获取中奖号码实例
        lottery_number   = get_prize(lottery.lottery_id)
        __lottery_number = model_to_dict(lottery_number) if lottery_number else None
        if not lottery_number:
            print u'[PrizeError] prize number is none: %s' % __lottery
            continue

        # 风险检查 - 中奖用户实例
        user = session.query(User).filter(User.uid == lottery_number.uid).first()
        if not user:
            print u'[PrizeError] prize user is none: %s' % __lottery_number
            continue

        # 风险检查 - 中奖订单实例
        order = session.query(Order).filter(Order.order_id == lottery_number.order_id).\
                            filter(Order.uid == lottery_number.uid).\
                            filter(Order.order_type == 3).first()
        if not order:
            print u'[PrizeError] prize order is none: %s' % __lottery_number
            continue

        print u'[PrizeLotteryNumberInfo] prize_lottery_number: %s' % __lottery_number

        # 中奖 - 更新中奖号码实例
        lottery_number.is_prize = 1

        # 中奖 - 更新活动实例
        lottery.lottery_status  = 3
        lottery.prize_number    = lottery_number.lottery_number
        lottery.prize_uid       = user.uid
        lottery.prize_nickname  = user.nickname
        lottery.prize_avatar    = user.avatar
        lottery.prize_goods_num = order.goods_num_list
        lottery.prize_time      = current_time

        session.commit()

        lt_id_list.append(lottery.lt_id)

    # 根据模板创建下期活动
    for lt_id in lt_id_list:
        # 获取模板实例
        template = session.query(LotteryTemplate).filter(LotteryTemplate.lt_id == lt_id).first()
        __template = model_to_dict(template) if template else None

        print u'[TemplateInfo] template: %s' % __template

        # 检查
        if not template:
            print u'[LotteryTemplateError] template is none: %s' % lt_id
            continue

        # 检查
        if template.status == 0:
            print u'[LotteryTemplateInfo] template is close: %s' % __template
            continue

        # 创建下期活动
        ret = create_lottery(template)
        if not ret:
            print u'[CreateLotteryError] create lottery error: %s' % __template
            continue

        # 更新模板实例
        template.section_number = template.section_number + 1
        session.commit()

    session.commit()


if __name__ == '__main__':
    """ 揭晓 """

    # 打印日志
    print u'Start: %s' % current_time

    # 记录定时脚本执行轨迹
    save_exe_time()

    # 揭晓
    announced()

    # 打印日志
    print u'All Done: %s' % current_time




