use euka;
delete from takes;
delete from teaches;    
delete from section;
delete from student;    
delete from professor;
delete from course;
delete from department;
delete from classroom;
delete from building;

insert into building values ('Conner Hall', 4, 25, '120', 'University Ave', 'Kent', 'Ohio', 44240);
insert into building values ('Taylor Hall', 3, 18, '200', 'Main Street', 'Kent', 'Ohio', 44240);
insert into building values ('Franklin Hall', 5, 30, '310', 'College Street', 'Kent', 'Ohio', 44240);
insert into building values ('Johnson Hall', 2, 12, '75', 'Academy Lane', 'Kent', 'Ohio', 44240);
insert into building values ('Anderson Hall', 4, 20, '460', 'Summit Street', 'Kent', 'Ohio', 44240);


insert into classroom values ('Conner Hall', '101', 50);
insert into classroom values ('Taylor Hall', '202', 30);
insert into classroom values ('Franklin Hall', '303', 40);  
insert into classroom values ('Johnson Hall', '404', 20);
insert into classroom values ('Anderson Hall', '505', 35);


insert into department values('computer science', 'conner hall', 500000, 1001);
insert into department values ('Mathematics', 'Taylor Hall', 420000, 1002);
insert into department values ('History', 'Franklin Hall', 380000, 1003);
insert into department values ('English', 'Johnson Hall', 310000, 1004);
insert into department values ('Life Sciences', 'Anderson Hall', 460000, 1005);


insert into course values('CS101', 'Introduction to Computer Science', '4', '1001');
insert into course values('MATH201', 'Calculus I', '4', '1002');
insert into course values('ENG150', 'English Literature', '3', '1003');
insert into course values('HIST210', 'World History', '3', '1004');
insert into course values('BIO110', 'General Biology', '4', '1005');


insert into professor values('1273892037', 'James Evans', '1001', 100000, 'j.evans@kent.edu', '120', 'county road 12', 'toledo', 'ohio', 23495 );
insert into professor values ('2384920183', 'Sarah Thompson', '1002', 87500, 's.thompson@kent.edu', '45', 'Maple Street', 'Cleveland', 'Ohio', 44114);
insert into professor values ('3471829401', 'Robert Jenkins', '1003', 94500, 'r.jenkins@kent.edu', '210', 'Lakeview Drive', 'Akron', 'Ohio', 44308);
insert into professor values ('4592038174', 'Emily Rivera', '1004', 91000, 'e.rivera@kent.edu', '18', 'Sunset Blvd', 'Columbus', 'Ohio', 43215);
insert into professor values ('5610283947', 'Michael Chen', '1005', 99000, 'm.chen@kent.edu', '300', 'Summit Avenue', 'Kent', 'Ohio', 44240);


insert into student values ('9515617924', 'Emmanuel Uka', '12', 3.95, 'emauka@gmail.com', '2000', 'Monster', 'Hell', 'Ohio', '12446');
insert into student values ('9515617925', 'luna garcia', '11', 3.82, 'lgarcia@gmail.com', '400', 'starfall blvd', 'dreamvale', 'ca', '90210');
insert into student  values ('9515617926', 'marcus lee', '10', 3.47, 'mlee@gmail.com', '872', 'maple street', 'riverton', 'tx', '75001');
insert into student values ('9515617927', 'sophia brown', '12', 4.00, 'sbrown@gmail.com', '230', 'elm grove', 'silverlake', 'fl', '33101');
insert into student  values ('9515617928', 'noah patel', '9', 3.60, 'npatel@gmail.com', '678', 'sunset drive', 'willowtown', 'ny', '10027');


insert into section values('CS101', '1273892037','Fall', '2023', '001', '101', 'M', '5:00', '75');
insert into section values('MATH201', '2384920183','Spring', '2024','002', '202', 'T', '11:00', '30');
insert into section values('ENG150','3471829401','Fall', '2023','003', '404', 'F', '4:00', '65');    
insert into section values('HIST210','4592038174','Spring', '2024','004', '303', 'Th', '2:15', '110');
insert into section values('BIO110','5610283947','Fall', '2023','005', '505', 'W', '12:30', '45');


insert into teaches values('1273892037', '001');
insert into teaches values('2384920183', '002');
insert into teaches values('3471829401', '003'); 
insert into teaches values('4592038174', '004');
insert into teaches values('5610283947', '005');


insert into takes values ('9515617924', '001', 'A');
insert into takes values ('9515617925', '002', 'B');
insert into takes values ('9515617926', '003', 'C');
insert into takes values ('9515617927', '004', 'A');
insert into takes values ('9515617928', '005', 'B');