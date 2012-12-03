<?php

require_once(dirname(__FILE__).'/captchalib.php');

if (!empty($_POST['cid'])) $cid = $_POST['cid']; else $cid = '';
if (!empty($_POST['csol'])) $csol = $_POST['csol']; else $csol = '';
if (!empty($_POST['nojs_csol_x'])) $nojs_csol_x = $_POST['nojs_csol_x']; else $nojs_csol_x = '';
if (!empty($_POST['nojs_csol_y'])) $nojs_csol_y = $_POST['nojs_csol_y']; else $nojs_csol_y = '';

// print_r($_POST)

$response = captcha_http_post ("localhost:8888", "/captcha/postresponse",
                                          array (
                                                 'cid' => $cid,
                                                 'csol' => $csol,
                                                 'nojs_csol_x' => $nojs_csol_x,
                                                 'nojs_csol_y' => $nojs_csol_y,
                                                 ),
                                          null,
                                          8888
                                          );

if ($response[1] == 'OK') {
    $check = 'YES, you are HUMAN';
} else {
    $check = 'NO GET AWAY BOT';
}

print $check;

?>