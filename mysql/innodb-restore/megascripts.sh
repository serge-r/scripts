#!/bin/bash

MY_BACKUP="/backup/mysql-backup"
MY_SQL="/var/lib/mysql/some_base"
MY_OLDSQL="/backup/some_base"

while read line
do
    cd /root/scripts
    name=($line)


    ./reset-db.sh
    mysql -u root --password="some_pass" some_base -e "CREATE TABLE ${name[0]} (id INT PRIMARY KEY) ENGINE=Innodb;"
    systemctl stop mariadb
    cp -f $MY_OLDSQL/${name[0]}.frm $MY_SQL/${name[0]}.frm
    chown mysql:mysql $MY_SQL/${name[0]}.frm
    systemctl start mariadb
    echo "waiting..."
    sleep 30 
    echo "Ready to dump structure table ${name[0]} with id ${name[1]}"
    mysqldump --force --no-data -u root --password="some_pass" some_base > table.tmp
    
#    echo "ready to get data"
#    ./reset-db.sh
#    ./set-id.php ${name[1]}
#    mysql -u root --password="" some_base < table.tmp
#    echo "Doing some magic..Disable idb file"
#    mysql -u root --password="" some_base -e "ALTER TABLE ${name[0]} DISCARD TABLESPACE;"
#    echo "Copy new file"
#    cp $MY_OLDSQL/${name[0]}.ibd $MY_SQL/${name[0]}.ibd
#    chown mysql:mysql $MY_SQL/${name[0]}.ibd
#    echo "Enable new file"
#    mysql -u root --password="" some_base -e "ALTER TABLE ${name[0]} IMPORT TABLESPACE;"
#    echo "Checking"
#    mysqlcheck -c -f -r some_base ${name[0]}
#    echo "Dump!"
#    mysqldump --force --compress --triggers --routines --create-options -u root --password="some_pass" some_base ${name[0]} > $MY_BACKUP/${name[0]}.mysql

done < id.txt

    
