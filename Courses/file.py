from bs4 import BeautifulSoup
from httpx import Client
from urllib3 import disable_warnings
from re import findall
from json import dumps, loads
from typing import Optional
from flask import Flask
from flask_caching import Cache
disable_warnings()

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)

# https://drew.edu/registrars-office/about-us/facultystaff/course-attribute-overview/
SUBJECT_MAPPING = {
    'EAP': 'Academic English',
    'AMST': 'American Studies',
    'ANTH': 'Anthropology',
    'ARBC': 'Arabic Language',
    'ART': 'Art',
    'ARTH': 'Art History',
    'ARFA': 'Arts & Letters Fine Arts/Media',
    'AREL': 'Arts & Letters Literature',
    'ARSP': 'Arts & Letters Spirituality',
    'ARWR': 'Arts & Letters Writing',
    'ARLT': 'Arts and Letters',
    'ARTT': 'Arts and Teaching',
    'BBCL': 'Bible and Cultures',
    'BCHM': 'Biochemistry',
    'BIOL': 'Biology',
    'BST': 'Business',
    'CHEM': 'Chemistry',
    'CHIN': 'Chinese',
    'CE': 'Civic Engagement',
    'CLAS': 'Classics',
    'CRW': 'Comm, Research, Writing',
    'CSCI': 'Computer Science',
    'CRES': 'Conflict Resolution',
    'DANC': 'Dance',
    'DATA': 'Data Sciences',
    'DMIN': 'Doctor of Ministry',
    'ECON': 'Economics',
    'EDUC': 'Education',
    'EOS': 'Educational Opportunity Prog',
    'ENGH': 'English',
    'ENV': 'Environmental Science',
    'ESS': 'Environmental Stud and Sustain',
    'ETH': 'Ethics',
    'FILM': 'Film',
    'FIN': 'Finance',
    'FREN': 'French',
    'GERM': 'German',
    'GDR': 'Graduate Division of Religion',
    'HIST': 'History',
    'HOST': 'Holocaust Studies',
    'HON': 'Honors',
    'HUM': 'Humanities',
    'INTD': 'Interdisciplinary',
    'INTF': 'Interfaith Studies',
    'INTC': 'Internship-CLA',
    'ITAL': 'Italian',
    'LAT': 'Latin',
    'DREW': 'Launch',
    'LING': 'Linguistics',
    'MATH': 'Mathematics',
    'MCOM': 'Media & Communications',
    'MDHM': 'Medical Humanities',
    'MUS': 'Music',
    'NEUR': 'Neuroscience',
    'PAST': 'Pan-African Studies',
    'PCC': 'Pastoral Care Counseling',
    'PHIL': 'Philosophy',
    'PE': 'Physical Education',
    'PHYS': 'Physics',
    'PSCI': 'Political Science',
    'PRTH': 'Practical Theology',
    'PREA': 'Preaching',
    'PSYC': 'Psychology',
    'PH': 'Public Health',
    'REL': 'Religion',
    'RLSC': 'Religion and Society',
    'REDU': 'Religious Education',
    'RUSS': 'Russian',
    'SOC': 'Sociology',
    'SPAN': 'Spanish',
    'SPCH': 'Speech',
    'STAT': 'Statistics',
    'TMUS': 'TS - Music',
    'THST': 'TS-HIST',
    'THEA': 'Theatre Arts',
    'TPHL': 'Theo. & Philosophical Stds',
    'THEO': 'Theology',
    'TREC': 'Travel Course',
    'UNIV': 'University',
    'VOCF': 'Vocation and Formation',
    'WESM': 'Wesleyan/Methodist Studies',
    'WGST': 'Women\'s and Gender Studies',
    'WOR': 'Worship and Liturgy',
    'WRTG': 'Writing'
}
ALL = {
    'Subjects': [],
    'Abbreviations': [],
    'Types': [],
    'Locations': [],
    'Natures': [],
    'Days': [],
    'Times': [],
    'Instructors': [],
    'Attributes': []
}

class Schedules():
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        self.username = username
        self.password = password
        self.valid = False
        
    def _authenticate(self):
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
                                    except Exception as e: raise Exception(f"Error: {e}")
                            except Exception as e: raise Exception(f"Error: {e}")
                    except Exception as e: raise Exception(f"Error: {e}")
            except Exception as e: raise Exception(f"Error: {e}")
    
    def _get_desc(self, session: Client, headers: dict, uri: str):
        try:
            a = session.get('https://selfservice.drew.edu/' + uri, headers=headers)
            if '>Catalog Entries<' in a.text:
                soup = BeautifulSoup(a.content, features='html.parser')
                selection = soup.find('td', class_='ntdefault')
                
                return findall(r'(?<=class="ntdefault"\>)(.*?)(?=\<)', str(selection).replace('\n', ''))[0].strip()
        except Exception as e: print(e)
    
    def _get_numbers(self, session: Client, headers: dict, uri: str):
        try:
            a = session.get('https://selfservice.drew.edu/' + uri, headers=headers)
            if '>Detailed Class Information<' in a.text:
                soup = BeautifulSoup(a.content, features='html.parser')
                table = soup.find_all('table', class_='datadisplaytable')[1]
                rows = table.find_all('tr')
                
                seats = rows[1].find_all('td', class_='dddefault')
                waitlisted = rows[2].find_all('td', class_='dddefault')
                
                return int(seats[0].text), int(seats[1].text), int(seats[2].text), int(waitlisted[1].text)              
        except Exception as e: print(e)
    
    def _format_subject(self, abbreviation: str):
        abbreviation = SUBJECT_MAPPING[abbreviation]
        
        try: subject_dict = next(item for item in ALL['Subjects'] if item["Name"] == abbreviation)
        except Exception as e:
            subject_dict = {'ID': len(ALL['Subjects']) + 1, 'Name': abbreviation}
            ALL['Subjects'].append(subject_dict)
        
        return subject_dict
    
    def _format_abbreviation(self, abbreviation: str):
        try: abbreviation_dict = next(item for item in ALL['Abbreviations'] if item["Name"] == abbreviation)
        except Exception as e:
            abbreviation_dict = {'ID': len(ALL['Abbreviations']) + 1, 'Name': abbreviation}
            ALL['Abbreviations'].append(abbreviation_dict)
        
        return abbreviation_dict
    
    def _format_type(self, class_type: str):
        try: class_type_dict = next(item for item in ALL['Types'] if item["Name"] == class_type)
        except Exception as e:
            class_type_dict = {'ID': len(ALL['Types']) + 1, 'Name': class_type}
            ALL['Types'].append(class_type_dict)
            
        return class_type_dict
        
    def _format_location(self, location: str):
        try: location_dict = next(item for item in ALL['Locations'] if item["Name"] == location)
        except Exception as e:
            location_dict = {'ID': len(ALL['Locations']) + 1, 'Name': location}
            ALL['Locations'].append(location_dict)
            
        return location_dict
    
    def _format_nature(self, nature: str):
        try: nature_dict = next(item for item in ALL['Natures'] if item["Name"] == nature)
        except Exception as e:
            nature_dict = {'ID': len(ALL['Natures']) + 1, 'Name': nature}
            ALL['Natures'].append(nature_dict)
            
        return nature_dict
    
    def _format_time(self, t: str):
        try: t = t.upper().replace(' - ', ' - ')
        except Exception as e: t = 'TBA'

        try: time_dict = next(item for item in ALL['Times'] if item["Name"] == t)
        except Exception as e:
            time_dict = {'ID': len(ALL['Times']) + 1, 'Name': t}
            ALL['Times'].append(time_dict)

        return time_dict
    
    def _format_day(self, days: str):
        final_days = []
        for day in days:

            if day == 'M': day = 'Monday'
            elif day == 'T': day = 'Tuesday'
            elif day == 'W': day = 'Wednesday'
            elif day == 'R': day = 'Thursday'
            else: day = 'Friday'

            try: day_dict = next(item for item in ALL['Days'] if item["Name"] == day) #Get Dict by looking up with Name Key
            except Exception as e:
                day_dict = {'ID': len(ALL['Days']) + 1, 'Name': day}
                ALL['Days'].append(day_dict)
            final_days.append(day_dict)

        return final_days
    
    def _convert_instructors(self, instructors: str):
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

    def _convert_attributes(self, attributes: list): 
        final_attributes = []

        for attr in attributes:
            try: attr_dict = next(item for item in ALL['Attributes'] if item["Name"] == attr)
            except Exception as e:
                attr_dict = {'ID': len(ALL['Attributes']) + 1, 'Name': attr}
                ALL['Attributes'].append(attr_dict)
            final_attributes.append(attr_dict)

        return final_attributes
    
    def get_courses(self) -> list[dict]:
        with Client(base_url='https://selfservice.drew.edu', verify=False, timeout=30) as session:
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
                    cal_ids = findall(r'(?<=OPTION VALUE=")(.*?)(?=")', first_response.text)
                    cal_names = findall(r'(?<=\d\d"\>)(.*?)(?=\<)', first_response.text)
                    for cal_id, cal_name in zip(cal_ids, cal_names): calanders.append({'ID': str(len(calanders)), 'Calander ID': cal_id, 'Calander Name': cal_name.replace(' (View only)', '')})
                    
                    try:
                        second_headers = {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Origin': 'https://selfservice.drew.edu',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                            'Referer': 'https://selfservice.drew.edu/prod/bwckschd.p_disp_dyn_sched',
                            'Accept-Language': 'en-US,en;q=0.9'
                            }
                        second_data = {'p_calling_proc': 'bwckschd.p_disp_dyn_sched', 'p_term': '202330', 'p_by_date': 'Y', 'p_from_date': '', 'p_to_date': ''}

                        second_response = session.post('/prod/bwckgens.p_proc_term_date', headers=second_headers, data=second_data)
                        if '>Class Schedule Search</' in second_response.text:
                            source = second_response.text.strip().replace('\n', '')
                            predefined = { #Won't neecessarily use, will parse categories while parsing the courses
                                'Subjects': findall(r'(?<="\>)(.*?)(?=\<)', findall(r'(?<=MULTIPLE ID\="subj_id"\>)(.*?)(?=\</TD)', source)[0]),
                                'Natures': findall(r'(?<="\>)(.*?)(?=\<)', findall(r'(?<=MULTIPLE ID\="schd_id"\>)(.*?)(?=\</TD)', source)[0]), #Seminar, Lab, Independent Study, etc.
                                'Levels': findall(r'(?<="\>)(.*?)(?=\<)', findall(r'(?<=MULTIPLE ID\="levl_id"\>)(.*?)(?=\</TD)', source)[0]), #Grad, Undergrad, Masters, etc.
                                'Lengths': findall(r'(?<="\>)(.*?)(?=\<)', findall(r'(?<=MULTIPLE ID\="ptrm_id"\>)(.*?)(?=\</TD)', source)[0]), #1st Half, 2nd Half, Full Term
                                'Instructors': findall(r'(?<="\>)(.*?)(?=\<)', findall(r'(?<=MULTIPLE ID\="instr_id"\>)(.*?)(?=\</TD)', source)[0]),
                                'Types': findall(r'(?<="\>)(.*?)(?=\<)', findall(r'(?<=MULTIPLE ID\="sess_id"\>)(.*?)(?=\</TD)', source)[0]), #In Person, Hybrid, Online, etc.
                                'Attributes': findall(r'(?<="\>)(.*?)(?=\<)', findall(r'(?<=MULTIPLE ID\="attr_id"\>)(.*?)(?=\</TD)', source)[0])
                            }
                            
                            try:  
                                second_headers['Referer'] = 'https://selfservice.drew.edu/prod/bwckgens.p_proc_term_date'
                                third_response = session.post('/prod/bwckschd.p_get_crse_unsec', headers=second_headers, data='term_in=202330&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj=EAP&sel_subj=AMST&sel_subj=ANTH&sel_subj=ARBC&sel_subj=ART&sel_subj=ARTH&sel_subj=ARFA&sel_subj=AREL&sel_subj=ARSP&sel_subj=ARWR&sel_subj=ARLT&sel_subj=ARTT&sel_subj=BBCL&sel_subj=BCHM&sel_subj=BIOL&sel_subj=BST&sel_subj=CHEM&sel_subj=CHIN&sel_subj=CE&sel_subj=CLAS&sel_subj=CRW&sel_subj=CSCI&sel_subj=CRES&sel_subj=DANC&sel_subj=DATA&sel_subj=DMIN&sel_subj=ECON&sel_subj=EDUC&sel_subj=EOS&sel_subj=ENGH&sel_subj=ENV&sel_subj=ESS&sel_subj=ETH&sel_subj=FILM&sel_subj=FIN&sel_subj=FREN&sel_subj=GERM&sel_subj=GDR&sel_subj=HIST&sel_subj=HOST&sel_subj=HON&sel_subj=HUM&sel_subj=INTD&sel_subj=INTF&sel_subj=INTC&sel_subj=ITAL&sel_subj=LAT&sel_subj=DREW&sel_subj=LING&sel_subj=MATH&sel_subj=MCOM&sel_subj=MDHM&sel_subj=MUS&sel_subj=NEUR&sel_subj=PAST&sel_subj=PCC&sel_subj=PHIL&sel_subj=PE&sel_subj=PHYS&sel_subj=PSCI&sel_subj=PRTH&sel_subj=PREA&sel_subj=PSYC&sel_subj=PH&sel_subj=REL&sel_subj=RLSC&sel_subj=REDU&sel_subj=RUSS&sel_subj=SOC&sel_subj=SPAN&sel_subj=SPCH&sel_subj=STAT&sel_subj=TMUS&sel_subj=THST&sel_subj=THEA&sel_subj=TPHL&sel_subj=THEO&sel_subj=TREC&sel_subj=UNIV&sel_subj=VOCF&sel_subj=WESM&sel_subj=WGST&sel_subj=WOR&sel_subj=WRTG&sel_crse=&sel_title=&sel_schd=%25&sel_from_cred=&sel_to_cred=&sel_levl=UG&sel_ptrm=%25&sel_dunt_unit=&sel_dunt_code=DAY&sel_instr=%25&sel_sess=%25&sel_attr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a')
                                
                                if 'Class Schedule Listing<' in third_response.text:
                                    second_headers['Referer'] = 'https://selfservice.drew.edu/prod/bwckschd.p_get_crse_unsec'
                                    soup = BeautifulSoup(third_response.content, features='html.parser')
                                    
                                    table = soup.find('table', class_='datadisplaytable')
                                    rows = iter(table.find_all('tr'))
                                    
                                    courses = []
                                    course = {}

                                    while True:
                                        try:
                                            row = next(rows)
                                            if row.find('th') and row.find('th')['class'][0] == 'ddtitle':
                                                item = row.text.strip().split(' - ')
                                                if len(item) != 4: #Instance when Course Name has ' - '
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
                                                    'Attributes': [],
                                                    'Properties': []
                                                    }

                                                course['Capacity'], course['Registered'], course['Remaining'], course['Waitlisted'] = self._get_numbers(session, second_headers, row.find('a')['href'])
                                                row = next(rows)

                                                course['Description'] = self._get_desc(session, second_headers, row.find('a')['href'])
                                                course['Credits'] = findall(r'\d\.\d\d\d.*(?= )', row.text)[0]
                                                course['Attributes'] = self._convert_attributes(findall(r'(?<=Attributes\: )(.*?)(?= \n)', row.text)[0].split(', ') if 'Attributes' in row.text else [])

                                                rendezvous = row.find_all('tr')
                                                del rendezvous[0] # Contains column headers
                                                
                                                for rende in rendezvous:
                                                    sub_rows = rende.find_all('td')
                                                    course['Properties'].append({ #Apparently a class can have multipe meeting locations, dates, etc?
                                                        'Type': self._format_type(sub_rows[0].text),
                                                        'Time': self._format_time(sub_rows[1].text),
                                                        'Days': self._format_day(sub_rows[2].text),
                                                        'Location': self._format_location(sub_rows[3].text),
                                                        'Period': sub_rows[4].text, #Presumed to be the same for every course.
                                                        'Nature': self._format_nature(sub_rows[5].text),
                                                        'Instructors': self._convert_instructors(sub_rows[6].text.strip())
                                                        })
                                                courses.append(course)

                                        except StopIteration: break
                                    return courses
                                    with open('table.json', 'w', encoding='UTF-8') as f: f.write(dumps(courses, indent=4))
                            except Exception as e: print(e)
                    except Exception as e: print(e)
            except Exception as e: print(e)

@app.route('/get_courses', methods=['GET'])
@cache.cached(timeout=100)
def handle_request():
    return schedule.get_courses()

schedule = Schedules()
app.run(debug=True)
