#!/usr/bin/env python
#coding=utf-8

from codingabc.database import db


class MyModelService(object):
    """ MyModelService """
    def __init__(self):
        super(MyModelService, self).__init__()
        self.__attrilist={}
        self.__attributes=[]

    @classmethod
    def create(cls, commit=False, **kwargs):
        instance = cls(**kwargs)
        return instance.save(commit=commit)

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_or_404(cls, id):
        return cls.query.get_or_404(id)

    def update(self, commit=False, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save(commit=commit) or self

    def save(self, commit=False):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=False):
        db.session.delete(self)
        return commit and db.session.commit()

    def updateAttributes(self,attributes):
        self.__attributes=attributes
    def updatePairs(self,values):
        for i in range(len(values)):
            self.__attrilist[self.__attributes[i]]=values[i]
