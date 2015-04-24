from django.core.exceptions import ValidationError
from django.test import TestCase

from bread.utils import get_model_field, validate_fieldspec, has_required_args
from tests.models import BreadTestModel2, BreadTestModel


class HasRequiredArgsTestCase(TestCase):
    def test_simple_no_args_function(self):
        def testfunc():
            pass
        self.assertFalse(has_required_args(testfunc))

    def test_simple_1_arg_function(self):
        def testfunc(foo):
            pass
        self.assertTrue(has_required_args(testfunc))

    def test_simple_1_arg_function_with_default(self):
        def testfunc(foo=2):
            pass
        self.assertFalse(has_required_args(testfunc))

    def test_simple_2_arg_function(self):
        def testfunc(foo, bar):
            pass
        self.assertTrue(has_required_args(testfunc))

    def test_simple_2_arg_function_with_one_default(self):
        def testfunc(foo, bar=3):
            pass
        self.assertTrue(has_required_args(testfunc))

    def test_simple_2_arg_function_with_two_defaults(self):
        def testfunc(foo=1, bar=3):
            pass
        self.assertFalse(has_required_args(testfunc))

    def test_class_function_no_args(self):
        class TestClass(object):
            def func(self):
                pass
        self.assertFalse(has_required_args(TestClass.func))

    def test_class_function_1_arg(self):
        class TestClass(object):
            def func(self, foo):
                pass
        self.assertTrue(has_required_args(TestClass.func))

    def test_class_function_1_arg_with_default(self):
        class TestClass(object):
            def func(self, foo=2):
                pass
        self.assertFalse(has_required_args(TestClass.func))

    def test_class_function_2_args(self):
        class TestClass(object):
            def func(self, foo, bar):
                pass
        self.assertTrue(has_required_args(TestClass.func))

    def test_class_function_2_args_1_default(self):
        class TestClass(object):
            def func(self, foo, bar=2):
                pass
        self.assertTrue(has_required_args(TestClass.func))

    def test_class_function_2_args_2_defaults(self):
        class TestClass(object):
            def func(self, foo=1, bar=2):
                pass
        self.assertFalse(has_required_args(TestClass.func))


class GetModelFieldTestCase(TestCase):
    def test_it(self):
        obj2 = BreadTestModel2.objects.create(
            text="Rinocerous"
        )
        obj1 = BreadTestModel.objects.create(
            name="Rudy Vallee", other=obj2
        )
        self.assertEqual(obj1.name, get_model_field(obj1, 'name'))
        self.assertEqual(obj1.name, get_model_field(obj1, 'get_name'))

        self.assertEqual(obj2.text, get_model_field(obj1, 'other__text'))
        self.assertEqual(obj2.text, get_model_field(obj1, 'other__get_text'))


class ValidateFieldspecTestCase(TestCase):
    def test_simple_field(self):
        validate_fieldspec(BreadTestModel, 'name')

    def test_method_name(self):
        validate_fieldspec(BreadTestModel, 'get_name')

    def test_method_with_optional_arg(self):
        validate_fieldspec(BreadTestModel, 'method2')

    def test_method_with_required_arg(self):
        with self.assertRaises(ValidationError):
            validate_fieldspec(BreadTestModel, 'method1')

    def test_no_such_attribute(self):
        with self.assertRaises(ValidationError):
            validate_fieldspec(BreadTestModel, 'petunias')

    def test_get_other(self):
        validate_fieldspec(BreadTestModel, 'other')

    def test_field_on_other(self):
        validate_fieldspec(BreadTestModel, 'other__text')

    def test_method_on_other(self):
        validate_fieldspec(BreadTestModel, 'other__get_text')

    def test_no_such_attribute_on_other(self):
        with self.assertRaises(ValidationError):
            validate_fieldspec(BreadTestModel, 'other__petunias')
