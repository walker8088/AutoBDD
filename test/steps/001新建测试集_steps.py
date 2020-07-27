
import os

from behave import given, when, then, step_matcher

@when('新建测试集')
def step_impl(context):
    pass

@then('显示新建测试集')
def step_impl(context):
    assert True

@given("程序启动")
def step_impl(context):
    pass
