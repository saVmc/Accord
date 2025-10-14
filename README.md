# Accord – A Social Networking App for Students

- [disclaimer](PLSREADME.md): citing used online resources 

## Table of Contents!

- [Part 1 – Project Definition and Requirements](#part-1--project-definition-and-requirements)
- [Part 2 – Design and Wireframes](#part-2--design-and-wireframes)
- [Part 3 – Alternative Design and User Flow](#part-3--alternative-design-and-user-flow)
- [Part 4 – Designing algorithms](#part-4---designing-algorithms)
- [Part 5 – Setting up for the joys of SQL](#part-5--setting-up-for-the-joys-of-sql)


---

## Part 1 – Project Definition and Requirements

### Project Overview

Accord is a cross-platform social networking and productivity app designed specifically for students, schools, and educational institutions. It is inspired by the best of both Google Classroom and Discord, merging instant messaging, assignment submission, and time management into one single, mega-intuitive interface.

Accord helps students communicate, collaborate, and stay organized—all within a secure and moderated environment tailored to meet the needs of education in 2025. Through its real-time messaging system, students can easily engage in class discussions, form study groups and calls, and share ideas freely, while teachers are still in control over message visibility and moderation.

---

### Functional Requirements
- **User Authentication**
  - Secure login and signup  
  - Role-based access (Student [with sub roles] / Teacher )
- **Messaging**
  - Real-time chat channels per class or subject  
  - Teacher moderation and message controls
- **Assignments**
  - Student file submissions  
  - Teacher viewing, feedback, and marking
- **Timetable**
  - Dynamic school-provided schedule  
  - Offline access to cached timetable
- **Profile & Settings**
  - Avatar upload, theme choice, notification preferences
- **Notifications**
  - Alerts for new messages, deadlines, and timetable changes

---

### Non-Functional Requirements
- **Interface** – Clean, minimal layout; consistent colour scheme (navy blue, grey, white accents); responsive on mobile, tablet, desktop.  
- **Performance** – Fast loading, smooth screen changes, fast messaging.  
- **Security** – Encrypted login/data, sensible permissions.  
- **Accessibility** – Adjustable text size, high-contrast mode, theme colour changes.  
- **Reliability** – Stable performance, offline access to timetable and past assignments.  
- **Scalability** – Handles multiple schools and hundreds of users.

---

### Scope (what I really want to work)
- Login & roles  
- Class-based real-time messaging  
- Assignment submission + marking  
- View-only timetable with updates  
- Profile basics (avatar, theme, notifications)  

### Out of Scope (what would be sick but aint no way)
- Voice/video calls  
- AI assistant??
- Parent/guardian portals for things like permission notes etc

### Developer Notes

Hi 👋
My commits are incredibly inconsistent. I just forget....
You have been warned........
---

## Part 2 – Design and Wireframes

![screenshot](media/accordfigma1.png)

**Key Annotations:**
- **Navigation** – Bottom bar with Chat, Timetable, Assignments, for super-friendly mobile use  
- **Timetable** – Timetable list > nice colours and organised
- **Login Page** – Simple options > clean buttons

---

### Visual Design Choices
| Element        | Choice                                | Reason |
|----------------|---------------------------------------|--------|
| Primary Colour | Navy (#0A1F44)                        | Professional, doesn't hurt to look at |
| Secondary      | White (#FFFFFF)                 | Looks great against navy |
| Accent         | Green (#1DB954)                        | helps to draw attention to active items |
| Font           | Inter (Headings & Body)                | Clean, modern |
| Icons          | Nice line icons             | Simplicity and consistency |

---

## Part 3 – Alternative Design and User Flow

### Alternate Design (Figma :o )
![User Flow – Alternative](media/accordfigma-alt.png)

**Changes in Alt Design:**
- Beige background for softer look  
- Maroon accent colour instead of blue  
- Serif headings (Cormorant Garamond) for a different style, feels fancier and more academic  
- Intergrated navigation bar instead of bottom bar  

---

### Updated Design
| Element     | Choice              |
|-------------|---------------------|
| Logo        | Fancier “A” mark with text   |
| Secondary   | Just fancier A           |
| Palette     | Maroon, Beige, White, Black |
| Typography  | Verdana (UI), Cormorant Garamond (Headings) |

---

## Part 4 - Designing algorithms

### Feature im trying to figure out
**Login & Role-Based Access!** (Student/Teacher)

---

### Simple Algorithm for this 
1. User opens login screen  
2. Enter email + password  
3. Check email format  
   - Invalid > error message > stop  
4. Search database for email  
   - Not found > error message > stop  
5. Compare entered password (encrypted) with stored encrypted password  
   - No match > error message > stop  
6. If match > start session and check role:  
   - Teacher > Teacher Home/Dashboard  
   - Student > Student Home
  


  **Flow Chart:**  
  ![Login Flowchart](media/login_flowchart.png)


**Complexity:**  
Might be fast enough for like a couple users? the system stops early on invalid details and only checks one account at a time though, not very efficient or 

### Test Cases :D
based off of my test feature

### Test Cases (updated 22/09/2025 with results)

| Test Case ID | Test Case Name              | Preconditions | Test Steps | Expected Result | Actual Result | Pass/Fail | Priority |
|--------------|-----------------------------|---------------|------------|-----------------|---------------|-----------|----------|
| TC-1 | Correct Login (Student) | Student account exists in DB; correct email/password are known | 1. Open login page<br>2. Enter valid student email and correct password<br>3. Click "Login" | Student is logged in and redirected to Student Home | If credentials present in DB, saved as active user and directs to Student Login page | Pass | High |
| TC-2 | Wrong Password (Teacher) | Teacher account exists in DB; correct email known, incorrect password will be entered | 1. Open login page<br>2. Enter valid teacher email and incorrect password<br>3. Click "Login" | Error: “Incorrect password” is displayed; login fails | Error banner pops up, stating credentials aren't present in database. Doesn't allow login. | Pass | High |
| TC-3 | Invalid Email Format | None (rejected before even looked in the DB) | 1. Open login page<br>2. Enter `teacher@@school.com` and any password<br>3. Click "Login" | Error: “Invalid email format” is displayed | Doesn't allow input, only valid email formats are allowed to be submitted in the box, with warning appearing if incorrect. | Pass | Medium |
| TC-4 | Email Not Found | Email isnt in DB | 1. Open login page<br>2. Enter `newuser@school.com` and any password<br>3. Click "Login" | Error: “Account not found” is displayed | Error banner pops up, stating credentials aren't present in database. Doesn't allow login. | Pass | Medium |


---



## Part 5 – Setting up for the joys of SQL

### 1 – Student submissions
```sql
SELECT u.name AS student,
       a.title AS assignment,
       s.grade,
       s.feedback
FROM submissions s
JOIN users u ON s.studentID = u.userID
JOIN assignments a ON s.assignmentID = a.assignmentID
ORDER BY u.name;
```

---

### 2 - Finding all ungraded assignments
```sql
SELECT u.name AS student,
       a.title AS assignment,
       s.fileLink,
       s.grade
FROM submissions s
JOIN users u ON s.studentID = u.userID
JOIN assignments a ON s.assignmentID = a.assignmentID
WHERE s.grade IS NULL
ORDER BY a.dueDate;
```

---

### 3 – Show all users
```sql
SELECT userID, name, email, role
FROM users
ORDER BY role, name;
```

---

### 4 – Show all messages in a specific channel
```sql
SELECT messageID, senderID, content, timestamp
FROM messages
WHERE channel = 'math10a'
ORDER BY timestamp DESC;
```

---

### 5 – Show the timetable
```sql
SELECT subject, dayOfWeek, startTime, endTime, teacherID
FROM timetable
ORDER BY dayOfWeek, startTime;
```


## COMPLETE CSS OVERHAUL GAME PLAN! pre holidays
Lighthouse report before CSS + holidays (dashboard)
| Performance | Accessibility | SEO | Best Practice |
|-------------|---------------|-----|---------------|
|      98       |       100        |  100   |     100          |
---

Lighthouse report after CSS + after holidays
| Performance | Accessibility | SEO | Best Practice |
|-------------|---------------|-----|---------------|
|       97      |       98        |   91  |     100          |

Advice from Lighthouse, post holidays
- Requests are blocking the page's initial render, which may delay LCP. Deferring or inlining can move these network requests out of the critical path. (font)
- Reducing the download time of images can improve the perceived load time of the page and LCP.
- Avoid chaining critical requests by reducing the length of chains, reducing the download size of resources, or deferring the download of unnecessary resources to improve page load.  
-Your first network request is the most important. Reduce its latency by avoiding redirects, ensuring a fast server response, and enabling text compression. (apply compression mostly)

- Properly ordered headings that do not skip levels convey the semantic structure of the page, making it easier to navigate and understand when using assistive technologies.
- Meta descriptions may be included in search results to concisely summarize page content.

I think CSS is like very very very important in a website so I'm going to try to prioritise it :)
Here are some notes on what I like in a good UI and what I've found online to try include 
### Things I REALLY LIKE (and want to add)
- Apple's liquid glass (glassmorphism?) from IOS26 + clean semi transparent layers
  - 20px blur ish + transparency
- Cool animations like pop ups, fades, slides stuff like that BUT SMOOOTHHH
- Animated card underline (thanks internet :D)
  ```
  .class-card::after {
  height: 3px;
  background: linear-gradient(90deg, var(--primary) 0%, transparent 100%);
  transform: scaleX(0);
  transition: transform var(--transition-bounce);
  }
  ```

- Nice rounded corners make everything look good always
- Very reactive everything CSS, like cursor reaction such as pop ups
  - Glows, outlines, transforms, all within a consistent colour scheme
- NICE CENTERED ELEMENTS, CLEAR PADDING and nice margins
- Minamilstic symbols, svgs from W3
- Pretty colours, gradients? Colour pallete make GLOBAL!!
- Gradients in the text, moving maybe if its not too distracting
- Cool animated background
  - Found out you can do this very easy! courtesy of codepen v

```
body::before {
  background: radial-gradient(circle at 20% 50%, rgba(20, 230, 221, 0.03) 0%, transparent 50%);
  animation: float 20s ease-in-out infinite; /* this specifically!!!! */
}
```

- ANIMATION DELAY !! key to making it look good and clean apparently

```
.grid > * {
  animation-delay: calc(var(--item-index, 0) * 0.1s);
}
```

  - ALSO...  animation **curves** for super clean

  ```
  --transition-bounce: 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  ```

  - And directional animations as well

  ```
  .class-card::after {
  transform: scaleX(0);
  transform-origin: left;
  }
  ```

  
- Nice semantic color usage (success, danger, warning)
- Dark mode, but not too dark? Like clean consistent blue dark, like midnight dark

- Custom scrollbar??!

- Primary: Cyan (`#14E6DD`) - Modern, electric almost 
- Dark: Navy (`#0a1929`) - Professional, much easier on eyes than any other colour


- USE SYMBOLS IN PLACE OF TEXT for simplicity!
  - W3 free assets/icons https://www.w3.org/2000/svg


- LOAAADDD up ur transitions to make them compound
  ```
  transform: translateY(#x) scale(#) rotate(#deg); /* Like this 
  ```



## Weekly logs



## Known Bugs (pre submission to fix by final)
- Database lock errors when editing class 
- Random CSS inconsitencies and visual bugs 
- Button overlaps and incorrect hover animations
