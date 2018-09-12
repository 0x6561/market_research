<?php
include($_SERVER['DOCUMENT_ROOT'] . '/utils.php');
$page = 'code.html';
$title = '0x6561.net - Python - Market Research';
$body = file_get_contents('popular_tech.html'); 
include($_SERVER['DOCUMENT_ROOT'] . '/template.php');
?>
