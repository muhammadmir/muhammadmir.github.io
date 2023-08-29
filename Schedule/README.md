# Schedule Project
An easier way to search and filter courses by various properties.

---

## Table of Contents
1. [Definitions](#Definitions)
2. [About](#About)
3. [How It Works](#How-It-Works)
4. [Functionality](#Functionality)
    * [Search Panes](#Search-panes)
    * [Cascading](#Cascading)
4. [Usage](#Usage)
5. [Benefits](#Benefits)
    * [Searching and Filtering](#Searching-and-Filtering)
    * [Data Analysis](#Data-Analysis)
6. [Replication](#Replication)
7. [Todo List](#Todo-List)

## Definitions
**Calendar** - Refers to a semester and year where courses are offered, such as "Fall 2023." Every Calendar has an "interface" where you can view courses based on a query.

**Dynamic Schedule** - A place where you can select a Calendar and view courses offered in that Calendar. The public one can be found [here](https://selfservice.drew.edu/prod/bwckschd.p_disp_dyn_sched). The various versions can be found at the [Registrar's webpage](https://drew.edu/registrars-office/about-us/catalogs-class-schedule/).

---

## About
I didn't like the way the Calendar was set up. I thought the interface was unappealing, unintuitive, and limited. I wanted to find courses that fulfilled a specific set of requirements, and doing so with the current features made it very tedious and difficult. Because I grew tired of this and knew the solution was simple, I started this project so I could make my life easier.

---

## How It Works
Using [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), I parsed the crummy HTML tables and all related information to courses and developed a structure to represent the information about a course programmatically. I first did this for one Calendar and then made it dynamic so it would be applicable for the entire Dynamic Schedule. After having my structure, I used [DataTables](https://datatables.net) to construct the new table. You can view it [here](#Usage).


It's important to know there are two versions of the Dynamic Schedule, and I chose the public version to gather my information from. The other version required a valid Drew login. The main difference between these two versions--in the context of this project--is that the public version requires you to visit an extra URI for *each* course to get information about the course's capacity, remaining slots, etc. Regardless of which version you use, they both have essentially the same interface and both query for the same information.

---

## Functionality
Interacting with DataTables is really intuitive. Here are some of the neat features relevant to this table:
1. Each row (course) has a button to the left that when clicked, reveals the child rows, or information like CRN, attributes, meeting times, and more for that particular course.

2. Just above the table there is a search bar where you can search for terms or words that appears anywhere in the table.

3. By default, only the first 10 rows (courses) are shown. To see the total number of rows that match the current filters applied, look to the bottom left of the table. Additionally, you can cycle through all the courses by changing the page number at the bottom right.

4. The panels above the table are called Search Panes, which provide additional searching and filtering functionality. More on that [later](#Search-Panes).

5. Any searching or filtering action will only present all other possible combinations that meet that searched/filtered action.

6. For the nerds, you can download the course structure as JSON of either multiple calendars (during Calendar Selection), a specific Calendar (using Download Filtered Results button with no filters applied or going to Session Storage), or of a specific query of a specific Calendar (using Download Filtered Results).

### Search Panes
One of the biggest motivators of this project was the desire for the functionality of Search Panes. Courses are a definitive structure and have properties like a name, level, meeting time and day, attributes, number of people registered, etc. Wouldn't it be super useful to know which courses that in Music also have a specific attribute you need to fulfill a GenEd requirement? The 8 Search Panes (or simply Panes) allow us to do this and much more.

Each Pane can be searched and sorted. Additionally, the number of available rows (courses) that have a particular Option of a particular Pane are displayed on the right side of the Option. As you select multiple Options across Panes, the results [cascade](#Cascading).

By default, the logic across Options of Panes (inter-Pane logic) is OR. Meaning, selecting the Option "Finance" from the Pane "Subject" and the Option "Full" from the Pane "Capacity" will show you results (courses) that either in Finance OR are have reached maximum capacity. The current inter-Pane logic is listed in the Logic button.

However, inter-Pane logic being AND can be useful, too. To enable that option, simply click on the Logic button. Note: you cannot change the logic between options of a Pane (intra-Pane Logic)

### Cascading
Cascading refers to when there is one or more filters applied and only the matching results and remaining available Options are presented. All non-matching results or impossible options are "cascaded," or not shown. Note: cascading of Options within a Pane (intra-Pane cascade) is not supported, only Options across Panes is (inter-Pane cascading).

Example:
Selecting the Option "Anthropology" from the Pane "Subject" will immediately present you all the courses in that discipline. Additionally, it will cascade all impossible Options across all **other** Panes, such as not showing all the instructors that don't teach the discipline or not displaying attributes that usually aren't associated with the discipline like "TS-Ecology."

Another thing that should be noted is when the table loads, by default all the Options that are available are presented already. Meaning, if you do not see a specific attribute and no filters are applied, then that attribute simply does not appear in any course for the selected calendar.

---

## Usage
To see a live version, click [here](https://muhammadmir.github.io/Schedule/). Please note results are NOT cached.

---

## Benefits
There are two main benefits:

### Searching and Filtering
As described in [Functionality](#Functionality).

### Data Analysis
While Registrar does not make certain information public like how many students an instructor has for a given semester or the number of courses with a certain attribute, this data is all publicly available because the Calendar is publicly available. The information is there, but it is not represented in a friendly manner. By using the several means I made available, anyone can readily download the data and unnest the structure to easily perform a data analysis.

---

## Replication
To replicate and host yourself:
1. Make a copy of `Schedule` folder
2. Run `file.py` on a server
3. Edit `SERVER` variable in `index.html` with your server link.

---

## Todo List
1. Make front-end prettier? (idk)