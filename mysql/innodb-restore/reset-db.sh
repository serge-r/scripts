#!/bin/bash

systemctl stop mariadb
rm -rf /var/lib/mysql/base
rm -f /var/lib/mysql/ib*

systemctl start mariadb
sleep 2
mysql -u root --password="" -e "CREATE DATABASE base CHARACTER SET utf8 COLLATE utf8_general_ci;"
