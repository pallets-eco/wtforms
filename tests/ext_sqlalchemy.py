from __future__ import unicode_literals

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.schema import MetaData, Table, Column, ColumnDefault
from sqlalchemy.types import String, Integer, Numeric, Date, Text, Enum, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from unittest import TestCase

from wtforms.compat import text_type, iteritems
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms import Form, fields
from wtforms.ext.sqlalchemy.orm import model_form, ModelConversionError, ModelConverter
from wtforms.validators import Optional, Required
from tests.common import DummyPostData, contains_validator


class LazySelect(object):
    def __call__(self, field, **kwargs):
        return list((val, text_type(label), selected) for val, label, selected in field.iter_choices())


class Base(object):
    def __init__(self, **kwargs):
        for k, v in iteritems(kwargs):
            setattr(self, k, v)


class AnotherInteger(Integer):
    """Use me to test if MRO works like we want"""


class TestBase(TestCase):
    def _do_tables(self, mapper, engine):
        metadata = MetaData()

        test_table = Table(
            'test', metadata,
            Column('id', Integer, primary_key=True, nullable=False),
            Column('name', String, nullable=False),
        )

        pk_test_table = Table(
            'pk_test', metadata,
            Column('foobar', String, primary_key=True, nullable=False),
            Column('baz', String, nullable=False),
        )

        Test = type(str('Test'), (Base, ), {})
        PKTest = type(str('PKTest'), (Base, ), {
            '__unicode__': lambda x: x.baz,
            '__str__': lambda x: x.baz,
        })

        mapper(Test, test_table, order_by=[test_table.c.name])
        mapper(PKTest, pk_test_table, order_by=[pk_test_table.c.baz])
        self.Test = Test
        self.PKTest = PKTest

        metadata.create_all(bind=engine)

    def _fill(self, sess):
        for i, n in [(1, 'apple'), (2, 'banana')]:
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
        self.assertTrue(form.a.data is not None)
        self.assertEqual(form.a.data.id, 1)
        self.assertEqual(form.a(), [('1', 'apple', True), ('2', 'banana', False)])
        self.assertTrue(form.validate())

        form = F(a=sess.query(self.Test).filter_by(name='banana').first())
        form.a.query = sess.query(self.Test).filter(self.Test.name != 'banana')
        assert not form.validate()
        self.assertEqual(form.a.errors, ['Not a valid choice'])

        form = F(a=sess.query(self.Test).filter_by(name='banana').first())
        another_sess = self.Session()
        form.a.query = another_sess.query(self.Test)
        #this is the problem. not same pointer.
        self.assertEqual(form.a(), [('1', 'apple', False), ('2', 'banana', False)])

        #So, use coerce and get_pk for test
        class F2(Form):
            a = QuerySelectField(get_label='name', widget=LazySelect(), get_pk=lambda x: x.id, coerce=int)
        form = F2(a=sess.query(self.Test).filter_by(name='banana').first())
        another_sess = self.Session()
        form.a.query = another_sess.query(self.Test)
        self.assertEqual(form.a(), [('1', 'apple', False), ('2', 'banana', True)])

    def test_with_query_factory(self):
        sess = self.Session()
        self._fill(sess)

        class F(Form):
            a = QuerySelectField(get_label=(lambda model: model.name), query_factory=lambda: sess.query(self.Test), widget=LazySelect())
            b = QuerySelectField(allow_blank=True, query_factory=lambda: sess.query(self.PKTest), widget=LazySelect())

        form = F()
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a(), [('1', 'apple', False), ('2', 'banana', False)])
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.b(), [('__None', '', True), ('hello1', 'apple', False), ('hello2', 'banana', False)])
        self.assertFalse(form.validate())

        form = F(DummyPostData(a=['1'], b=['hello2']))
        self.assertEqual(form.a.data.id, 1)
        self.assertEqual(form.a(), [('1', 'apple', True), ('2', 'banana', False)])
        self.assertEqual(form.b.data.baz, 'banana')
        self.assertEqual(form.b(), [('__None', '', False), ('hello1', 'apple', False), ('hello2', 'banana', True)])
        self.assertTrue(form.validate())

        # Make sure the query is cached
        sess.add(self.Test(id=3, name='meh'))
        sess.flush()
        sess.commit()
        self.assertEqual(form.a(), [('1', 'apple', True), ('2', 'banana', False)])
        form.a._object_list = None
        self.assertEqual(form.a(), [('1', 'apple', True), ('2', 'banana', False), ('3', 'meh', False)])

        # Test bad data
        form = F(DummyPostData(b=['__None'], a=['fail']))
        assert not form.validate()
        self.assertEqual(form.a.errors, ['Not a valid choice'])
        self.assertEqual(form.b.errors, [])
        self.assertEqual(form.b.data, None)


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
        self.assertEqual(form.a(), [('1', 'apple', True), ('2', 'banana', False)])
        self.assertTrue(form.validate())

    def test_multiple_values_without_query_factory(self):
        form = self.F(DummyPostData(a=['1', '2']))
        form.a.query = self.sess.query(self.Test)
        self.assertEqual([1, 2], [v.id for v in form.a.data])
        self.assertEqual(form.a(), [('1', 'apple', True), ('2', 'banana', True)])
        self.assertTrue(form.validate())

        form = self.F(DummyPostData(a=['1', '3']))
        form.a.query = self.sess.query(self.Test)
        self.assertEqual([x.id for x in form.a.data], [1])
        self.assertFalse(form.validate())

    def test_single_default_value(self):
        first_test = self.sess.query(self.Test).get(2)

        class F(Form):
            a = QuerySelectMultipleField(
                get_label='name', default=[first_test],
                widget=LazySelect(), query_factory=lambda: self.sess.query(self.Test)
            )
        form = F()
        self.assertEqual([v.id for v in form.a.data], [2])
        self.assertEqual(form.a(), [('1', 'apple', False), ('2', 'banana', True)])
        self.assertTrue(form.validate())


class ModelFormTest(TestCase):
    def setUp(self):
        Model = declarative_base()

        student_course = Table(
            'student_course', Model.metadata,
            Column('student_id', Integer, ForeignKey('student.id')),
            Column('course_id', Integer, ForeignKey('course.id'))
        )

        class Course(Model):
            __tablename__ = "course"
            id = Column(Integer, primary_key=True)
            name = Column(String(255), nullable=False)
            # These are for better model form testing
            cost = Column(Numeric(5, 2), nullable=False)
            description = Column(Text, nullable=False)
            level = Column(Enum('Primary', 'Secondary'))
            has_prereqs = Column(Boolean, nullable=False)
            started = Column(DateTime, nullable=False)
            grade = Column(AnotherInteger, nullable=False)

        class School(Model):
            __tablename__ = "school"
            id = Column(Integer, primary_key=True)
            name = Column(String(255), nullable=False)

        class Student(Model):
            __tablename__ = "student"
            id = Column(Integer, primary_key=True)
            full_name = Column(String(255), nullable=False, unique=True)
            dob = Column(Date(), nullable=True)
            current_school_id = Column(Integer, ForeignKey(School.id), nullable=False)

            current_school = relationship(School, backref=backref('students'))
            courses = relationship(
                "Course",
                secondary=student_course,
                backref=backref("students", lazy='dynamic')
            )

        self.School = School
        self.Student = Student
        self.Course = Course

        engine = create_engine('sqlite:///:memory:', echo=False)
        Session = sessionmaker(bind=engine)
        self.metadata = Model.metadata
        self.metadata.create_all(bind=engine)
        self.sess = Session()

    def test_auto_validators(self):
        student_form = model_form(self.Student, self.sess)()
        assert contains_validator(student_form.dob, Optional)
        assert contains_validator(student_form.full_name, Required)

    def test_include_pk(self):
        form_class = model_form(self.Student, self.sess, exclude_pk=False)
        student_form = form_class()
        assert ('id' in student_form._fields)

    def test_exclude_pk(self):
        form_class = model_form(self.Student, self.sess, exclude_pk=True)
        student_form = form_class()
        assert ('id' not in student_form._fields)

    def test_exclude_fk(self):
        student_form = model_form(self.Student, self.sess)()
        assert ('current_school_id' not in student_form._fields)

    def test_include_fk(self):
        student_form = model_form(self.Student, self.sess, exclude_fk=False)()
        assert ('current_school_id' in student_form._fields)

    def test_convert_many_to_one(self):
        student_form = model_form(self.Student, self.sess)()
        assert isinstance(student_form.current_school, QuerySelectField)

    def test_convert_one_to_many(self):
        school_form = model_form(self.School, self.sess)()
        assert isinstance(school_form.students, QuerySelectMultipleField)

    def test_convert_many_to_many(self):
        student_form = model_form(self.Student, self.sess)()
        assert isinstance(student_form.courses, QuerySelectMultipleField)

    def test_convert_basic(self):
        self.assertRaises(TypeError, model_form, None)
        self.assertRaises(ModelConversionError, model_form, self.Course)
        form_class = model_form(self.Course, exclude=['students'])
        form = form_class()
        self.assertEqual(len(list(form)), 7)
        assert isinstance(form.cost, fields.DecimalField)
        assert isinstance(form.has_prereqs, fields.BooleanField)
        assert isinstance(form.started, fields.DateTimeField)

    def test_only(self):
        desired_fields = ['id', 'cost', 'description']
        form = model_form(self.Course, only=desired_fields)()
        self.assertEqual(len(list(form)), 2)
        form = model_form(self.Course, only=desired_fields, exclude_pk=False)()
        self.assertEqual(len(list(form)), 3)

    def test_no_mro(self):
        converter = ModelConverter(use_mro=False)
        # Without MRO, will not be able to convert 'grade'
        self.assertRaises(ModelConversionError, model_form, self.Course, self.sess, converter=converter)
        # If we exclude 'grade' everything should continue working
        F = model_form(self.Course, self.sess, exclude=['grade'], converter=converter)
        self.assertEqual(len(list(F())), 7)


class ModelFormColumnDefaultTest(TestCase):
    def setUp(self):
        Model = declarative_base()

        def default_score():
            return 5

        class StudentDefaultScoreCallable(Model):
            __tablename__ = "course"
            id = Column(Integer, primary_key=True)
            name = Column(String(255), nullable=False)
            score = Column(Integer, default=default_score, nullable=False)

        class StudentDefaultScoreScalar(Model):
            __tablename__ = "school"
            id = Column(Integer, primary_key=True)
            name = Column(String(255), nullable=False)
            # Default scalar value
            score = Column(Integer, default=10, nullable=False)

        self.StudentDefaultScoreCallable = StudentDefaultScoreCallable
        self.StudentDefaultScoreScalar = StudentDefaultScoreScalar

        engine = create_engine('sqlite:///:memory:', echo=False)
        Session = sessionmaker(bind=engine)
        self.metadata = Model.metadata
        self.metadata.create_all(bind=engine)
        self.sess = Session()

    def test_column_default_callable(self):
        student_form = model_form(self.StudentDefaultScoreCallable, self.sess)()
        self.assertEqual(student_form._fields['score'].default, 5)

    def test_column_default_scalar(self):
        student_form = model_form(self.StudentDefaultScoreScalar, self.sess)()
        assert not isinstance(student_form._fields['score'].default, ColumnDefault)
        self.assertEqual(student_form._fields['score'].default, 10)
