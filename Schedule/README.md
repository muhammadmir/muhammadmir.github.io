# Schedule Project
An easier way to search and filter courses by various properties.

---

## Definitions
**Dynamic Schedule** - A place where you can select a Calander and view courses offered in that Calander. The public one can be found [here](https://selfservice.drew.edu/prod/bwckschd.p_disp_dyn_sched). The various versions can be found at the [Registrar's webpage](https://drew.edu/registrars-office/about-us/catalogs-class-schedule/).

**Calander** - Refers to a semester and year where courses are offered, such as "Fall 2023." Every Calander has an "interface" where you could view courses based on a query.

---

## About
I didn't like the way the Calander was set up. I thought the interface was unappealing, unintuitive, and limited. I wanted to find courses that fulfilled a specific set of requirements, and doing so with the current features made it very tedious and difficult. Because I grew tired of this and knew the solution was simple, I started this project so I could make my life easier.

---

## How It Works
I scraped and parsed information about courses available from one Calander and re-represented the course by developing a structure that encapsulated their properties like name, level, credits, instructors, times, etc. After doing this for one Calander, I made the entire process dynamic for the entire Dynamic Schedule. Currently, you are able to view a better interface for one Calander at a time, but can download the JSON data for any number of calanders.

It's important to know there are two version of the Dynamic Schedule, and I chose the public version to gather my information from. The other version required a valid Drew login. The main difference between these two versions--in the context of this project--is that the public version requires you visit an extra URI for *each* course to get information about the course's capacity, remaining slots, etc. Regardless of which version you use, they both have essentially the same interface and both query for the same information.

---

## Usage
To see a live version, click [here](https://muhammadmir.github.io/Schedule/).

---

## Benefits
There are two main benefits:

### Searching and Filtering
The regular interface is limited. You can make a query with multiple filters. For example, you can select multiple subjects, instructors, and attributes. However, the logic is **OR**, not **AND**. So, if you wanted to know which two or more attributes are applied to the same course, you cannot know and you must tediously CTRL+F to find such a course that does have that.

Additionally, as you select properties, the unavaialable properties do not collapse. You must submit the query and then it will tell you whether or not courses with those condition exist, and if they don't, you have to go back the page, reload it, and re-select. Furthemore, you have to click on an extra link just to get information like the course description or pre-requsities. And, depending on the Dynamic Schedule, there is another link to visit just to see how many people have registered or waitlisted.

Along with some additional tweaks, I refined the way to view course properties so it is more useful.

### Data Analysis
While Registrar does not make certain information public like how many students does an instructor have for a given semester, or the number of courses with a certain attribute, this data is all publicly available because the calander is publicly available. The information is there, but it is not represented in a friendly manner.

Because my initial goal of the project, parsing the data neatly and effectively was a pre-requisite. By doing this, I elminated the need of someone developing a parser for this. They can instead just vist the live version of this project and download the data for the calander(s) they want and easily perform analyses.

---

## Replication
To replicate and host yourself:
1. Make a copy of `Schedule` folder
2. Run `file.py` on a server
3. Edit `index.html` with link to server

---

## Todo List
1. Front-end updates
2. Download courses selected after filtraton
3. Fix the SearchPanes search panels not showing proper text?