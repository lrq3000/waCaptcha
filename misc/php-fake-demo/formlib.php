<?php

function getform($cpath, $solpath, $cid) {
    // Get the URL basepath
    $basepath = 'http://'.$_SERVER["HTTP_HOST"].$_SERVER['REQUEST_URI'];
    // If it's not already a folder, we get the folder name
    if (substr($basepath, -1, 1) !== '/') $basepath = dirname($basepath);
    // Get the images fullpath
    $fullcpath = $basepath.'/'.$cpath.'/'.$cid.'.jpg';
    $fullsolpath = $basepath.'/'.$solpath.'/'.$cid.'.png';
    // Generate a random id to force refresh
    $rid = uniqid();
    // Get the image's size
    $imgsize = getimagesize($fullcpath);
    $width = $imgsize[0];
    $height = $imgsize[1];

    return "


    <style>
      #captcharcanvas {
        background: url('$fullcpath?forcerefresh=$rid');
        display: inline-block;
        overflow: hidden;
        width: ".$width."px;
        height: ".$height."px;
      }
    </style>

    <script type=\"text/javascript\" src=\"kineticjs-custombuild.js?forcerefresh=$rid\"></script>

    <script type='text/javascript'>//<![CDATA[
    window.onload=function(){

        var stage = new Kinetic.Stage({
          container: 'captcharcanvas',
          width: $width,
          height: $height
        });
        var layer = new Kinetic.Layer();

        var base = new Kinetic.Rect({
            x:0,
            y:0,
            width:stage.getWidth(),
            height:stage.getHeight(),
            stroke:0
        });

        var targrect = new Kinetic.Rect({
            x: -3,
            y: -3,
            width: 6,
            height: 6,
            stroke: 'blue',
            strokeWidth: 2
        });

        var targcircle = new Kinetic.Circle({
          x: 0,
          y: 0,
          radius: 20,
          stroke: 'red',
          strokeWidth: 7,
          draggable: true
        });

        var target = new Kinetic.Group({
            draggable: true
        });

        target.add(targrect);
        target.add(targcircle);

        base.on('mousedown tap', function() {
            var mousePos = stage.getMousePosition();
            var x = mousePos.x - target.getX();
            var y = mousePos.y - target.getY();
            layer.clear();
            target.move(x,y);
            layer.draw();
            document.getElementById(\"csol\").value = Math.round(target.getX()) + \":\" + Math.round(target.getY());
        });

        target.on('dragend', function() {
            var mousePos = stage.getMousePosition();
            document.getElementById(\"csol\").value = Math.round(target.getX()) + \":\" + Math.round(target.getY());
        });


        layer.add(base);
        layer.add(target);
        base.moveToTop();
        target.moveToTop();

        stage.add(layer);

    }//]]>
    </script>

    <noscript>
        <input type=\"image\" name=\"nojs_csol\" src='$fullcpath?forcerefresh=$rid' title=\"Click on the reference object to pass the captcha test\" alt=\"Click on the reference object to pass the captcha test\" />
        <input type=\"submit\" style=\"display: none;\" /> <!-- For FireFox, else it will automatically add a submit button even when it's not needed. //-->
        <style>
            /* Hide the javascript captcha image */
            #captcharcanvas {
                background-image: none;
                display: none;
            }
        </style>
    </noscript>
    <div id=\"captcharcanvas\"></div>
    <input type=\"text\" name=\"csol\" id=\"csol\" value=\"NULL\" />
    <input type=\"text\" name=\"cid\" id=\"cid\" value='$cid' />

";

}

function getRandomImage($dirpath) {
    $dictid = array();
    if ($handle = opendir($dirpath)) {

        /* This is the correct way to loop over the directory. */
        while (false !== ($entry = readdir($handle))) {
            $parts = explode('.', $entry);
            if (!empty($parts[0])) $dictid[$parts[0]] = true;
        }

        closedir($handle);
    }

    //print_r($dictid);
    //print count($dictid);
    $dictid = array_keys($dictid);
    return $dictid[mt_rand(0, count($dictid)-1)];
}

?>