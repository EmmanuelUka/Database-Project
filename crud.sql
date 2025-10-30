--create professor
insert into professor
values('1273892037', 'James Evans', '1001', 100000, 'j.evans@kent.edu', '120', 'county road 12', 'toledo', 'ohio', 23495 );

--read: all professors
select * from professor;

--read: individual professor
select * from professor where ID ='';

--update: change salary
update professor
set salary = ''
where professor_ID = '';

--delete professor
delete from professor where professor_ID = '';



--create student
insert into student 
values ('9515617924', 'Emmanuel Uka', '12', 3.95, 'emauka@gmail.com', '2000', 'Monster', 'Hell', 'Ohio', '12446');

--read: all students
select * from students

--read: individual professor
select * from professor where student_ID = '';

--update: change GPA
update student
set GPA = ''
where student_ID = '';

--delete student
delete from student where student_ID = '';



--create course
insert into course values('CS101', 'Introduction to Computer Science', '4', '1001');

--read: all courses
select * from courses;

--read: particular course
select * from course where course_ID = '';

--update: change credit amount
update course
set credits = ''
where course_ID = '';

--delect course
delete from course where course_ID = '';



--create teaches
insert into teaches values('1273892037', '001');

--delete takes
delete from teaches where professor_ID = '' and section_number = '';



---create Section
insert into section values('CS101', '1273892037','Fall', '2023', '001', '101', 'M', '5:00', '75');

--read:all sections
select * from section;

--read: all sections of a course
select * from section where course_ID = '';

--update:time
update section
set time = ''
where course_ID = '' and section_ID = '';

--delete section
delete from section where course_ID = '' and section_ID = '';



--create department
insert into department
values('computer science', 'conner hall', 500000, 1001);

--read: all departments
select * from department

--read: particular department
select * from department where department_ID = ''

--update department: change budget
update department 
set budget = 0
where department_ID = ''

--delete department
delete from department where department_ID = '';



--create takes
insert into takes
 values ('9515617924', '001', 'A');

 --delete takes
 delete from takes where student_ID = '' and section_number = ''



 --create building
insert into building 
values ('1001', 'Conner Hall', 4, 25, '120', 'University Ave', 'Kent', 'Ohio', 44240);

--read: all buildings
select * from building

--read: building in a particular department
select * from building where department_ID = '';

--update: change name
update building
set b_name = ''
where b_name = ''

--delete building
delete from building where building_name = '';



--create classroom
insert into classroom
values ('conner hall', '100', '212');

--read: all classrooms 
select * from classroom;

--read: every classroom in a building
select * from classroom where b_name = '';

--update: seat count
update classroom
set capacity = ''
where b_name = '' and room_number = '';

--delete classroom
delete from classroom where b_name = '' and room_number = '';



--enroll in class
insert into takes
values('9515617924', '001', null, 'CS101')



--assign an instructor to a class
insert into teaches
values('1273892037', '001', 'CS101')



--drop a section
delete from takes
where section_number = '001' and course_ID = 'CS101';

delete from teaches
where section_number = '001' and course_ID = 'CS101';

delete from section
where section_number = '001' and course_ID = 'CS101';



--give a grade to a student in a section
update takes
set letter = 'A'
where student_id = '9515617924' 
  and section_number = '001'
  and course_ID = 'cs101';