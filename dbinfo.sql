delete from student;
delete from professor;
delete from section;
delete from course;
delete from classroom;    
delete from building;
delete from department;
delete from takes;
delete from teaches;

-----Professor Data Inserts-----
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

------Student Data Inserts-----
insert into student 
values ('9515617924', 'Emmanuel Uka', '12', 3.95, 'emauka@gmail.com', '2000', 'Monster', 'Hell', 'Ohio', '12446');

insert into student 
values ('9515617925', 'luna garcia', '11', 3.82, 'lgarcia@gmail.com', '400', 'starfall blvd', 'dreamvale', 'ca', '90210');

insert into student 
values ('9515617926', 'marcus lee', '10', 3.47, 'mlee@gmail.com', '872', 'maple street', 'riverton', 'tx', '75001');

insert into student 
values ('9515617927', 'sophia brown', '12', 4.00, 'sbrown@gmail.com', '230', 'elm grove', 'silverlake', 'fl', '33101');

insert into student 
values ('9515617928', 'noah patel', '9', 3.60, 'npatel@gmail.com', '678', 'sunset drive', 'willowtown', 'ny', '10027');

------Course Data Inserts-----
insert into course values('CS101', 'Introduction to Computer Science', '4', '1001');
insert into course values('MATH201', 'Calculus I', '4', '1002');
insert into course values('ENG150', 'English Literature', '3', '1003');
insert into course values('HIST210', 'World History', '3', '1004');
insert into course values('BIO110', 'General Biology', '4', '1005');

------Department Data Inserts-----
insert into classroom values ('Engineering Hall', '150', 'E101');
insert into classroom values ('Math Center', '100', 'M202');
insert into classroom values ('Humanities Building', '80', 'H303');
insert into classroom values ('English Hall', '120', 'E404');
insert into classroom values ('Life Science Center', '200', 'S505');

-------Teaches Data Inserts-----
insert into teaches values('1273892037', 'CS101');
insert into teaches values('2384920183', 'MATH201');
insert into teaches values('3471829401', 'ENG150'); 
insert into teaches values('4592038174', 'HIST210');
insert into teaches values('5610283947', 'BIO110');

-------Section Data Inserts-----
insert into section values('CS101', '1273892037','Fall', '2023', '001', 'E101');
insert into section values('MATH201', '2384920183','Spring', '2024','002', 'M202');
insert into section values('ENG150','3471829401','Fall', '2023','001', 'E404');    
insert into section values('HIST210','4592038174','Spring', '2024','002', 'H303');
insert into section values('BIO110','5610283947','Fall', '2023','001', 'S505');

