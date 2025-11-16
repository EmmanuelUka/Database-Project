USE euka;

DELETE FROM takes;
DELETE FROM teaches;    
DELETE FROM section;
DELETE FROM student;    
DELETE FROM professor;
DELETE FROM course;
DELETE FROM department;
DELETE FROM classroom;
DELETE FROM building;

INSERT INTO building VALUES ('Conner Hall', 4, 25, '120', 'University Ave', 'Kent', 'Ohio', 44240);
INSERT INTO building VALUES ('Taylor Hall', 3, 18, '200', 'Main Street', 'Kent', 'Ohio', 44240);
INSERT INTO building VALUES ('Franklin Hall', 5, 30, '310', 'College Street', 'Kent', 'Ohio', 44240);
INSERT INTO building VALUES ('Johnson Hall', 2, 12, '75', 'Academy Lane', 'Kent', 'Ohio', 44240);
INSERT INTO building VALUES ('Anderson Hall', 4, 20, '460', 'Summit Street', 'Kent', 'Ohio', 44240);

INSERT INTO classroom VALUES ('Conner Hall', '101', 50);
INSERT INTO classroom VALUES ('Taylor Hall', '202', 30);
INSERT INTO classroom VALUES ('Franklin Hall', '303', 40);  
INSERT INTO classroom VALUES ('Johnson Hall', '404', 20);
INSERT INTO classroom VALUES ('Anderson Hall', '505', 35);

INSERT INTO department VALUES ('1001', 'Computer Science', 'Conner Hall', 500000);
INSERT INTO department VALUES ('1002', 'Mathematics', 'Taylor Hall', 420000);
INSERT INTO department VALUES ('1003', 'History', 'Franklin Hall', 380000);
INSERT INTO department VALUES ('1004', 'English', 'Johnson Hall', 310000);
INSERT INTO department VALUES ('1005', 'Life Sciences', 'Anderson Hall', 460000);

INSERT INTO course VALUES ('CS101', 'Introduction to Computer Science', 4, '1001');
INSERT INTO course VALUES ('MATH201', 'Calculus I', 4, '1002');
INSERT INTO course VALUES ('ENG150', 'English Literature', 3, '1003');
INSERT INTO course VALUES ('HIST210', 'World History', 3, '1004');
INSERT INTO course VALUES ('BIO110', 'General Biology', 4, '1005');

-- USERS
INSERT INTO users VALUES ('123456789', 'Zachary', 'pass', 'admin');
INSERT INTO users VALUES ('987654321', 'Emmanuel', 'pass', 'admin');

INSERT INTO users VALUES ('1273892037', 'James Evans', 'pass', 'instructor');
INSERT INTO users VALUES ('2384920183', 'Sarah Thompson', 'pass', 'instructor');
INSERT INTO users VALUES ('3471829401', 'Robert Jenkins', 'pass', 'instructor');
INSERT INTO users VALUES ('4592038174', 'Emily Rivera', 'pass', 'instructor');
INSERT INTO users VALUES ('5610283947', 'Michael Chen', 'pass', 'instructor');

INSERT INTO users VALUES ('9515617924', 'Emmanuel Uka', 'pass', 'student');
INSERT INTO users VALUES ('9515617925', 'Luna Garcia', 'pass', 'student');
INSERT INTO users VALUES ('9515617926', 'Marcus Lee', 'pass', 'student');
INSERT INTO users VALUES ('9515617927', 'Sophia Brown', 'pass', 'student');
INSERT INTO users VALUES ('9515617928', 'Noah Patel', 'pass', 'student');

-- PROFESSORS
INSERT INTO professor VALUES ('1273892037','James Evans','1001',100000,'j.evans@kent.edu','120','county road 12','toledo','ohio',23495);
INSERT INTO professor VALUES ('2384920183','Sarah Thompson','1002',87500,'s.thompson@kent.edu','45','Maple Street','Cleveland','Ohio',44114);
INSERT INTO professor VALUES ('3471829401','Robert Jenkins','1003',94500,'r.jenkins@kent.edu','210','Lakeview Drive','Akron','Ohio',44308);
INSERT INTO professor VALUES ('4592038174','Emily Rivera','1004',91000,'e.rivera@kent.edu','18','Sunset Blvd','Columbus','Ohio',43215);
INSERT INTO professor VALUES ('5610283947','Michael Chen','1005',99000,'m.chen@kent.edu','300','Summit Avenue','Kent','Ohio',44240);

-- STUDENTS
INSERT INTO student VALUES ('9515617924','Emmanuel Uka','1001',12,3.95,'emauka@gmail.com','2000','Monster','Hell','Ohio',12446);
INSERT INTO student VALUES ('9515617925','Luna Garcia','1002',11,3.82,'lgarcia@gmail.com','400','starfall blvd','dreamvale','CA',90210);
INSERT INTO student VALUES ('9515617926','Marcus Lee','1003',10,3.47,'mlee@gmail.com','872','maple street','riverton','TX',75001);
INSERT INTO student VALUES ('9515617927','Sophia Brown','1004',12,4.00,'sbrown@gmail.com','230','elm grove','silverlake','FL',33101);
INSERT INTO student VALUES ('9515617928','Noah Patel','1005',9,3.60,'npatel@gmail.com','678','sunset drive','willowtown','NY',10027);

-- SECTIONS
INSERT INTO section VALUES ('001','CS101','1273892037','Fall',2023,'101','Conner Hall','M','5:00',75);
INSERT INTO section VALUES ('002','MATH201','2384920183','Spring',2024,'202','Taylor Hall','T','11:00',30);
INSERT INTO section VALUES ('003','ENG150','3471829401','Fall',2023,'404','Johnson Hall','F','4:00',65);
INSERT INTO section VALUES ('004','HIST210','4592038174','Spring',2024,'303','Franklin Hall','Th','2:15',110);
INSERT INTO section VALUES ('005','BIO110','5610283947','Fall',2023,'505','Anderson Hall','W','12:30',45);

-- TEACHES
INSERT INTO teaches VALUES ('1273892037','001','CS101');
INSERT INTO teaches VALUES ('2384920183','002','MATH201');
INSERT INTO teaches VALUES ('3471829401','003','ENG150');
INSERT INTO teaches VALUES ('4592038174','004','HIST210');
INSERT INTO teaches VALUES ('5610283947','005','BIO110');

-- TAKES
INSERT INTO takes VALUES ('9515617924','001','A','CS101');
INSERT INTO takes VALUES ('9515617925','002','B','MATH201');
INSERT INTO takes VALUES ('9515617926','003','C','ENG150');
INSERT INTO takes VALUES ('9515617927','004','A','HIST210');
INSERT INTO takes VALUES ('9515617928','005','B','BIO110');
