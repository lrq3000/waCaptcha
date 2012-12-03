<?php
session_start();
if (!empty($_GET['option'])) {
    $_SESSION['option'] = $_GET['option'];
}

$options = array(
                                't1' => 'Default - 4 objects, 320x240, model+name',
                                't2' => 'More objects - 10 objects, 320x240, model+name',
                                't3' => 'Bigger resolution - 4 objects, 800x600, model+name',
                                't4' => 'Harder mode - 4 objects, 320x240, model only',
                                't5' => 'Hardest mode - 4 objects, 320x240, name only',
                            );

$cpath = 'solmasks'.$_SESSION['option'];
$solpath = $cpath;

if (!strcmp($_SESSION['option'], 't3')) {
    $width = 800;
    $height = 600;
} else {
    $width = 320;
    $height = 240;
}

/****************************/

include(dirname(__FILE__).'/formlib.php');
include(dirname(__FILE__).'/rlereaderlib.php');

if (!empty($_POST['cid'])) $cid = $_POST['cid']; else $cid = '';
if (!empty($_POST['csol'])) $csol = $_POST['csol']; else $csol = '';
if (!empty($_POST['nojs_csol_x'])) $nojs_csol_x = $_POST['nojs_csol_x']; else $nojs_csol_x = '';
if (!empty($_POST['nojs_csol_y'])) $nojs_csol_y = $_POST['nojs_csol_y']; else $nojs_csol_y = '';

if (!empty($cid)) {
    if (!empty($csol) and strcmp($csol, 'NULL')) {
        list($x,$y) = explode(':', $csol);
    } else {
        $x = $nojs_csol_x;
        $y = $nojs_csol_y;
    }

    if (checkPixel($solpath, $cid, $x, $y)) {
        $cresult = '<span style="font-weight: bold; color: darkgreen;">VALID: Captcha is CORRECT!</span>';
    } else {
        $cresult = '<span style="font-weight: bold; color: red;">INVALID: Captcha is incorrect...</span>';
    }
}

$cid = getRandomImage($cpath);

$form = getform($cpath, $solpath, $cid, $width, $height);

?>

<!DOCTYPE HTML>
<html>
  <head>
  <META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
  <META HTTP-EQUIV="EXPIRES" CONTENT="0">
  <META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">
    <script>
    function showHide(shID) {
	if (document.getElementById(shID)) {
		if (document.getElementById(shID).style.display == 'block') {
			document.getElementById(shID).style.display = 'none';
		}
		else {
			document.getElementById(shID).style.display = 'block';
		}
	}
    }
    </script>
    <style>
    #solutionmask {
        display: none;
    }
    </style>
  </head>
  <body>
    <h1>waCaptcha (3D captcha) simulation demo</h1>
    <p>Please note that this is <strong>not an actual demo of the captcha</strong>, the images are already pregenerated instead of generated on-the-fly and there's no security for the access of solution masks.<br /><br />The real implementation has securities and a lot of parameters that can be customized, and captcha images can be generated on-the-fly and requested via a REST web api.<br /></p>
    <?php if (isset($cresult)) echo $cresult; ?>
    <form action="#" method="get" name="optionsform" id="optionsform">
        <select name="option" onchange="form.submit()">
            <?php

            foreach ($options as $key=>$value) {
                if (!strcmp($key,$_SESSION['option'])) {
                    $selected = 'selected="selected"';
                } else {
                    $selected = '';
                }
                echo '<option value="'.$key.'" '.$selected.'>'.$value.'</option>';
            }
            ?>
        </select>
        <input type="submit" value="OK" />
        <input type="checkbox" name="showsolutionmask" value="true" onclick="showHide('solutionmask');">Show solution mask
    </form>
    <form action="#" method="post" enctype="application/x-www-form-urlencoded" name="captchaform" id="captchaform">
        <?php echo $form; ?>
        <br />
        <img id="solutionmask" src="<?php echo $solpath.'/'.$cid.'.png'; ?>" />
        <br />
        <input type="submit" value="Submit" />
    </form>
    <hr />
    <p>Description: This captcha is very alike the Where's Waldo game: you get a reference object (placed randomly at the right or left of the image), and you must find it inside the other image. The software ensures that there's always a minimum clickable area for the solution, and that it is also not too big. Colours and placement are totally randomized. The reference model is unique in the scene, there cannot be a duplicate. The form use Javascript if available, but if not the form is totally HTML compliant so you can just disable Javascript and keep validating captchas.<br /></p>
  </body>
</html>
