from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from faker import Faker
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MyTest:

    def send_sql_request(self, request):
        code_mirror = self.driver.find_element_by_class_name("CodeMirror")
        ac = webdriver.ActionChains(self.driver)
        ac.click(code_mirror).perform()
        ac.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.DELETE).perform()
        ac.send_keys(request).perform()
        self.driver.find_element_by_xpath('//button[text()="Run SQL »"]').click()
        self.driver.implicitly_wait(5)

    @staticmethod
    def data_generation():
        faker_data = Faker()
        list_data = [
            faker_data.name(),
            faker_data.name(),
            faker_data.street_address(),
            faker_data.city(),
            faker_data.postcode(),
            faker_data.country(),
        ]
        return list_data

    def get_rows(self):
        return self.driver.find_element_by_xpath('//table/tbody').find_elements_by_tag_name('tr')

    @staticmethod
    def compare_rows(list_data, rows):
        check_row = ' '.join(list_data)
        count = 0
        for i, text in enumerate(rows):
            text = rows[i].text
            if check_row in text:
                count += 1
        assert count == 1

    def show_all_rows_and_check_address(self):
        self.send_sql_request(request="SELECT * FROM Customers;")
        rows = self.get_rows()
        for i, row in enumerate(rows):
            values = row.find_elements_by_tag_name('td' if i else 'th')
            contact_name = values[2].text
            address = values[3].text
            if contact_name == 'Giovanni Rovelli':
                assert address == 'Via Ludovico il Moro 22'
                break

    def check_rows_london_city(self):
        self.send_sql_request(request="SELECT * FROM Customers WHERE city = 'London';")
        rows = self.get_rows()
        assert len(rows) - 1 == 6

    def insert_row_and_check(self):
        list_data = self.data_generation()
        self.send_sql_request(request='INSERT INTO Customers(CustomerName,ContactName,Address,City,PostalCode,Country) '
                                      'VALUES ({})'.format(','.join(("'" + elem + "'") for elem in list_data)))
        self.send_sql_request(request=f'SELECT * FROM Customers WHERE CustomerName = \'{list_data[0]}\' '
                                      f'ORDER BY CustomerID DESC')
        rows = self.get_rows()
        self.compare_rows(list_data, rows)

    def update_and_check_row(self):
        list_data = self.data_generation()
        self.send_sql_request(request=f'UPDATE Customers SET CustomerName = \'{list_data[0]}\','
                                      f'ContactName = \'{list_data[1]}\',Address =\'{list_data[2]}\','
                                      f'City =\'{list_data[3]}\',PostalCode =\'{list_data[4]}\','
                                      f'Country = \'{list_data[5]}\' WHERE CustomerID=1')

        self.send_sql_request(request='SELECT * FROM Customers WHERE CustomerID = 1')
        rows = self.get_rows()
        self.compare_rows(list_data, rows)

    def another_case(self):
        """
        Проверяется появление алерта при некорректном запросе. После этого проверяется, что результату исправленному
        корректному запросу соответствует одна запись
        """
        self.send_sql_request('select * from Customers as c '
                              'join Orders as o on o.CustomerID = c.CustomerID '
                              'where CustomerID = 90')
        WebDriverWait(self.driver, 3).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert.accept()
        self.send_sql_request('select * from Customers as c '
                              'join Orders as o on o.CustomerID = c.CustomerID '
                              'where c.CustomerID = 90')
        rows = self.get_rows()
        assert len(rows) - 1 == 1

    def __init__(self):
        self.driver = webdriver.Chrome('./chromedriver')
        self.driver.get("https://www.w3schools.com/sql/trysql.asp?filename=trysql_select_all")

    def __del__(self):
        self.driver.close()


if __name__ == '__main__':
    my_test = MyTest()
    my_test.show_all_rows_and_check_address()
    my_test.check_rows_london_city()
    my_test.insert_row_and_check()
    my_test.update_and_check_row()
    my_test.another_case()
    del my_test
