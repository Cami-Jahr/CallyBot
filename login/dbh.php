<?php

$conn = mysqli_connect("mysql.stud.ntnu.no", "halvorkm", "kimjong", "halvorkm_CallyTEST");
if(!$conn){
	die("Connection failed: ".mysqli_connect_error()); #Remove error or be prone to injections!!!! Only for testing
}
