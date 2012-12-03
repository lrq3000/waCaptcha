<?php

require_once(dirname(__FILE__).'/captchalib.php');

$resp = captcha_http_get ("localhost:8888", "/captcha/getform", null, 8888);
//$resp = captcha_http_get ("localhost:8888", "/captcha/getform", array("embedImage"=>"True"), 8888);
$form = $resp[1]


?>

<!DOCTYPE HTML>
<html>
  <head>
  <META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
  <META HTTP-EQUIV="EXPIRES" CONTENT="0">
  <META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">
  </head>
  <body>
    <form action="check.php" method="post" enctype="application/x-www-form-urlencoded ">
        <?php echo $form; ?>
        <br />
        <input type="submit" value="Submit" />
    </form>
  </body>
</html>
