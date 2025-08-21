#############################################
# Custom commands for data initialization
#############################################
#database ops for development
./manage.py syncdb

#[NECESSARY]add two groups and related permission for production use
./manage.py initportal

#[OPTIONAL]add upload folders
./manage.py initquestion

#[OPTIONAL]add some test data, currently it's 1 teacher and 1 student data
./manage.py addtestdata

#############################################
# Remove tables with foreign key constraint
#############################################
mysql> SET foreign_key_checks = 0;
Query OK, 0 rows affected (0.00 sec)

mysql> drop table exam_exam;
Query OK, 0 rows affected (0.09 sec)

mysql> SET foreign_key_checks = 1;
Query OK, 0 rows affected (0.00 sec)