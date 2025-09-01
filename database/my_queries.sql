-- database: c:\Users\farle\Documents\vscode\adamissigma\database\data_source.db

-- Users (students + teachers)
CREATE TABLE users (
    userID      INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    password    TEXT NOT NULL,
    role        TEXT CHECK(role IN ('student', 'teacher')) NOT NULL
);

-- Messages (chat system)
CREATE TABLE messages (
    messageID   INTEGER PRIMARY KEY AUTOINCREMENT,
    senderID    INTEGER NOT NULL,
    channel     TEXT NOT NULL,
    content     TEXT NOT NULL,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (senderID) REFERENCES users(userID)
);

-- Assignments
CREATE TABLE assignments (
    assignmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT NOT NULL,
    description  TEXT,
    dueDate      DATE NOT NULL,
    class        TEXT NOT NULL
);

-- Submissions (links students to assignments)
CREATE TABLE submissions (
    submissionID INTEGER PRIMARY KEY AUTOINCREMENT,
    assignmentID INTEGER NOT NULL,
    studentID    INTEGER NOT NULL,
    fileLink     TEXT NOT NULL,
    submittedAt  DATETIME DEFAULT CURRENT_TIMESTAMP,
    grade        TEXT,
    feedback     TEXT,
    FOREIGN KEY (assignmentID) REFERENCES assignments(assignmentID),
    FOREIGN KEY (studentID) REFERENCES users(userID)
);

-- Timetable (simple version)
CREATE TABLE timetable (
    classID      INTEGER PRIMARY KEY AUTOINCREMENT,
    subject      TEXT NOT NULL,
    teacherID    INTEGER NOT NULL,
    dayOfWeek    TEXT NOT NULL, 
    startTime    TIME NOT NULL,
    endTime      TIME NOT NULL,
    FOREIGN KEY (teacherID) REFERENCES users(userID)
);

CREATE TABLE classes (
    classID     INTEGER PRIMARY KEY AUTOINCREMENT,
    className   TEXT NOT NULL,
    code        TEXT NOT NULL UNIQUE, -- random join code
    teacherID   INTEGER NOT NULL,
    FOREIGN KEY (teacherID) REFERENCES users(userID)
);

-- Enrollments (links students to classes)
CREATE TABLE enrollments (
    enrollmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    classID      INTEGER NOT NULL,
    studentID    INTEGER NOT NULL,
    FOREIGN KEY (classID) REFERENCES classes(classID),
    FOREIGN KEY (studentID) REFERENCES users(userID)
);
