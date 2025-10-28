create schema euka; --change schema username to yours
use euka;

create table student{
    student_ID          varchar(10) primary key,
    s_name              varchar(25) not null,
    dept_ID             varchar(10),
    tot_credits         numeric(2,0),
    GPA                 numeric(1,2),
    email               varchar(30),
    address_houseNumber varchar(4),
    address_street      varchar(25),
    address_city,       varchar(25),
    address_state       varchar(15),
    address_zip         numeric(5,0),
    foreign key (dept_ID) references department(department_ID)
}

create table professor{
    professor_ID        varchar(10) primary key,
    p_name              varchar(25) not null,
    dept_ID             varchar(10),
    salary              numeric(6,2),
    email               varchar(30),
    address_houseNumber varchar(4),
    address_street      varchar(25),
    address_city,       varchar(25),
    address_state       varchar(15),
    address_zip         numeric(5,0),
    foreign key (dept_ID) references department(department_ID)
}

create table section{
    section_ID              varchar(10) primary key,
    course_ID               varchar(10),
    professor_ID            varchar(10),
    semester                varchar(6)
		check (semester in ('Fall', 'Winter', 'Spring', 'Summer')), 
    year			numeric(4,0) check (year > 1701 and year < 2100), 
    section_number          varchar(3),
    room_number    varchar(3),
    days           varchar(2)
		check (semester in ('M', 'T', 'W', 'Th', 'F')),
    time          varchar(5),
    capacity varchar(3),
    foreign key (course_ID) references Course(course_ID),
    foreign key (professor_ID) references Professor(professor_ID),
    foreign key (building_ID, room_number) references Classroom(building_ID, room_number)
}

create table course{
    course_ID varchar(10) primary key,
    c_name varchar(25) not null,
    credits numeric(1, 0),
    department_ID varchar(10),
    foreign key (department_ID) references department(department_ID)
}

create table clasroom{
    b_name varchar(25),
    capacity numeric(c,0),
    room_number varchar(3),
    primary key (building_ID, room_number),
    foreign key (building_ID) references building(building_ID)
}

create table building {
    department_ID varchar(10),
    b_name varchar(25) primary key,
    floor_count numeric(2,0),
    classroom_count numeric(3,0),
    address_building_numer varchar(4),
    address_street varchar(25),
    address_city varchar(25),
    address_state varchar(25),
    address_zip numeric(5,0),
}

create table department{
    d_name varchar(25) not null,
    building_ID varchar(10),
    budget numeric(9,2),
    department_ID varchar(10) primary key,
}

create table takes{
    student_ID varchar(10),
    section_ID varchar(10),
    letter varchar(1),
    check (letter in ("A", "B", "C", "D", "F"))
    primary key (student_ID, section_ID),
    foreign key (student_ID) references Student(student_ID),
    foreign key (section_ID) references Section(section_ID)
}

create table teaches{
    proffesor_ID varchar(10),
    section_ID varchar(10),
    primary key (professor_ID, section_ID),
    foreign key (professor_ID) references Professor(professor_ID),
    foreign key (section_ID) references Section(section_ID)
} 