
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select


#---------------------------------------------------------------------------------#
class Element(object):
    def __init__(self, parent, selector, wait = EC.presence_of_element_located, wait_timeout=10):
        self.parent = parent
        self.selector = selector
        self.wait = wait
        self.wait_timeout = wait_timeout
        
    @property
    def element(self):
        if self.wait is not None:
            return \
                WebDriverWait(self.parent.driver, self.wait_timeout).until(
                    EC.presence_of_element_located(self.selector)
                )
        return self.parent.driver.find_element(*self.selector)
    
    def click(self):
        self.element.click()
        
#---------------------------------------------------------------------------------#
class InputField(Element):
    
    def get(self):
        return self.element.get_value()
    
    def set(self, value):
        self.element.clear()
        self.element.send_keys(value)

   
#---------------------------------------------------------------------------------#
class CheckBox(Element):
    
    def get(self):
        return self.element.is_selected()

    def set(self, value):
        if (value is True and not self.element.is_selected()) or \
           (value is False and self.element.is_selected()):
               self.element.click()


#---------------------------------------------------------------------------------#
class SelectBox(Element):
    
    def get(self):
        return self.all_selected_options

    def set(self, value):
        self.select_by_visible_text(value)               
        
    def select_all(self):
        for index in range(len(self.options)):
            self.select_by_index(index)
            
    def deselect_all(self):
        self.select.deselect_all()    
    
    def deselect_by_index(self, index):
        self.select.deselect_by_index(index)
    
    def deselect_by_value(self, value):
        self.select.deselect_by_value(value)
        
    def deselect_by_visible_text(self, text):
        self.select.deselect_by_visible_text(text)
        
    def select_by_index(self, index):
        self.select.select_by_index(index)
    
    def select_by_value(self, value):
        self.select.select_by_value(value)
    
    def select_by_visible_text(self, text):
        self.select.select_by_visible_text(text)
    
    def select_multi_texts(self, texts):
        for text in texts:
            self.select_by_visible_text(text)
            
    @property
    def all_selected_options(self):
        return self.select.all_selected_options
        
    @property
    def first_selected_option(self):
        return self.select.first_selected_option
    
    @property
    def options(self):
        return self.select.options
    
    @property
    def select(self):
        return Select(self.element)
    

#---------------------------------------------------------------------------------#
class Table:
    def __init__(self, webtable):
       self.table = webtable

    def rows(self):
      return len(self.table.find_elements_by_tag_name("tr"))-1

    def cols(self):
        return len(self.table.find_elements_by_xpath("//tr[1]/td"))
    
    def size(self):
        return {"rows": self.rows(),
                "cols": self.cols()}
    
    def row_text(self, row):
        rows = self.table.find_elements_by_xpath(f"//tr[{row+1}]/td")
        rets = []
        for it in rows :
            rets.append(it.text)

        return rets
    
    def col_text(self, col):
        cols = self.table.find_elements_by_xpath(f"//tr/td[{col+1}]")
        rets = []
        for it in cols :
            rets.append(it.text)
        return rets
    
    def sub_texts(self, xpath_selector):
        cols = self.table.find_elements_by_xpath(xpath_selector)
        return [it.text for it in cols]
        
    def get_all_text(self):
        
        allData = []
        # iterate over the rows, to ignore the headers we have started the i with '1'
        for i in range(self.rows()):
            # reset the row data every time
            ro = []
            # iterate over columns
            for j in range(self.cols()) :
                # get text from the i th row and j th column
                ro.append(get_item_text(self.table.find_element_by_xpath(f"//tr[{i+1}]/td{j+1}]")))

            # add the row data to allData of the self.table
            allData.append(ro)

        return allData

    def presence_of_text(self, data):
        data_len = len(self.table.find_elements_by_xpath(f"//td[normalize-space(text())='{data}']"))
        return True if (data_len > 0) else False
        
    def get_cell_text(self, row, col):
        cell = table.find_element_by_xpath(f"//tr[{row+1}]/td[{col+1}]").text
        return cell
        
#---------------------------------------------------------------------------------#
    
class PageBase():
    def __init__(self, driver):
        self.driver = driver
    
    def open(self, url):
        self.driver.get(url)
           
    def input(self, by, selector):
        return InputField(self, (by, selector))
    
    def button(self, by, selector):
        return Element(self, (by, selector))
    
    def button_text(self, text):
        
        btn = self.get_tag_of_text('button', text)   
        if btn :
            return btn
            
        submits = self.tags_type('input', 'submit')
        for btn in submits:
            if btn.text == text:
                return btn
            if text == btn.get_property('value'):
                return btn    
            
        return None
    
    def tag_id(self, tag_name, id):
        selector = (By.XPATH, f"//{tag_name}[@id='{id}']")        
        return self.wait_element(selector)
    
    def tag_value(self, tag_name, value):
        selector = (By.XPATH, f"//{tag_name}[@value='{value}']")        
        return self.wait_element(selector)
        
    def tag_name(self, tag_name, name):
        selector = (By.XPATH, f"//{tag_name}[@name='{name}']")        
        return self.wait_element(selector)
    
    def tags_name(self, tag_name, name):
        selector = (By.XPATH, f'//{tag_name}[@name="{name}"]')
        return self.driver.find_elements(*selector)
    
    def tag_type(self, tag_name, tag_type):
        selector = (By.XPATH, f"//{tag_name}[@type='{tag_type}']")        
        return self.wait_element(selector)
    
    def tags_type(self, tag_name, tag_type):
        selector = (By.XPATH, f"//{tag_name}[@type='{tag_type}']")        
        return self.driver.find_elements(*selector)
        
    def tag_class(self, tag_name, class_name):
        selector = (By.XPATH, f"//{tag_name}[@class='{class_name}']")        
        return self.wait_element(selector)
    
    def tags_class(self, tag_name, class_name):
        selector = (By.XPATH, f"//{tag_name}[@class='{class_name}']")        
        return self.driver.find_elements(*selector)
    
    def get_tag_of_text(self, tag_name, text):
        #TODO add wait
        tags = self.driver.find_elements_by_tag_name(tag_name)
        for it in tags:
            if it.text == text:
                return it
        return None
        
    def wait_element(self, selector, wait = 5):
        return WebDriverWait(self.driver, wait).until(EC.presence_of_element_located(selector))
        #return self.driver.find_element(*selector)
    
    def tags(self, tag_name):
        return self.driver.find_elements_by_tag_name(tag_name)
    
    def elements_text(self, xpath_selector): 
        elements = self.driver.find_elements_by_xpath(xpath_selector)
        return [it.text for it in elements]
        
    def tags_text(self, tag_name):
        tags = self.tags(tag_name)
        return [it.text for it in tags]
        
    def checkboxs(self):
        return self.tags_type('input', 'checkbox')
        
    def select_box(self, by, selector):
        return SelectBox(self, (by, selector))
        
    def link_text(self, text):
        links = self.driver.find_elements_by_link_text(text)
        if len(links) == 1:
            return links[0]
        
        if len(links) == 0:
            links = self.driver.find_elements_by_partial_link_text(text)
            if len(links) == 1:
                return links[0]
                
        return None
    
    def links_text(self, text):
        return self.driver.find_elements_by_link_text(text)
        
    def links(self):
        links = []
        elements = self.driver.find_elements_by_tag_name('a')
        for elem in elements:
            href = elem.get_attribute("href")
            if href is None:
                continue
            links.append(href)
        return links
        
    def tables(self):
        elements = self.driver.find_elements(By.XPATH, "//table")
        tables = [Table(t) for t in elements]
        return tables
        
    def table_from_element(self, element):    
        return Table(element)    
        