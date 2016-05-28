#!/bin/bash
# 
# Create separate dumps for all mysql tables
# !=DONT FORGET create LOGFILE=!
# Needs to install original 'time' util, not a bash function
# Logging functions from http://askel.ru/archives/330
#

# ------------ Variables
# MYSQL connection
HOST="localhost"
USER=""
PASS=""
DATABASE="isp"
CONNECT_OPTIONS="-h $HOST -u $USER --password=$PASS $DATABASE"

# Store options
BACKUPDIR="/mnt/MYSQL"
LOGFILE="/var/log/mariadb/backup.log"
MY_UID=nobody
MY_GID=nobody
DATE_DIR=`date +'%d-%m-%Y'`

# Mail options
# TODO: add mail reports

# ------------- Functions
function now_time() {
    date +"%Y-%m-%d %H:%M:%S"
}

function logging() {
    echo "`now_time` [$1] $2" >> $LOGFILE
}

# --------------- Main
mkdir -p $BACKUPDIR/$DATABASE/$DATE_DIR 2>/dev/null
cd $BACKUPDIR/$DATABASE/$DATE_DIR

logging NFO "Run. Test connection..."

# Test mysql connection
mysql $CONNECT_OPTIONS -e "exit"

if [ $? -ne 0 ]
then
    logging ERROR "Some error in mysql, connect line is $CONNECT_OPTIONS"
    exit -1
fi

logging NFO "Connection success"

# Gets all tables
for table in `mysql $CONNECT_OPTIONS -e "show tables;" | egrep -v "Tables_in"`; do
	logging NFO "Creating dump of table $table"
	mysqldump $CONNECT_OPTIONS $table | gzip -c > "$table.sql.gz"
	if [ $? -ne 0 ]
	then
		logging ERROR "Error create dump of table $table"
	else
		logging NFO "Succsesfully create dump of table $table"
	fi 
done
chown -R $MY_UID:$MY_GID $BACKUPDIR/$DATABASE
logging NFO "Exit"
exit 0
