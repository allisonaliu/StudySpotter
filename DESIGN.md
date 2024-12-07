# StudySpotter Design

## Table of Contents

1. [Instructions](#instructions)
2. [Motivation](#motivation)
3. [Database Structure](#database-structure)
4. [Ratings and Notes](#ratings-and-notes)
5. [User Info](#user-info)
6. [Error Handling](#error-handling)
7. [Style](#style)
8. [Image Citations](#image-citations)

---

## Instructions

A “design document” for your project in the form of a Markdown file called DESIGN.md that discusses, technically, how you implemented your project and why you made the design decisions you did. Your design document should be at least several paragraphs in length. Whereas your documentation is meant to be a user’s manual, consider your design document your opportunity to give the staff a technical tour of your project underneath its hood.

---

## Motivation

At the start of the semester, I was so intimidated by Harvard's innumerable libraries, lounges, and cafes that I ended up just studying in my dorm most of the time. From speaking with my peers, I knew I wasn't alone in experiencing decision paralysis when faced with all the possible study locations on and around campus. So for my CS50 final project, I decided to create an application which simplifies the process of finding study spots that fit students' individual preferences.

---

## Database Structure

### users ###

The SQL table users stores information specific to each of the application's  users. The username field is a unique index that identifies users; the hash field stores each user's hashed password; and the noise, sociality, crowding, size, and decoration fields store the user's study preferences in the form of a decimal number in the inclusive range [0, 1].

To calculate user "fit" for each study spot, StudySpotter compares these five user preference values with the particular study spot's noise, sociality, crowding, size, and decoration values. I chose to enable NULL for the five user preferences because these fields shouldn't have values until after the user completes the study quiz. Any one of these values being NULL clearly signals to the app that the user hasn't taken the quiz yet, which is important information.

```
CREATE TABLE users (

    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,

    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    noise NUMERIC,
    sociality NUMERIC,
    crowding NUMERIC,
    size NUMERIC,
    decoration NUMERIC
);

CREATE UNIQUE INDEX username ON users (username);
```

### spots ###

The SQL table spots stores information about each location in the StudySpotter database. The name field stores the display name/title of the spot; description stores a detailed one-paragraph summary of the spot; location stores the spot's address; hours stores the spot's open hours; and noise, sociality, crowding, size, and decoration store the spot's features. The five features directly parallel the user's five study preferences so that the StudySpotter algorithm can compare the two sets of values in order to determine fit.

Each spot also has its own JPG photo in /static/images folder, whose title is simply the spot's unique ID followed by .jpg. I initially had a separate text column in the spots table to store the image path, but I realized that I could make my database and program even more concise by automatically deriving the image path from the spot ID.

Filling in this table with accurate information for twenty real study spots around Harvard required me to do some serious research, sometimes on places I hadn't ever been before! I collected spot recommendations from my friends, visited several sites in real life to take photos, and conducted online research to determine hours, addresses, and relevant details to include in the description column for each spot. In order to make the textual descriptions more vivid and attractive, I provided ChatGPT with some facts about each spot and asked it to write an appealing summary paragraph.

```
CREATE TABLE spots (

    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,

    name TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT NOT NULL,
    hours TEXT NOT NULL,

    noise NUMERIC,
    sociality NUMERIC,
    crowding NUMERIC,
    size NUMERIC,
    decoration NUMERIC
);
```

### fits ###

The SQL table fits stores information that pertains to particular users and to particular spots. Each fit has two foreign keys: the ID of the user and the ID of the spot to which it relates. This table's most salient field is the fits column, which quantifies how well each spot's features agree with each user's preferences.

Maximizing efficiency is important to me, so fit values for every spot in the database are only calculated when the user submits their quiz. If the user changes their preferences by resubmitting the quiz, the fit values are updated to reflect the user's new preferences. Choosing to calculate fit after the user submits the quiz instead of whenever the user views their ranked spots list minimizes the number of times the program needs to perform these calculations.

The note and stars fields store the user's personal opinions about each spot, enabling users to better remember what they liked and didn't like. Since users can view information about each spot before they rate it and/or leave a note, I enabled NULL for these fields. I didn't choose to make notes and stars public when I first created this application, but that is a potential future direction that I could take.

I initially had a separate table called ratings that stored stars and notes for each spot, but I realized that this structural choice was redundant. The existing fits table, given its user_id and spot_id foreign keys, already had the potential to store stars and notes in addition to a single fit value. To streamline queries and data storage, I consolidated ratings and fits. This design choice enabled me to maintain just three tables instead of four.

```
CREATE TABLE fits (

    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,

    user_id INTEGER NOT NULL,
    spot_id INTEGER NOT NULL,

    fit NUMERIC NOT NULL,
    stars INTEGER DEFAULT NULL,
    note TEXT DEFAULT NULL,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (spot_id) REFERENCES spots(id)
);
```

---

## Quiz

To create the quiz, I used Bootstrap and Bootswatch's attractive range input sliders as well as a bit of JavaScript that enabled me to display the selected value of each slider in real time. Since I wanted users to indicate their preferences on a continuous\*\*\* scale from 0.00 to 1.00, I learned how to use range input so that I wouldn't have to rely on the limited options we studied in class (multiple choice buttons, text entry, and drop-down menus).

\*\*\* Okay, fine... the sliders aren't really continuous. Users have two decimal places to work with, which is effectively continuous for the purposes of my application. Any more decimal places would be excessive.

---

## Fit Algorithm

The magical, mysterious StudySpotter fit-determining algorithm is actually quite straightforward! My formula takes inspiration from mean absolute deviation. For each of the five axes (noise, sociality, crowding, size, and decoration), the program finds the absolute difference of the user's preference value and the spot's feature value. These five absolute deviations are then averaged to determine overall anti-fit, which is subtracted from 1 to produce fit. Therefore, fit is guaranteed to be a number between 0% and 100%.

I considered using a formula inspired by mean squared error to give more importance to values that are further away from the user's indicated preferences, but I ultimately decided that mean absolute deviation would produce better recommendations.

---

## Browsing Spots

Once the user takes the quiz, they unlock the ability to browse all spots in the database.

### Spots List

The main way to browse spots is via the spots list, a table of spots ranked by personalized user fit. Each row in the table contains the name of the spot, the fit value as a percentage, an attractive banner-style image of the spot, the user's star rating (if applicable), and a button to view the spot's detailed profile page. Users can easily access this list via the navbar, and they are also automatically redirected there once they submit the quiz.

### Spot Profiles

Since I wanted users to be able to view a more datailed profile page for the spots that interested them, I figured out how to create a dynamically generated HTML page for every spot in the database—complete with a photo and an interface to leave a note and star rating. Figuring out the best way to format this template was a challenge that took some trial and error to overcome, but I ultimately settled on a large banner image front-and-center with some additional information in mobile-friendly columns beneath.

### Random Spots

This route randomly chooses a spot from the database and redirects the user to that spot's profile page.

I chose to add this route to my application for a few different reasons. First, I wanted adventurous users to be able to discover diverse spots that they might otherwise not have known about due to a low calculated fit score. It can be fun and exciting to try out a new study spot that doesn't necessarily align with your stated preferences—maybe you'll realize that you actually like different things than you thought you did! Second, I wanted impulsive users to have the option of diving right into the database at the click of a button without having to scroll through a ranked catalogue and ponder where to go.

---

## Ratings and Notes

The star rating and note system, as described in the [fits section](#fits), helps users keep track of their opinions about spots they've visited.

For a more elegant and less confusing user experience, I combined the rating editor and the note editor into one form that can be submitted all at once. But since the user might want to edit only their note or only their rating (not both), it was important to make the default values for each form field equal to the columns' current values. For the note field in particular, this choice had the added benefit of enabling the user to view their current note in the same place where they would make edits—i.e. the note viewer and the note editor are consolidated.

---

## User Info

### Profile

Users can view their average rating, number of spots rated, and study preferences on their profile page. I thought it was particularly important to display the number of spots that the user has rated to give users a sense of achievement and motivation.

### Login/Logout, Account

Using Werkzeug, I implemented a login/logout system heavily inspired by the one used in Problem Set 9: Finance. Hashing passwords makes for a more secure application than simply storing raw passwords in the SQL users table.

I also implemented an account route to enable users to change their password if desired.

---

## Error Handling

I implemented try-except in the /register route to handle errors that arise when the user attempts to register with a username that is taken.

I implemented server-side validation of form input, since a malicious user could inspect the browser and alter client-side HTML form attributes like minlength, min, and max in order to submit invalid values.

I avoided SQL injection attacks with parameterized queries.

---

## Style

I started with one of Bootswatch's free CSS themes (Sandstone) to create a professional look for my application, customizing certain features like the size of the navbar and the particular fonts available to better match the aesthetic that I had envisioned. I also updated the message flashing function used in Problem Set 9: Finance to take an extra parameter for the message category, and I found a different cat meme online to use in apology messages—an adorable, slightly sad-looking kitten.

I ensured that my application looks good on both desktop screens and mobile devices by making use of Bootstrap's collapsable navbar and stacking columns.

---

## Image Citations

Although I took some of the photos used in this web application myself, many came from the internet. Here are their URLs:

- https://www.harvardmagazine.com/2022/04/h2-harvard-square-blooms-again
- https://www.harvard.edu/about/endowment/
- https://area17.com/work/harvard-university-press
- https://terva-corporation.squarespace.com/portfolio/project-management/godfrey-lowell-cabot-science-library
- https://college.harvard.edu/about/campus/lamont-library-library-cafe-farnsworth-room-poetry-room-and-media-lab
- https://scictr.fas.harvard.edu/galleries/science-center-arcades
- https://news.harvard.edu/gazette/story/2017/12/harvard-students-favorite-spots-to-study-on-campus/
- https://scictr.fas.harvard.edu/about
- https://www.som.com/projects/harvard-university-northwest-science-building/
- https://www.google.com/maps/contrib/112090916623165845958/place/ChIJ3WRSxRB344kRjk2xzcuC55Y/@42.3733053,-71.1190658,17z/data=!4m6!1m5!8m4!1e2!2s112090916623165845958!3m1!1e1?entry=ttu&g_ep=EgoyMDI0MTIwNC4wIKXMDSoASAFQAw%3D%3D
- https://ar.wikipedia.org/wiki/%D9%85%D9%84%D9%81:Annenberg_Hall,_Memorial_Hall,_Harvard.jpg
- https://www.anseradvisory.com/project/smith-campus-center-harvard
- https://www.aiany.org/news/featured-member-melissa-delvecchio-faia/
- https://www.thecrimson.com/flyby/article/2016/11/17/cafe-personality-indicator/
- https://www.thecrimson.com/article/2024/10/18/harvard-law-gaza-study-in/
- https://www.thecrimson.com/article/2023/10/6/currier-new-dining-restrictions/
- https://www.thecrimson.com/article/2024/11/5/lowell-house-dining-hall-fire/
- https://www.hechtarch.com/harvard-biolabs-common-space-cambridge-ma
- https://gsas.harvard.edu/student-center/explore-lehman-hall/garden-level

