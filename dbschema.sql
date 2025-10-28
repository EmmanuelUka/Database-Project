create schema euka; --change schema username to yours
use euka;

create table student{
    student_ID          varchar(10),
    s_name              varchar(25),
    dept_ID             varchar(10),
    tot_credits         numeric(2,0),
    GPA                 numeric(1,2),
    email               varchar(30),
    address_houseNumber varchar(4),
    address_street      varchar(25),
    address_city,       varchar(25),
    address_state       varchar(15),
    address_zip         numeric(5,0),
}

create table professor{
    professor_ID        varchar(10),
    p_name              varchar(25),
    dept_ID             varchar(10),
    salary              numeric(6,2),
    email               varchar(30),
    address_houseNumber varchar(4),
    address_street      varchar(25),
    address_city,       varchar(25),
    address_state       varchar(15),
    address_zip         numeric(5,0),
}

create table section{
    section_ID              varchar(10),
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
}

