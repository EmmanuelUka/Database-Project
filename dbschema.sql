create schema euka; --change schema username to yours
use euka;

create table student{
    student_ID varchar(10)
    
}

create table course{
    course_ID varchar(10),
    c_name varchar(25),
    credits numeric(1, 0),
    department_ID varchar(10),

}

create table clasroom{
    b_name varchar(25),
    capacity numeric(c,0),
    room_number varchar(3),

}

create table building {
    department_ID varchar(10),
    b_name varchar(25),
    floor_count numeric(2,0),
    classroom_count numeric(3,0),
    address_building_numer varchar(4),
    address_street varchar(25),
    address_city varchar(25),
    address_state varchar(25),
    address_zip numeric(5,0),
}

create table department{
    d_name varchar(25),
    building_ID varchar(10),
    budget numeric(9,2),
    department_ID varchar(10),
}

create table takes{
    student_ID varchar(10),
    section_ID varchar(10),
    letter varchar(1),
    check (letter in ("A", "B", "C", "D", "F"))
}

create table teaches{
    proffesor_ID varchar(10),
    section_ID varchar(10),
}