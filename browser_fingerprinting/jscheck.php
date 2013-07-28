<?php
# JavaScript response 
#

if (isset($_GET['code'])) {
	if(preg_match("/^[0-9]{3}$/", $_GET['code'])) {
		$code = $_GET['code'];
		$req_code = $code;
	}
}

if (!isset($code)) {
       $code = 200;
       $req_code = "Not Specified (200)";
}

# Set response code
header($_SERVER["SERVER_PROTOCOL"]." $code");

//echo "alert('JavaScript loaded w/ " . $code ."');\n";
echo "var resp_" . $code ." = true;";
?>
