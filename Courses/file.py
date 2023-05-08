from bs4 import BeautifulSoup
from httpx import Client, AsyncClient
from urllib3 import disable_warnings
from re import findall, sub
from time import time
from json import dumps, loads
from typing import Optional
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
import asyncio
import logging

logging.basicConfig(
    filename = 'Logs.log',
    encoding = 'UTF-8',
    format = '=' * 150 + '\n%(name)s: %(asctime)s | %(levelname)s | Line: %(lineno)s |  %(message)s\n' + '=' * 150 + '\n',
    datefmt = '%Y-%m-%dT%H:%M:%SZ',
)
disable_warnings()

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)
CORS(app)

# https://drew.edu/registrars-office/about-us/facultystaff/course-attribute-overview/
with open('mappings.json', 'r', encoding = 'UTF-8') as f: SUBJECT_MAPPING = loads(f.read())
ALL = {
    'Subjects': [],
    'Abbreviations': [],
    'Types': [],
    'Times': [],
    'Days': [],
    'Locations': [],
    'Natures': [],
    'Periods': [],
    'Instructors': [],
    'Attributes': []
}

class Schedules():
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        self.username = username
        self.password = password
        self.valid = False
        self.number_and_stuff_uri = []
        self.desc_uris = []
    
    def _authenticate(self) -> None:
        logger = logging.getLogger('_authenticate')
        with Client(follow_redirects=True, verify=False, timeout=30) as session:
            try:
                first_headers = {
                    'Upgrade-Insecure-Requests': '1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate'
                    }
                first_response = session.get('http://treehouse.drew.edu/', headers=first_headers)
                if '<title>uLogin</title>' in first_response.text:
                    
                    try:
                        second_headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'https://idp.drew.edu',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                        'Referer': 'https://idp.drew.edu/nidp/idff/sso?id=DuoProxyADFS&sid=0&option=credential&sid=0',
                        'Accept-Language': 'en-US,en;q=0.9'
                        }
                        second_data = {'option': 'credential', 'Ecom_User_ID': self.username, 'Ecom_Password': self.password, 'duoOptions': 'Defaults', 'passcode': '', 'Ecom_Token': self.password}
                        second_response = session.post('https://idp.drew.edu/nidp/idff/sso?sid=0', headers=second_headers, data=second_data)
                        if 'top.location.href=\'sso?sid=0\';' in second_response.text:
                            
                            try:
                                third_headers = {
                                    'Upgrade-Insecure-Requests': '1',
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                                    'Accept-Language': 'en-US,en;q=0.9',
                                    'Referer': 'https://idp.drew.edu/nidp/idff/sso?sid=0',
                                    'Accept-Encoding': 'gzip, deflate'
                                    }
                                third_response = session.post('https://idp.drew.edu/nidp/idff/sso?sid=0', headers=third_headers)
                                if 'method="post" action="/cas-web/login;' in third_response.text:
                                    names = findall(r'(?<=name\=")(.*?)(?=")', third_response.text)
                                    values = findall(r'(?<=value\=")(.*?)(?=")', third_response.text)
                                    uri = findall(r'(?<=post" action\=")(.*?)(?=")', third_response.text)[0]
                                    
                                    try:
                                        fourth_headers = {
                                            'Content-Type': 'application/x-www-form-urlencoded',
                                            'Origin': 'https://cas.drew.edu',
                                            'Accept-Encoding': 'gzip, deflate, br',
                                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                                            'Referer': 'https://cas.drew.edu/cas-web/login?service=https%3A%2F%2Ftreehouse.drew.edu%2Fc%2Fportal%2Flogin',
                                            'Accept-Language': 'en-US,en;q=0.9'
                                            }
                                        fourth_data = {name: value for (name, value) in zip(names, values)}
                                        fourth_response = session.post('https://cas.drew.edu' + uri, headers=fourth_headers, data=fourth_data)
                                        if '>Sign Out<' in fourth_response.text:
                                            self.valid = True
                                    except Exception as e: logger.exception(f'4th Request | {type(e)} | {e}')
                            except Exception as e: logger.exception(f'3rd Request | {type(e)} | {e}')
                    except Exception as e: logger.exception(f'2nd Request| {type(e)} | {e}')
            except Exception as e: logger.exception(f'1st Request | {type(e)} | {e}')
    
    def _reset_uris(self) -> None:
        self.number_and_stuff_uri = []
        self.desc_uris = []    
    
    def _format_subject(self, abbreviation: str) -> dict:
        abbreviation = SUBJECT_MAPPING[abbreviation]
        
        try: subject_dict = next(item for item in ALL['Subjects'] if item["Name"] == abbreviation)
        except Exception as e:
            subject_dict = {'ID': len(ALL['Subjects']) + 1, 'Name': abbreviation}
            ALL['Subjects'].append(subject_dict)
        
        return subject_dict
    
    def _format_abbreviation(self, abbreviation: str) -> dict:
        try: abbreviation_dict = next(item for item in ALL['Abbreviations'] if item["Name"] == abbreviation)
        except Exception as e:
            abbreviation_dict = {'ID': len(ALL['Abbreviations']) + 1, 'Name': abbreviation}
            ALL['Abbreviations'].append(abbreviation_dict)
        
        return abbreviation_dict
    
    def _format_type(self, class_type: str) -> dict:
        try: class_type_dict = next(item for item in ALL['Types'] if item["Name"] == class_type)
        except Exception as e:
            class_type_dict = {'ID': len(ALL['Types']) + 1, 'Name': class_type}
            ALL['Types'].append(class_type_dict)
            
        return class_type_dict
        
    def _format_time(self, t: str) -> dict:
        try: t = t.upper().replace(' - ', ' - ')
        except Exception as e: t = 'TBA'

        try: time_dict = next(item for item in ALL['Times'] if item["Name"] == t)
        except Exception as e:
            time_dict = {'ID': len(ALL['Times']) + 1, 'Name': t}
            ALL['Times'].append(time_dict)

        return time_dict

    def _format_days(self, days: str) -> list[dict]:
        final_days = []
        
        if len(days.strip()) < 1: days = 'TBA' # Cases when no days are defined, which is weird?
        
        if not all([True if day in ['M', 'T', 'W', 'R', 'F', 'S'] else False for day in days]): # If TBA or something else
            try: day_dict = next(item for item in ALL['Days'] if item["Name"] == days) #Get Dict by looking up with Name Key
            except Exception as e:
                day_dict = {'ID': len(ALL['Days']) + 1, 'Name': days}
                ALL['Days'].append(day_dict)            
            return [day_dict]
        
        for day in days:
            if day == 'M': day = 'Monday'
            elif day == 'T': day = 'Tuesday'
            elif day == 'W': day = 'Wednesday'
            elif day == 'R': day = 'Thursday'
            elif day == 'F': day = 'Friday'
            elif day == 'S': day = 'Saturday'
            
            try: day_dict = next(item for item in ALL['Days'] if item["Name"] == day) #Get Dict by looking up with Name Key
            except Exception as e:
                day_dict = {'ID': len(ALL['Days']) + 1, 'Name': day}
                ALL['Days'].append(day_dict)
            final_days.append(day_dict)

        return final_days

    def _format_location(self, location: str) -> dict:
        try: location_dict = next(item for item in ALL['Locations'] if item["Name"] == location)
        except Exception as e:
            location_dict = {'ID': len(ALL['Locations']) + 1, 'Name': location}
            ALL['Locations'].append(location_dict)
            
        return location_dict

    def _format_period(self, period: str) -> dict:
        try: period_dict = next(item for item in ALL['Periods'] if item["Name"] == period)
        except Exception as e:
            period_dict = {'ID': len(ALL['Periods']) + 1, 'Name': period}
            ALL['Periods'].append(period_dict)
            
        return period_dict

    def _format_nature(self, nature: str) -> dict:
        try: nature_dict = next(item for item in ALL['Natures'] if item["Name"] == nature)
        except Exception as e:
            nature_dict = {'ID': len(ALL['Natures']) + 1, 'Name': nature}
            ALL['Natures'].append(nature_dict)
            
        return nature_dict

    def _format_instructors(self, instructors: str) -> list[dict]:
        try: temp_instructors = " ".join(instructors.replace(' (P)', '').split()).split(', ')
        except Exception as e: temp_instructors = ['TBA']

        final_instructors = []

        for temp_instructor in temp_instructors:
            try: instructor_dict = next(item for item in ALL['Instructors'] if item["Name"] == temp_instructor)
            except Exception as e:
                instructor_dict = {'ID': len(ALL['Instructors']) + 1, 'Name': temp_instructor}
                ALL['Instructors'].append(instructor_dict)
            final_instructors.append(instructor_dict)
 
        return final_instructors

    def _format_attributes(self, attributes: list) -> list[dict]:
        final_attributes = []
        
        for attr in attributes:
            try: attr_dict = next(item for item in ALL['Attributes'] if item["Name"] == attr)
            except Exception as e:
                attr_dict = {'ID': len(ALL['Attributes']) + 1, 'Name': attr}
                ALL['Attributes'].append(attr_dict)
            final_attributes.append(attr_dict)
            
        return final_attributes
    
    def _update_mappings(self, mappings: dict) -> None:
        global SUBJECT_MAPPING
        logger = logging.getLogger('_update_mappings')
        update = False
        
        for key, value in mappings.items():
            if key not in SUBJECT_MAPPING:
                update = True
                SUBJECT_MAPPING[key] = value
                logger.debug(f'Added {key} --> {value}')
        
        if update:
            SUBJECT_MAPPING = dict(sorted(SUBJECT_MAPPING.items(), key = lambda x : x[1]))
            with open('mappings.json', 'w', encoding='UTF-8') as f: f.write(dumps(SUBJECT_MAPPING, indent=4))
     
    def _parse_courses(self, rows: list) -> list[dict]:
        logger = logging.getLogger('_parse_courses')
        rows = iter(rows)
        
        courses = []
        course = {}

        while True:
            try:
                row = next(rows)
                if row.find('th') and row.find('th')['class'][0] == 'ddtitle':
                    item = row.text.strip().split(' - ')
                    while len(item) != 4: # Instance when Course Name has ' - '
                        item[0] = item[0] + ' - ' + item[1]
                        del item[1]
                                                
                    course = {
                        'CRN': item[1],
                        'Section': item[3],
                        'Subject': self._format_subject(item[2].split(' ')[0]),
                        'Abbreviation': self._format_abbreviation(item[2].split(' ')[0]),
                        'Level': item[2].split(' ')[1],
                        'Name': item[0],
                        'Description': None,
                        'Credits': None,
                        'Capacity': None,
                        'Registered': None,
                        'Remaining': None,
                        'Waitlisted': None,
                        'Prerequisites': None,
                        'Corequisites': None,
                        'Mutual Exclusions': None,
                        'Cross List Courses': None,
                        'Restrictions': None,
                        'Attributes': [],
                        'Properties': []
                    }

                    course_uri = row.find('a')['href']
                    self.number_and_stuff_uri.append(course_uri)
                    
                    row = next(rows)
                    
                    desc_uri = row.find('a')['href']
                    self.desc_uris.append(desc_uri)
                    
                    course['Credits'] = findall(r'\d\.\d\d\d.*(?= )', row.text)[0].replace(' TO        ', ' - ')
                    course['Attributes'] = self._format_attributes(findall(r'(?<=Attributes\: )(.*?)(?= \n)', row.text)[0].split(', ') if 'Attributes' in row.text else [])

                    rendezvous = row.find_all('tr')
                    
                    if len(rendezvous) != 0: # Handle if no meeting times have been created yet.
                        del rendezvous[0] # Contains column headers
                        
                        for rende in rendezvous:
                            sub_rows = rende.find_all('td')
                            if len(sub_rows) < 6: 
                                continue
                            
                            course['Properties'].append({ # Courses can have multiple meeting locations/times
                            'Type': self._format_type(sub_rows[0].text),
                            'Time': self._format_time(sub_rows[1].text),
                            'Days': self._format_days(sub_rows[2].text),
                            'Location': self._format_location(sub_rows[3].text),
                            'Period': self._format_period(sub_rows[4].text),
                            'Nature': self._format_nature(sub_rows[5].text),
                            'Instructors': self._format_instructors(sub_rows[6].text.strip())
                            })
                    else: # Handling required for DataTables orthogonal data                        
                        course['Properties'].append({
                        'Type': self._format_type('TBA'),
                        'Time': self._format_time('TBA'),
                        'Days': self._format_days('TBA'),
                        'Location': self._format_location('TBA'),
                        'Period': self._format_period('TBA'),
                        'Nature': self._format_nature('TBA'),
                        'Instructors': self._format_instructors('TBA')
                        })
                            
                    courses.append(course)
            except StopIteration: break
            except Exception as e: logger.exception(f'{type(e)} | {e}\nRow: {row}\nCourse: {course}')
        return courses

    def _parse_extra_course_info(self, source: str) -> list:
        logger = logging.getLogger('_parse_extra_course_info')
        source = sub(r'<a href="([^"]*)">(.*?)</a>', r'\2', source).replace('\n', '').replace('&nbsp;', '')
        
        no_needs = ['Search', 'Associated Term:', 'Capacity', 'Actual', 'Remaining', 'Seats', 'Waitlist Seats', 'Cross List Seats']
        fields = [field.strip() for field in findall(r'(?<=class\="fieldlabeltext"\>)(.*?)(?=\<\/SPAN)', source)] # Remove trailing spaces
        
        fields = list(set(fields) - set(no_needs))
        
        stuff = {'Prerequisites': None, 'Corequisites': None, 'Mutual Exclusions': None, 'Cross List Courses': None, 'Restrictions': None}
                
        for field in fields:
            if field not in ['Prerequisites:', 'Corequisites:', 'Mutual Exclusions:', 'Mutual Exclusion:', 'Cross List Courses:', 'Restrictions:']: logger.debug(f'New Field: {field}')
            else:
                sub_parse = findall(r'(?<=' + field + r')(.*?)(?=\<SPAN|\<\/TD)', source)[0]
                items = [item.strip() for item in findall(r'(?<=<br />)(.*?)(?=<br />)', sub_parse) if len(item.strip()) > 0 and item.strip() != '<br />'] # Remove empty items
                  
                #with open(f'temp/{field}.txt', 'a') as f: f.write(str(items) + '\n') 
                        
                if field == 'Prerequisites:':
                    items = [item.replace('  ', ' ').replace('( ', '(').replace('Undergraduate level', '').replace('  ', ' ').replace('( ', '(').strip() for item in items] # Some cleanup, better formatting later?
                    stuff['Prerequisites'] = items
                elif field == 'Corequisites:':
                    stuff['Corequisites'] = items
                elif field == 'Mutual Exclusions:' or field == 'Mutual Exclusion:':
                    del items[0] # First entry should just be description                            
                    stuff['Mutual Exclusions'] = items
                elif field == 'Cross List Courses:':
                    stuff['Cross List Courses'] = items
                elif field == 'Restrictions:':
                    new_items = []
                    for item in items:
                        if 'following' in item:
                            if 'req' in locals(): new_items.append(req) # Initial
                            req = {'Description': item, 'Requirements': []}
                        else: req['Requirements'].append(item)
                    
                    new_items.append(req)
                    stuff['Restrictions'] = new_items
        return stuff           
    
    def get_calanders(self, all_calanders: bool = False) -> list[dict]:
        logger = logging.getLogger('get_calanders')
        with Client(base_url='https://selfservice.drew.edu', verify=False, timeout=60) as session:
            try:
                first_headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
                    }
                first_response = session.get('/prod/bwckschd.p_disp_dyn_sched', headers=first_headers)
                if '>Dynamic Schedule<' in first_response.text:
                    
                    calanders = []
                    cal_ids = findall(r'(?<=OPTION VALUE=")(\d\d.*?)(?=")', first_response.text)
                    cal_names = findall(r'(?<=\d\d"\>)(.*?)(?=\<)', first_response.text)
                    for cal_id, cal_name in zip(cal_ids, cal_names): calanders.append({'Calander ID': cal_id, 'Calander Name': cal_name.replace(' (View only)', ''), 'Processing Time': 0, 'Courses': []})

                    if not all_calanders: calanders = [calanders[0]]
                    
                    return calanders
            except Exception as e: logger.exception(f'{type(e)} | {e}')
    
    def get_courses(self, calanders: list[dict]) -> list[dict]:
        logger = logging.getLogger('get_courses')
        with Client(base_url='https://selfservice.drew.edu', verify=False, timeout=60) as session:
            for calander in calanders:
                start_time = time()
                
                try:
                    first_headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'https://selfservice.drew.edu',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                        'Referer': 'https://selfservice.drew.edu/prod/bwckschd.p_disp_dyn_sched',
                        'Accept-Language': 'en-US,en;q=0.9'
                        }
                    first_data = {'p_calling_proc': 'bwckschd.p_disp_dyn_sched', 'p_term': calander['Calander ID'], 'p_by_date': 'Y', 'p_from_date': '', 'p_to_date': ''}
                    first_response = session.post('/prod/bwckgens.p_proc_term_date', headers=first_headers, data=first_data)
                    if '>Class Schedule Search</' in first_response.text:
                        source = first_response.text.strip().replace('\n', '')
                        
                        subset = findall(r'(?<=subj_id"\>)(.*?)(?=\<\/select)', source)[0]
                        mappings = {item.split('">')[0]: item.split('">')[1] for item in findall(r'(?<=OPTION VALUE=")(.*?)(?=\<)', subset)}
                        self._update_mappings(mappings)
                                                        
                        terms_one = [term.replace('" value="', '=') for term in findall(r'(?<="hidden" name=")(.*?)(?=" /)', source)]
                        terms_two = [f'sel_subj={course}' for course in findall(r'(?<=OPTION VALUE\=")(.*?)(?=")', subset)]
                        terms_three = [f'{term}=' for term in findall(r'(?<=input type\="text" name\=")(.*?)(?=")', source)]
                        terms_four = [f'{a}={b}' for a, b in zip(findall(r'(?<=select name\=")(.*?)(?=")', source)[1:], findall(r'(?<="\>\<OPTION VALUE\=")(.*?)(?=")', source)[1:])]
                        
                        second_data = '&'.join(terms_one + terms_two + terms_three + terms_four).replace('%', '%25')
                        
                        try:  
                            first_headers['Referer'] = 'https://selfservice.drew.edu/prod/bwckgens.p_proc_term_date'
                            second_response = session.post('/prod/bwckschd.p_get_crse_unsec', headers=first_headers, data=second_data)
                            
                            if 'Class Schedule Listing<' in second_response.text:
                                first_headers['Referer'] = 'https://selfservice.drew.edu/prod/bwckschd.p_get_crse_unsec'
                                soup = BeautifulSoup(second_response.content, features='html.parser')
                                
                                table = soup.find('table', class_='datadisplaytable')
                                rows = table.find_all('tr')
                                
                                courses = self._parse_courses(rows)
                                asyncio.run(self._visit_uris(first_headers))
                                                                        
                                for course, num_and_stuff, desc in zip(courses, self.number_and_stuff_uri, self.desc_uris): # Unpacking
                                    course['Capacity'] = num_and_stuff['Capacity']
                                    course['Registered'] = num_and_stuff['Registered']
                                    course['Remaining'] = num_and_stuff['Remaining']
                                    course['Waitlisted'] = num_and_stuff['Waitlisted']
                                    
                                    stuff = num_and_stuff['Stuff']
                                    
                                    course['Prerequisites'] = stuff['Prerequisites']
                                    course['Corequisites'] = stuff['Corequisites']
                                    course['Mutual Exclusions'] = stuff['Mutual Exclusions']
                                    course['Cross List Courses'] = stuff['Cross List Courses']
                                    course['Restrictions'] = stuff['Restrictions']
                                    
                                    course['Description'] = desc                                            
                                
                                calander['Processing Time'] = round(time() - start_time)
                                calander['Courses'] = courses  
                                self._reset_uris()
                                
                                print(f'Done Calander {calander["Calander Name"]} in {calander["Processing Time"]}')
                        except Exception as e: logger.exception(f'Getting Courses | {type(e)} | {e}\nCalander: {calander}')
                except Exception as e: logger.exception(f'Getting Mappings | {type(e)} | {e}\nCalander: {calander}')
            return calanders
            # with open('table.json', 'w', encoding='UTF-8') as f: f.write(dumps(calanders, indent=4))

    async def _visit_uris(self, second_headers: dict) -> None:
        logger = logging.getLogger('_visit_uris')
        async with AsyncClient(base_url='https://selfservice.drew.edu', verify=False, timeout=60) as async_session:
            try:
                tasks = [self._get_desc(async_session, second_headers, number_uri) for number_uri in self.desc_uris]
                self.desc_uris = await asyncio.gather(*tasks) # Connection timeouts, cannot figure out yet, maybe dont use httpx
                
                tasks = [self._get_numbers_and_stuff(async_session, second_headers, number_uri) for number_uri in self.number_and_stuff_uri]
                self.number_and_stuff_uri = await asyncio.gather(*tasks)
            except Exception as e: logger.exception(f'{type(e)} | {e}')
    
    async def _get_desc(self, session: AsyncClient, headers: dict, uri: str) -> str:
        logger = logging.getLogger('_get_desc')
        try:
            a = await session.get(uri, headers=headers)
            if '>Catalog Entries<' in a.text:
                soup = BeautifulSoup(a.content, features='html.parser')
                selection = soup.find('td', class_='ntdefault')
                
                return findall(r'(?<=class="ntdefault"\>)(.*?)(?=\<)', str(selection).replace('\n', ''))[0].strip()
        except Exception as e: logger.exception(f'{type(e)} | {e}')
        return ''
    
    async def _get_numbers_and_stuff(self, session: AsyncClient, headers: dict, uri: str) -> dict:
        logger = logging.getLogger('_get_numbers_and_stuff')
        try:
            a = await session.get(uri, headers=headers)
            if '>Detailed Class Information<' in a.text:
                soup = BeautifulSoup(a.content, features='html.parser')
                
                table = soup.find_all('table', class_='datadisplaytable')[1]
                rows = table.find_all('tr')
                
                seats = rows[1].find_all('td', class_='dddefault')
                waitlisted = rows[2].find_all('td', class_='dddefault')
                
                # Though we could account for cross-list seats, I will not
                
                stuff = self._parse_extra_course_info(a.text)
                            
                return {'Capacity': int(seats[0].text), 'Registered': int(seats[1].text), 'Remaining': int(seats[2].text), 'Waitlisted': int(waitlisted[1].text), 'Stuff': stuff}             
        except Exception as e: logger.exception(f'{type(e)} | {e}')
        
        stuff = {'Prerequisites': None, 'Corequisites': None, 'Mutual Exclusions': None, 'Cross List Courses': None, 'Restrictions': None}
        return {'Capacity': 0, 'Registered': 0, 'Remaining': 0, 'Waitlisted': 0, 'Stuff': stuff}
    
@app.route('/get_courses', methods=['GET'])
@cache.cached(timeout=60 * 10)
def handle_request():
    calanders = schedule.get_calanders(all_calanders = False)
    return schedule.get_courses(calanders = calanders)

schedule = Schedules()
app.run(host='0.0.0.0', debug=True, port=8080)