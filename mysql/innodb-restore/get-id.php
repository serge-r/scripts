#!/usr/bin/php
# Found this in Inet
# Dont remember where
<?php

/*
Tested with tables from 4.1.23, 5.0.68, 5.1.28, and 6.0.7.
*/

// Set the filename
$filename = $argv[1];

// Read 2 bytes in at a time
$offset = 2;

// Open the filename - need 'rb' for binary file on Windows
$handle = fopen($filename, "rb");

// Define redundant, local variables for possible later functionality and/or checks
$ibd_id_bin = 0;
$ibd_id_hex = 0;
$ibd_id_dec = 0;
$ibd_id_bin2 = 0;
$ibd_id_hex2 = 0;
$ibd_id_dec2 = 0;

// Find the filesize (note: below command messes up script)
//$filesize = filesize($filename));

// Only loop through first 21 bytes - as table is is in $array[18] and $array[20]
for ($z = 0; $z <= 20; $z++) {
	
	// Set variable $contents equal to 2 ($offset) bytes of binary data
	$contents = fread($handle, $offset);
	
	// Convert $contents from binary data to hex data
	$contents2 = bin2hex($contents);
	
	// Convert $contents2 from hex data to decimal data
	$contents3 = hexdec($contents2);
	
	// If position 19, array position [18], then store the values
	if ($z == 18) {
		$ibd_id_bin = $contents;
		$ibd_id_hex = $contents2;
		$ibd_id_dec = $contents3;
	}
	
	// If position 21, array position [20], then store the values
	if ($z == 20) {
		$ibd_id_bin2 = $contents;
		$ibd_id_hex2 = $contents2;
		$ibd_id_dec2 = $contents3;
	}
}
fclose($handle);

if ($ibd_id_dec == $ibd_id_dec2) {
	echo "$filename " . "\t" . "$ibd_id_dec\n";
} else {
	echo "The values from positions [ 18] and [20] did not match,";
             echo "so please enable debug output, and check for proper positions.";
}

?>
