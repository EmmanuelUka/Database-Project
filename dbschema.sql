USE euka;

CREATE TABLE building (
    b_name VARCHAR(25) PRIMARY KEY,
    floor_count INT,
    classroom_count INT,
    address_building_number VARCHAR(4),
    address_street VARCHAR(25),
    address_city VARCHAR(25),
    address_state VARCHAR(25),
    address_zip INT
);

CREATE TABLE classroom (
    b_name VARCHAR(25),
    room_number VARCHAR(3),
    capacity INT,
    PRIMARY KEY (b_name, room_number),
    FOREIGN KEY (b_name) REFERENCES building(b_name)
);

CREATE TABLE department (
    department_id VARCHAR(4) PRIMARY KEY,
    d_name VARCHAR(25) NOT NULL,
    b_name VARCHAR(25),
    budget DECIMAL(9,2),
    FOREIGN KEY (b_name) REFERENCES building(b_name)
);

CREATE TABLE course (
    course_id VARCHAR(10) PRIMARY KEY,
    c_name VARCHAR(25) NOT NULL,
    credits INT,
    department_id VARCHAR(4),
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

CREATE TABLE users (
    user_id VARCHAR(10) PRIMARY KEY,
    username VARCHAR(25) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'instructor', 'student') NOT NULL
);

CREATE TABLE professor (
    professor_id VARCHAR(10) PRIMARY KEY,
    p_name VARCHAR(25) NOT NULL,
    dept_id VARCHAR(4),
    salary DECIMAL(8,2),
    email VARCHAR(30),
    address_houseNumber VARCHAR(4),
    address_street VARCHAR(25),
    address_city VARCHAR(25),
    address_state VARCHAR(15),
    address_zip INT,
    FOREIGN KEY (dept_id) REFERENCES department(department_id),
    FOREIGN KEY (professor_id) REFERENCES users(user_id)
);

CREATE TABLE student (
    student_id VARCHAR(10) PRIMARY KEY,
    s_name VARCHAR(25) NOT NULL,
    dept_id VARCHAR(4),
    tot_credits INT,
    gpa DECIMAL(3,2),
    email VARCHAR(30),
    address_houseNumber VARCHAR(4),
    address_street VARCHAR(25),
    address_city VARCHAR(25),
    address_state VARCHAR(15),
    address_zip INT,
    FOREIGN KEY (dept_id) REFERENCES department(department_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id)
);

CREATE TABLE section (
    section_number VARCHAR(10) PRIMARY KEY,
    course_id VARCHAR(10),
    professor_id VARCHAR(10),
    semester VARCHAR(6) CHECK (semester IN ('Fall','Winter','Spring','Summer')),
    year INT CHECK (year > 1701 AND year < 2100),
    room_number VARCHAR(3),
    b_name VARCHAR(25),
    days VARCHAR(2) CHECK (days IN ('M','T','W','Th','F')),
    time VARCHAR(5),
    capacity INT,
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (professor_id) REFERENCES professor(professor_id),
    FOREIGN KEY (b_name, room_number) REFERENCES classroom(b_name, room_number)
);

CREATE TABLE takes (
    student_id VARCHAR(10),
    section_number VARCHAR(10),
    letter VARCHAR(1) CHECK (letter IN ('A','B','C','D','F')),
    course_id VARCHAR(10),
    PRIMARY KEY (student_id, section_number),
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (section_number) REFERENCES section(section_number),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

CREATE TABLE teaches (
    professor_id VARCHAR(10),
    section_number VARCHAR(10),
    course_id VARCHAR(10),
    PRIMARY KEY (professor_id, section_number),
    FOREIGN KEY (professor_id) REFERENCES professor(professor_id),
    FOREIGN KEY (section_number) REFERENCES section(section_number),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);
