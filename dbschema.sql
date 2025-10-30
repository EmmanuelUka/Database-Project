use euka;


create table building (
    b_name varchar(25) primary key,
    floor_count numeric(2,0),
    classroom_count numeric(3,0),
    address_building_number varchar(4),
    address_street varchar(25),
    address_city varchar(25),
    address_state varchar(25),
    address_zip numeric(5,0)
);

create table classroom (
    b_name varchar(25),
    room_number varchar(3),
    capacity varchar(3),
    primary key (b_name, room_number),
    foreign key (b_name) references building(b_name)
);

create table department (
    department_id varchar(4) primary key,
    d_name varchar(25) not null,
    b_name varchar(25),
    budget numeric(9,2),
    foreign key (b_name) references building(b_name)
);

create table course (
    course_id varchar(10) primary key,
    c_name varchar(25) not null,
    credits numeric(1,0),
    department_id varchar(4),
    foreign key (department_id) references department(department_id)
);

create table professor (
    professor_id varchar(10) primary key,
    p_name varchar(25) not null,
    dept_id varchar(4),
    salary numeric(6,2),
    email varchar(30),
    address_houseNumber varchar(4),
    address_street varchar(25),
    address_city varchar(25),
    address_state varchar(15),
    address_zip numeric(5,0),
    foreign key (dept_id) references department(department_id)
);

create table student (
    student_id varchar(10) primary key,
    s_name varchar(25) not null,
    dept_id varchar(4),
    tot_credits numeric(2,0),
    gpa decimal(3,2),
    email varchar(30),
    address_houseNumber varchar(4),
    address_street varchar(25),
    address_city varchar(25),
    address_state varchar(15),
    address_zip numeric(5,0),
    foreign key (dept_id) references department(department_id)
);

create table section (
    section_number varchar(10) primary key,
    course_id varchar(10),
    professor_id varchar(10),
    semester varchar(6) check (semester in ('Fall', 'Winter', 'Spring', 'Summer')),
    year numeric(4,0) check (year > 1701 and year < 2100),
    room_number varchar(3),
    b_name varchar(25),
    days varchar(2) check (days in ('M', 'T', 'W', 'Th', 'F')),
    time varchar(5),
    capacity varchar(3),
    foreign key (course_id) references course(course_id),
    foreign key (professor_id) references professor(professor_id),
    foreign key (b_name, room_number) references classroom(b_name, room_number)
);

create table takes (
    student_id varchar(10),
    section_number varchar(3),
    letter varchar(1) check (letter in ('A', 'B', 'C', 'D', 'F')),
    course_ID varchar(10),
    primary key (student_id, section_number),
    foreign key (student_id) references student(student_id),
    foreign key (section_number) references section(section_number),
    foreign key (course_id) references course(course_id)
);

create table teaches (
    professor_id varchar(10),
    section_number varchar(3),
    course_ID varcvhar(10),
    primary key (professor_id, section_number),
    foreign key (professor_id) references professor(professor_id),
    foreign key (section_number) references section(section_number)
    foreign key (course_id) references course(course_id)
);
