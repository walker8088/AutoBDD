# -- FILE: features/environment.py
# USE: behave -D BEHAVE_DEBUG_ON_ERROR         (to enable  debug-on-error)
# USE: behave -D BEHAVE_DEBUG_ON_ERROR=yes     (to enable  debug-on-error)
# USE: behave -D BEHAVE_DEBUG_ON_ERROR=no      (to disable debug-on-error)


import behave_webdriver

# -- FILE: features/environment.py
# USE: behave -D BEHAVE_DEBUG_ON_ERROR         (to enable  debug-on-error)
# USE: behave -D BEHAVE_DEBUG_ON_ERROR=yes     (to enable  debug-on-error)
# USE: behave -D BEHAVE_DEBUG_ON_ERROR=no      (to disable debug-on-error)

import behave_webdriver

from page_base import *

class TestPage(PageBase):
    
    def is_404_page(self):
        return self.driver.title.lower().startswith('page not found')
        
    def has_error(self):
        errors = self.driver.find_elements_by_xpath('//p[@class="errornote"]')
        return len(errors) > 0    

    def is_login_page(self):
        logins = self.driver.find_elements_by_xpath("//body[@class=' login']")
        return len(logins) > 0    


BEHAVE_DEBUG_ON_ERROR = False
def setup_debug_on_error(userdata):
    global BEHAVE_DEBUG_ON_ERROR
    BEHAVE_DEBUG_ON_ERROR = userdata.getbool("BEHAVE_DEBUG_ON_ERROR")

def before_all(ctx):
    setup_debug_on_error(ctx.config.userdata)
    ctx.driver = behave_webdriver.Chrome()
    ctx.page = TestPage(ctx.driver)
    ctx.base_url = 'http://127.0.0.1:8000/admin/'

def after_step(ctx, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        # -- ENTER DEBUGGER: Zoom in on failure location.
        # NOTE: Use IPython debugger, same for pdb (basic python debugger).
        #import ipdb
        #ipdb.post_mortem(step.exc_traceback)    
        pass


def after_all(ctx):
    # cleanup after tests run
    ctx.driver.quit()