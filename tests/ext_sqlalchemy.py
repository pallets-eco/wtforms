#!/usr/bin/env python

from sqlalchemy import create_engine     
from sqlalchemy.schema import MetaData, Table, Column
from sqlalchemy.types import String, Integer
from sqlalchemy.orm import scoped_session, sessionmaker

from unittest import TestCase

from wtforms.ext.sqlalchemy.fields import ModelSelectField, QuerySelectField
from wtforms.form import Form


class LazySelect(object):
    def __call__(self, field, **kwargs):
        output = []
        for val, label, selected in field.iter_choices():
            s = selected and u'1' or u'0'
            output.append(u'%s,%s,%s' % (unicode(val), unicode(s), unicode(label)))
        return u'|'.join(output)

class DummyPostData(dict):
    def getlist(self, key):
        return self[key]

class Base(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class TestBase(TestCase):
    def _do_tables(self, mapper, engine):
        metadata = MetaData()

        test_table = Table('test', metadata, 
            Column('id', Integer, primary_key=True, nullable=False),
            Column('name', String, nullable=False),
        )

        pk_test_table = Table('pk_test', metadata, 
            Column('foobar', Integer, primary_key=True, nullable=False),
            Column('baz', String, nullable=False),
        )

        Test = type('Test', (Base, ), {})
        PKTest = type('PKTest', (Base, ), {'__unicode__': lambda x: x.baz })

        mapper(Test, test_table, order_by=[test_table.c.name])
        mapper(PKTest, pk_test_table, order_by=[pk_test_table.c.baz])
        self.Test = Test
        self.PKTest = PKTest

        metadata.create_all(bind=engine)

    def _fill(self, sess):
        for i, n in [(1, 'apple'),(2, 'banana')]:
            s = self.Test(id=i, name=n)
            p = self.PKTest(foobar=i, baz=n)
            sess.add(s)
            sess.add(p)
        sess.flush()
        sess.commit()
        

class QuerySelectFieldTest(TestBase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        self.Session = sessionmaker(bind=engine)
        from sqlalchemy.orm import mapper
        self._do_tables(mapper, engine)

    def test_without_factory(self):
        sess = self.Session()
        self._fill(sess)
        class F(Form):
            a = QuerySelectField(label_attr='name', widget=LazySelect())
        form = F(DummyPostData(a=['1']))
        form.a.query = sess.query(self.Test)
        self.assert_(form.a.data is not None)
        self.assertEqual(form.a.data.id, 1)
        self.assertEqual(form.a(), u'1,1,apple|2,0,banana')
        self.assert_(form.validate())

    def test_with_query_factory(self):
        sess = self.Session()
        self._fill(sess)

        class F(Form):
            a = QuerySelectField(label_attr='name', query_factory=lambda:sess.query(self.Test), widget=LazySelect())
            b = QuerySelectField(pk_attr='foobar', allow_blank=True, query_factory=lambda:sess.query(self.PKTest), widget=LazySelect())

        form = F()
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a(), u'1,0,apple|2,0,banana')
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.b(), u'__None,1,|1,0,apple|2,0,banana')
        self.assert_(not form.validate())

        form = F(DummyPostData(a=['1'], b=['2']))
        self.assertEqual(form.a.data.id, 1)
        self.assertEqual(form.a(), u'1,1,apple|2,0,banana')
        self.assertEqual(form.b.data.baz, 'banana')
        self.assertEqual(form.b(), u'__None,0,|1,0,apple|2,1,banana')
        self.assert_(form.validate())

        # Make sure the query is cached
        sess.add(self.Test(id=3, name='meh'))
        sess.flush()
        sess.commit()
        self.assertEqual(form.a(), u'1,1,apple|2,0,banana')
        form.a._object_list = None
        self.assertEqual(form.a(), u'1,1,apple|2,0,banana|3,0,meh')


class ModelSelectFieldTest(TestBase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        self.Session = scoped_session(sessionmaker(autoflush=False, autocommit=False, bind=engine))
        mapper = self.Session.mapper
        self._do_tables(mapper, engine)

    def test(self):
        sess = self.Session
        self._fill(sess)
        class F(Form):
            a = ModelSelectField(label_attr='name', model=self.Test, widget=LazySelect())

        form = F()
        self.assertEqual(form.a(), u'1,0,apple|2,0,banana')


if __name__ == '__main__':
    from unittest import main
    main()
