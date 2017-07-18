from six import text_type
from sqlalchemy import Column, func, exc
from sqlalchemy.sql.ddl import CreateTable

from src import types, engines, get_declarative_base, Table
from tests.testcase import BaseTestCase


class EnginesDeclarativeTestCase(BaseTestCase):
    def test_text_engine_columns_declarative(self):
        base = get_declarative_base()

        class TestTable(base):
            date = Column(types.Date, primary_key=True)
            x = Column(types.Int32)
            y = Column(types.String)

            __table_args__ = (
                engines.MergeTree('date', ('date', 'x')),
            )

        self.assertEqual(
            self.compile(CreateTable(TestTable.__table__)),
            'CREATE TABLE test_table (date Date, x Int32, y String) '
            'ENGINE = MergeTree(date, (date, x), 8192)'
        )

    def test_text_engine_columns(self):
        table = Table(
            't1', self.metadata(),
            Column('date', types.Date, primary_key=True),
            Column('x', types.Int32),
            Column('y', types.String),
            engines.MergeTree('date', ('date', 'x')),
        )

        self.assertEqual(
            self.compile(CreateTable(table)),
            'CREATE TABLE t1 (date Date, x Int32, y String) '
            'ENGINE = MergeTree(date, (date, x), 8192)'
        )

    def test_func_engine_columns(self):
        base = get_declarative_base()

        class TestTable(base):
            date = Column(types.Date, primary_key=True)
            x = Column(types.Int32)
            y = Column(types.String)

            __table_args__ = (
                engines.MergeTree('date', ('date', func.intHash32(x)),
                                  sampling=func.intHash32(x)),
            )

        self.assertEqual(
            self.compile(CreateTable(TestTable.__table__)),
            'CREATE TABLE test_table (date Date, x Int32, y String) '
            'ENGINE = MergeTree('
            'date, intHash32(x), (date, intHash32(x)), 8192'
            ')'
        )

    def test_index_granularity(self):
        base = get_declarative_base()

        class TestTable(base):
            date = Column(types.Date, primary_key=True)
            x = Column(types.Int32)
            y = Column(types.String)

            __table_args__ = (
                engines.MergeTree(date, (date, x), index_granularity=4096),
            )

        self.assertEqual(
            self.compile(CreateTable(TestTable.__table__)),
            'CREATE TABLE test_table (date Date, x Int32, y String) '
            'ENGINE = MergeTree(date, (date, x), 4096)'
        )

    def test_create_table_without_engine(self):
        no_engine_table = Table(
            't1', self.metadata(),
            Column('x', types.Int32, primary_key=True),
            Column('y', types.String)
        )

        with self.assertRaises(exc.CompileError) as ex:
            self.compile(CreateTable(no_engine_table))

        self.assertEqual(text_type(ex.exception), "No engine for table 't1'")