<?php

include 'dbh.php';

$username = $_POST['username'];
$password = $_POST['password'];
$fbid = $_POST['fbid'];

$key="12345678abcdefgh12345678abcdefgh";

$enc = openssl_encrypt($password, "AES-256-CBC", $key);

$checked_username="Wrong format";
if (ctype_alpha($username)){
	$checked_username=$username;
}

$sql = "INSERT INTO user (fbid,username,password)
		VALUES ('$fbid','$checked_username','$enc')
		ON DUPLICATE KEY UPDATE
		username='$username', password='$enc'";
$result = mysqli_query($conn,$sql);
header("Location: added.php");
?>
