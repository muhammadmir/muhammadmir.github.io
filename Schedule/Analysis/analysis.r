library(jsonlite)
library(magrittr)
library(dplyr)
library(tidyr)
library(ggplot2)
library(treemapify)

data <- fromJSON("../table.json") %>%
    as.data.frame() %>%
    unnest(cols = c(Courses), names_sep = ".")


# Basic information about Arabic Language Courses
data %>%
    unnest(cols = c(Courses.Subject, Courses.Properties), names_sep = ".") %>%
    unnest(cols = c(Courses.Properties.Instructors), names_sep = ".") %>%
    filter(grepl("Arabic", Courses.Subject.Name)) %>%
    select(
        "Calander Name",
        Courses.Subject.Name,
        Courses.Name,
        Courses.Level,
        Courses.Credits,
        Courses.Registered,
        Courses.Properties.Instructors.Name
    ) %>%
    distinct %>%
    print(n = 100)


# Number of Courses per Subject
data %>%
    select(Courses.Subject) %>%
    unnest(cols = c(Courses.Subject), names_sep = ".") %>%
    select(Courses.Subject.Name) %>%
    group_by(Courses.Subject.Name) %>%
    summarise(count = n()) %>%
    arrange(desc(count))

# Number of Instructors
data %>%
    select(Courses.Properties) %>%
    unnest(cols = c(Courses.Properties), names_sep = ".") %>%
    unnest(cols = c(Courses.Properties.Instructors), names_sep = ".") %>%
    select(Courses.Properties.Instructors.Name) %>%
    group_by(Courses.Properties.Instructors.Name) %>%
    summarise(count = n()) %>%
    arrange(desc(count))

# Number of Attributes
df <- data %>%
    select(Courses.Attributes) %>%
    unnest(cols = c(Courses.Attributes), names_sep = ".") %>%
    select(Courses.Attributes.Name) %>%
    group_by(Courses.Attributes.Name) %>%
    summarise(count = n()) %>%
    arrange(desc(count)) %>%
    as.data.frame()

ggplot(df, aes(
    area = count,
    label = paste(Courses.Attributes.Name, count, sep = "\n"),
    fill = Courses.Attributes.Name
)) +
    geom_treemap() +
    geom_treemap_text(
        colour = "white",
        place = "centre",
        size = 15
    ) +
    theme(legend.position = "none")

# Group by Subject and Class Type
data %>%
    select(Courses.Subject, Courses.Properties) %>%
    unnest(cols = c(Courses.Subject, Courses.Properties), names_sep = ".") %>%
    unnest(cols = c(Courses.Properties.Type), names_sep = ".") %>%
    select(Courses.Subject.Name, Courses.Properties.Type.Name) %>%
    group_by(Courses.Subject.Name, Courses.Properties.Type.Name) %>%
    summarise(count = n()) %>%
    arrange(desc(count)) %>%
    spread(Courses.Properties.Type.Name, count, fill = 0)


# Group by Subject and Attributes
data %>%
    select(Courses.Subject, Courses.Attributes) %>%
    unnest(cols = c(Courses.Subject, Courses.Attributes), names_sep = ".") %>%
    group_by(Courses.Subject.Name, Courses.Attributes.Name) %>%
    summarize(count = n()) %>%
    spread(Courses.Attributes.Name, count, fill = 0)

# Group by Subject and Day
data %>%
    select(Courses.Subject, Courses.Properties) %>%
    unnest(cols = c(Courses.Subject, Courses.Properties), names_sep = ".") %>%
    unnest(cols = c(Courses.Properties.Days), names_sep = ".") %>%
    select(Courses.Subject.Name, Courses.Properties.Days.Name) %>%
    group_by(Courses.Subject.Name, Courses.Properties.Days.Name) %>%
    summarise(count = n()) %>%
    arrange(desc(count)) %>%
    spread(Courses.Properties.Days.Name, count, fill = 0)

# Group by Subject and Credits
data %>%
    select(Courses.Subject, Courses.Credits) %>%
    unnest(cols = c(Courses.Subject), names_sep = ".") %>%
    select(Courses.Subject.Name, Courses.Credits) %>%
    group_by(Courses.Subject.Name, Courses.Credits) %>%
    summarise(count = n()) %>%
    arrange(desc(count)) %>%
    spread(Courses.Credits, count, fill = 0)

# Average number of registered people by Subject
data %>%
    select(Courses.Subject, Courses.Registered) %>%
    unnest(cols = c(Courses.Subject), names_sep = ".") %>%
    select(Courses.Subject.Name, Courses.Registered) %>%
    group_by(Courses.Subject.Name) %>%
    summarise(average = mean(Courses.Registered)) %>%
    arrange(desc(average))
