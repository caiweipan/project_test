#!/usr/bin/env python
#coding=utf-8

from codingabc import create_app
from codingabc.database import db
from codingabc.helpers import format_timestamp, toint

from app import DEFAULT_MODULES, DEFAULT_APP_NAME, configure_before_handlers, configure_errorhandlers
from app.helpers.sys import get_nav_classname
from app.helpers.date_time import get_social_time
from app.helpers.common import object_name, getip, img_list, child_menu_list

app = create_app("config.cfg", DEFAULT_MODULES, DEFAULT_APP_NAME)
db.init_app(app)
configure_before_handlers(app)
configure_errorhandlers(app)

filter_dict = {'getattr':getattr,
                'get_nav_classname':get_nav_classname,
                'toint':toint,
                'format_timestamp':format_timestamp,
                'get_social_time':get_social_time,
                'object_name':object_name,
                'child_menu_list':child_menu_list,
                'img_list':img_list}

app.jinja_env.filters.update(filter_dict)


if __name__ == '__main__':
    app.config.from_pyfile('config.dev.cfg')
    app.run(host='0.0.0.0', debug=True, port=5008)





