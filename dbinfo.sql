delete from classroom;



--create proffessor
insert into professor
values('1273892037', 'James Evans', '1001', 100000, 'j.evans@kent.edu', '120', 'county road 12', 'toledo', 'ohio', 23495 );

INSERT INTO professor
VALUES ('2384920183', 'Sarah Thompson', '1002', 87500, 's.thompson@kent.edu', '45', 'Maple Street', 'Cleveland', 'Ohio', 44114);

INSERT INTO professor
VALUES ('3471829401', 'Robert Jenkins', '1003', 94500, 'r.jenkins@kent.edu', '210', 'Lakeview Drive', 'Akron', 'Ohio', 44308);

INSERT INTO professor
VALUES ('4592038174', 'Emily Rivera', '1004', 91000, 'e.rivera@kent.edu', '18', 'Sunset Blvd', 'Columbus', 'Ohio', 43215);

INSERT INTO professor
VALUES ('5610283947', 'Michael Chen', '1005', 99000, 'm.chen@kent.edu', '300', 'Summit Avenue', 'Kent', 'Ohio', 44240);

--delete proffessor
delete from proffessor where professor_ID = '';

--create department
insert into department
values('computer science', 'conner hall', 500000, 1001);

insert into department
VALUES ('Mathematics', 'Taylor Hall', 420000, 1002);

insert into department
VALUES ('Physics', 'Franklin Hall', 380000, 1003);

insert into department
VALUES ('English', 'Johnson Hall', 310000, 1004);

insert into department
VALUES ('Psychology', 'Anderson Hall', 460000, 1005);

--delete department
delete from department where department_ID = '';

--create takes
insert into takes
 values ('9515617924', '001', 'A');
insert into takes
 values ('9515617925', '002', 'B');
insert into takes
 values ('9515617926', '003', 'C');
insert into takes
 values ('9515617927', '001', 'A');
insert into takes
 values ('9515617928', '004', 'B');

 --delete takes
 delete from takes where student_ID = '' & section_number = ''

 --create building
insert into building 
values ('1001', 'Conner Hall', 4, 25, '120', 'University Ave', 'Kent', 'Ohio', 44240);

insert into building 
values ('1002', 'Taylor Hall', 3, 18, '200', 'Main Street', 'Kent', 'Ohio', 44240);

insert into building 
values ('1003', 'Franklin Hall', 5, 30, '310', 'College Street', 'Kent', 'Ohio', 44240);

insert into building 
values ('1004', 'Johnson Hall', 2, 12, '75', 'Academy Lane', 'Kent', 'Ohio', 44240);

insert into building 
values ('1005', 'Anderson Hall', 4, 20, '460', 'Summit Street', 'Kent', 'Ohio', 44240);

--delete building
delete from building where building_name = '';