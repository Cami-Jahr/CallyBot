<?php

include 'dbh.php';

$username = $_POST['username'];
$password = $_POST['password'];

echo passthru("python ilearn_scrape.py $username $password");
#$sql = "INSERT INTO user (username,password)
#		VALUES ('$username','$password')";
