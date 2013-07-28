<?php
// JavaScript response 
//

$code = 200;

# Set response code
header($_SERVER["SERVER_PROTOCOL"]." $code");

echo "
var text_205 = '<h2>Internet Explorer Detected</h2><p><img src=\'/img/ie.png\' height=100 width=100></p><p>Using the status code 205 it was possible to detect IE as the browser in use</p>';
var text_300 = '<h2>Firefox Detected</h2><p><img src=\'/img/ff.png\' height=100 width=100><p>Using the lack of status code 300 support it was possible to detect FF as the browser in use</p>';
var text_307 = '<h2>Chrome Detected</h2><p><img src=\'/img/chrome.jpg\' height=100 width=100><p>Using the status code 307 it was possible to detect Chrome as the browser in use</p>';
";

// echo "alert('Fingerprint Handler Loaded');\n";

echo "
if (typeof resp_205 != 'undefined') {
        //alert('Internet Explorer Browser detected via 205 status code check');
	document.getElementById('placeholder').innerHTML = text_205;
}";

echo "
if (typeof resp_300 === 'undefined') {
        //alert('Firefox Browser detected via 300 status code check (negative)');
	document.getElementById('placeholder').innerHTML = text_300;
}";

echo "
if (typeof resp_307 != 'undefined') {
        //alert('Chrome Browser detected via 307 status code check');
	document.getElementById('placeholder').innerHTML = text_307;
}";


?>
