-- ============================================
-- SQL Commands Extracted from Lab Notebook (Pages 30-32)
-- ============================================

-- Create database and use it
CREATE DATABASE enrollment;
USE enrollment;

-- ============================================
-- Create Table: course
-- ============================================
CREATE TABLE course (
    regno INT PRIMARY KEY,
    cname VARCHAR(30) NOT NULL,
    dept INT NOT NULL
);

-- ============================================
-- Create Table: student
-- ============================================
CREATE TABLE student (
    regno INT PRIMARY KEY,
    name VARCHAR(25) NOT NULL,
    major VARCHAR(25) NOT NULL,
    bdate DATE NOT NULL
);

-- ============================================
-- Create Table: book
-- ============================================
CREATE TABLE book (
    isbn INT,
    booktitle VARCHAR(25) NOT NULL,
    author VARCHAR(25) NOT NULL,
    publisher VARCHAR(25) NOT NULL
);

-- ============================================
-- Create Table: enroll
-- ============================================
CREATE TABLE enroll (
    regno INT,
    course INT,
    dept INT NOT NULL,
    marks INT NOT NULL,
    FOREIGN KEY (regno) REFERENCES student(regno)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (course) REFERENCES course(course)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================
-- Create Table: book_adoption
-- ============================================
CREATE TABLE book_adoption (
    course INT,
    sem INT NOT NULL,
    isbn INT NOT NULL,
    FOREIGN KEY (course) REFERENCES course(course)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (isbn) REFERENCES book(isbn)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================
-- Insert into course
-- ============================================
INSERT INTO course VALUES
('01HF653', 'Student-4', 'Philosophy', '2003-10-12'),
('01HF234', 'Student-5', 'Computer Science', '2001-10-10');

-- ============================================
-- Insert into enroll values
-- ============================================
INSERT INTO enroll VALUES
('01HF235', '001, S', '85'),
('01HF354', '002, 6', '87'),
('01HF354', '002, 3', '95'),
('01HF653', '004, 4', '80'),
('01HF234', '005, 5', '75');

-- ============================================
-- Insert into book values
-- ============================================
INSERT INTO book VALUES
('001', 'DBMS', 'CS'),
('002', 'Structure', 'English'),
('003', 'Philosophy', 'Philosophy'),
('004', 'History', 'Social Science'),
('005', 'Computer Science', 'CS');

-- ============================================
-- Insert into student values
-- ============================================
INSERT INTO student VALUES
('01HF235', 'Student-1', 'CSE', '2001-05-15'),
('01HF354', 'Student-2', 'Literature', '2002-06-10'),
('01HF354', 'Student-3', 'History', '2000-04-04');

-- ============================================
-- Insert into book_adoption values
-- ============================================
INSERT INTO book_adoption VALUES
(123456, 'Spring', 'Pearson'),
('001, S', '1234 76');

-- ============================================
-- Query 1: Add a new textbook to the database and make this
-- textbook be adopted by course for course adopted by two books
-- ============================================
INSERT INTO book VALUES (123476, 'Spring Offer', 'Pearson/Dr. APJ Abdul Kalam');

INSERT INTO book_adoption (course, sem, isbn)
SELECT course, sem, 123476
FROM book_adoption
GROUP BY course, sem
HAVING COUNT(isbn) = 2;

-- ============================================
-- Query 2: Produce a list of textbooks (including course#, book.isbn,
-- book title) in alphabetical order for courses offered by the
-- CS department that use more than two books
-- ============================================
SELECT course.course, book.isbn, book.booktitle
FROM course, book_adoption AS ba, book
WHERE course.course = ba.course
  AND ba.isbn = book.isbn
  AND course.dept = 'CS'
  AND 2 < (
      SELECT COUNT(book_adoption.isbn)
      FROM book_adoption
      WHERE book_adoption.course = course.course
  )
ORDER BY book.booktitle;

-- ============================================
-- Query 3: List any department that has all its adopted
-- books published by a specific publisher
-- ============================================
SELECT course.dept
FROM course, book_adoption, book
WHERE course.course = book_adoption.course
  AND book_adoption.isbn = book.isbn
  AND book.publisher = 'Pearson'
AND NOT EXISTS (
    SELECT book_adoption.isbn
    FROM course AS c, book_adoption
    WHERE c.course = book_adoption.course
      AND c.dept = course.dept
      AND book_adoption.isbn NOT IN (
          SELECT book.isbn
          FROM book
          WHERE book.publisher = 'Pearson'
      )
);

-- ============================================
-- Query 4: List the students who have scored max marks in
-- "DBMS" course
-- ============================================
SELECT student.name
FROM student, enroll, course
WHERE student.regno = enroll.regno
  AND enroll.course = course.course
  AND course.cname = 'DBMS'
  AND enroll.marks = (
      SELECT MAX(e.marks)
      FROM enroll AS e, course AS c1
      WHERE e.course = c1.course
        AND c1.cname = course.cname
  );

-- ============================================
-- Query 5: Create a view to display all the courses opted by
-- a student along with marks obtained
-- ============================================
CREATE VIEW courseopted_by_student AS
SELECT course.cname, enroll.marks
FROM course, enroll
WHERE course.course = enroll.course;

-- Select from the view
SELECT c.cname, c.marks
FROM courseopted_by_student AS c
WHERE c.course = '01HF235';

-- ============================================
-- Additional selects
-- ============================================
SELECT c.course, c.marks
FROM courseopted_by_student AS c;
