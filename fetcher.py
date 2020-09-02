from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from sqlite_utils import Database
import sqlite3
import time
import requests
import sys
import re


class GradesFetcher:
    DB_TABLE = 'grades'
    BASE_URL = 'https://sheilta.apps.openu.ac.il'
    GRADES_PATH = '/pls/dmyopt2/course_info.courses?p_from=1'
    TELEGRAM_URL =  'https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}'

    def __init__(self, db_file, username, password, id_number, token, chat_id):
        self.__db = Database(sqlite3.connect(db_file))
        self.__grades = self.__db[GradesFetcher.DB_TABLE]
        self.__username = username
        self.__password = password
        self.__id_number = id_number
        self.__token = token
        self.__chat_id = chat_id

        chrome_options = Options()
        chrome_options.headless = True
        self.__driver = webdriver.Chrome(options=chrome_options)

    def __del__(self):
        self.__driver.close()

    def send_telegram_update(self, message):
        send_message = GradesFetcher.TELEGRAM_URL.format(
            self.__token, self.__chat_id, message
        )
        requests.get(send_message)

    def is_logged_in(self):
        return 'כניסה אישית' not in self.__driver.switch_to.active_element.text

    def login(self):
        username_elem = self.__driver.find_element_by_id("p_user")
        password_elem = self.__driver.find_element_by_id("p_sisma")
        id_number_elem = self.__driver.find_element_by_id("p_mis_student")
        submit_btn = self.__driver.find_element_by_css_selector("fieldset>input")

        username_elem.send_keys(self.__username)
        password_elem.send_keys(self.__password)
        id_number_elem.send_keys(self.__id_number)
        submit_btn.click()

    def fetch(self, courses=None):
        courses = [] if not courses or '*' in courses else courses
        pattern = r'"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"'
        start_time = time.time()
        self.__driver.get(''.join([GradesFetcher.BASE_URL, GradesFetcher.GRADES_PATH]))

        if not self.is_logged_in():
            self.login()

        self.__driver.get(''.join([GradesFetcher.BASE_URL, GradesFetcher.GRADES_PATH]))
        
        if not self.is_logged_in():
            raise RuntimeError('Failed to login')
            
        table = self.__driver.find_element_by_css_selector('.content_tbl>tbody')
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]
        grades_per_course_urls = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            a = cols[1].find_elements(By.TAG_NAME, "a")
            if len(a) > 0:
                grades_url = a[0].get_attribute("onclick")
                m = re.search(pattern, grades_url)
                url = m.group().strip('"')
                course_found = False

                for course in courses:
                    if course in url:
                        course_found = True
                        break

                if len(courses) == 0 or course_found:
                    grades_per_course_urls.append(url)

        for url in grades_per_course_urls:
            self.__driver.get(''.join([GradesFetcher.BASE_URL, url]))
            table = self.__driver.find_element_by_xpath('/html/body/table/tbody')
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) > 3:
                course_info = rows[0].find_element(By.TAG_NAME, "span").text
                course_info = course_info.split(':')[2].strip().split(' ')
                course_id = int(course_info[0])
                course_name = ' '.join(course_info[1:])
                rows = rows[7:]
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    try:
                        grade = int(cols[5].text)
                        mmn_type = cols[6].text.split('\n')
                        mmn_type = ' '.join(mmn_type[:1] if len(mmn_type) > 1 else mmn_type)
                        number = cols[7].text
                        self.__grades.insert(
                            {'course_id': course_id, 'course_name': course_name,
                             'number': number, 'type': mmn_type, 'grade': grade, 'updated': time.time()},
                            pk=('course_id', 'course_name', 'number'), ignore=True)
                    except ValueError:
                        pass

        new_grades = list(self.__grades.rows_where('updated > ?', [start_time], order_by='course_id desc'))
        if len(new_grades):
            latest_course_id = None
            msg = []
            for grade in new_grades:
                if latest_course_id is None:
                    latest_course_id = grade['course_id']
                    msg = ['ציונים חדשים בקורס {} ({})'.format(grade['course_name'], grade['course_id'])]
                elif grade['course_id'] != latest_course_id:
                    latest_course_id = grade['course_id']
                    self.send_telegram_update(message='\n'.join(msg))
                    msg = ['ציונים חדשים בקורס {} ({})'.format(grade['course_name'], grade['course_id'])]

                msg.append('{} {}: {}'.format(grade['type'], grade['number'], grade['grade']))
            self.send_telegram_update(message='\n'.join(msg))


if __name__ == '__main__':
    import yaml

    with open('config.yaml', 'r', encoding='utf8') as f:
        try:
            conf = yaml.safe_load(f)
            gf = GradesFetcher(db_file=sys.argv[1], username=sys.argv[2], password=sys.argv[3], id_number=sys.argv[4],
                               token=sys.argv[5], chat_id=sys.argv[6])
            gf.fetch(courses=conf['courses'])
        except yaml.YAMLError as exc:
            print(exc)
