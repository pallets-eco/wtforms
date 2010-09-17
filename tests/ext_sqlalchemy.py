#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData, Table, Column
from sqlalchemy.types import String, Integer
from sqlalchemy.orm import scoped_session, sessionmaker

from unittest import TestCase

from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.form import Form


class LazySelect(object):
    def __call__(self, field, **kwargs):
        return list((val, unicode(label), selected) for val, label, selected in field.iter_choices())

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
            Column('foobar', String, primary_key=True, nullable=False),
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
            p = self.PKTest(foobar='hello%s' % (i, ), baz=n)
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
            a = QuerySelectField(get_label='name', widget=LazySelect(), get_pk=lambda x: x.id)
        form = F(DummyPostData(a=['1']))
        form.a.query = sess.query(self.Test)
        self.assert_(form.a.data is not None)
        self.assertEqual(form.a.data.id, 1)
        self.assertEqual(form.a(), [(u'1', 'apple', True), (u'2', 'banana', False)])
        self.assert_(form.validate())

    def test_with_query_factory(self):
        sess = self.Session()
        self._fill(sess)

        class F(Form):
            a = QuerySelectField(get_label=(lambda model: model.name), query_factory=lambda:sess.query(self.Test), widget=LazySelect())
            b = QuerySelectField(allow_blank=True, query_factory=lambda:sess.query(self.PKTest), widget=LazySelect())

        form = F()
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a(), [(u'1', 'apple', False), (u'2', 'banana', False)])
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.b(), [(u'__None', '', True), (u'hello1', 'apple', False), (u'hello2', 'banana', False)])
        self.assert_(not form.validate())

        form = F(DummyPostData(a=[u'1'], b=[u'hello2']))
        self.assertEqual(form.a.data.id, 1)
        self.assertEqual(form.a(), [(u'1', 'apple', True), (u'2', 'banana', False)])
        self.assertEqual(form.b.data.baz, 'banana')
        self.assertEqual(form.b(), [(u'__None', '', False), (u'hello1', 'apple', False), (u'hello2', 'banana', True)])
        self.assert_(form.validate())

        # Make sure the query iQuerySelectMultipleFields cached
        sess.add(self.Test(id=3, name='meh'))
        sess.flush()
        sess.commit()
        self.assertEqual(form.a(), [(u'1', 'apple', True), (u'2', 'banana', False)])
        form.a._object_list = None
        self.assertEqual(form.a(), [(u'1', 'apple', True), (u'2', 'banana', False), (u'3', 'meh', False)])


class QuerySelectMultipleFieldTest(TestBase):
    def setUp(self):
        from sqlalchemy.orm import mapper
        engine = create_engine('sqlite:///:memory:', echo=False)
        Session = sessionmaker(bind=engine)
        self._do_tables(mapper, engine)
        self.sess = Session()
        self._fill(self.sess)

    class F(Form):
        a = QuerySelectMultipleField(get_label='name', widget=LazySelect())

    def test_unpopulated_default(self):
        form = self.F()
        self.assertEqual([], form.a.data)

    def test_single_value_without_factory(self):
        form = self.F(DummyPostData(a=['1']))
        form.a.query = self.sess.query(self.Test)
        self.assertEqual([1], [v.id for v in form.a.data])
        self.assertEqual(form.a(), [(u'1', 'apple', True), (u'2', 'banana', False)])
        self.assert_(form.validate())

    def test_multiple_values_without_query_factory(self):
        form = self.F(DummyPostData(a=['1', '2']))
        form.a.query = self.sess.query(self.Test)
        self.assertEqual([1, 2], [v.id for v in form.a.data])
        self.assertEqual(form.a(), [(u'1', 'apple', True), (u'2', 'banana', True)])
        self.assert_(form.validate())

        form = self.F(DummyPostData(a=['1', '3']))
        form.a.query = self.sess.query(self.Test)
        self.assertEqual([x.id for x in form.a.data], [1])
        self.assert_(not form.validate())

    def test_single_default_value(self):
        first_test = self.sess.query(self.Test).get(2)
        class F(Form):
            a = QuerySelectMultipleField(get_label='name', default=[first_test],
                widget=LazySelect(), query_factory=lambda: self.sess.query(self.Test))
        form = F()
        self.assertEqual([v.id for v in form.a.data], [2])
        self.assertEqual(form.a(), [(u'1', 'apple', False), (u'2', 'banana', True)])
        self.assert_(form.validate())


if __name__ == '__main__':
    from unittest import main
    main()
