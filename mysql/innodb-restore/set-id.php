#!/usr/bin/php
<?php
error_reporting(0);
$dbhost = "localhost";
$dbname = "base";
$dbuser = "root";
$dbpwd  = "";

$count = $argv[1];
$count--;

mysql_connect($dbhost,$dbuser,$dbpwd) or die(mysql_error());

for ($i = 10; $i <= $count; $i++) {
   $dbquery = "CREATE TABLE ips_oncalls.t" . $i . " (id int) ENGINE=InnoDB";
    
      $resu lt = mysql_db_query($dbname,$dbquery) or die(mysql_error());
    
      $j = 0;
    
      while($row = mysql_fetch_array($result)) {
         $j+ +;
         echo $row[0];
      }
}

mysql_close();

?>
