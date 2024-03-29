
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

from behave import given, when, then, step_matcher

% for scenario in scenarios :
##${scenario.name}##
##given##
  % for given_step in scenario.given_steps :
@given('${given_step.name_out}')
def step_impl(ctx, ${', '.join(given_step.params)}):
    pass

  % endfor

##when##
  % for when_step in scenario.when_steps :
@when('${when_step.name_out}')
def step_impl(ctx, ${', '.join(when_step.params)}):
    pass

  % endfor

##then##
  % for then_step in scenario.then_steps :   
@then('${then_step.name_out}')
def step_impl(ctx, ${', '.join(then_step.params)}):
    pass

  % endfor

% endfor
