<?php

function checkPixel($solpath, $cid, $x, $y) {
    $fh = fopen($solpath.'/'.$cid.'.rle', 'r');
    $headers = fgets($fh);
    //print($headers);
    list($id, $dir, $size, $maxcol, $hlen) = explode(' ',$headers);
    list($height, $width) = explode('x',$size);

    fseek($fh, 0, 0);

    fseek($fh, $hlen + $maxcol * $y, 0);
    $row = fgets($fh);

    if ($x < 0 or $y < 0 or $x > $width or $y > $height) {
            print("Pixel position outside range: $x $y");
            return false;
    }

    preg_match_all('/0{0,}(\d+)([a-zA-Z]+)/i', $row, $m, PREG_SET_ORDER);

    $lastpos = 0; // relative pointer to know our absolute position in the row
    foreach($m as $match) {
        $xrange = (int)$match[1];
        $color = $match[2];

        if ($lastpos <= $x and $x <= ($xrange+$lastpos) ) {
            if ( !strcmp($color,'W') ) {
                return true;
            } else {
                return false;
            }
        } else {
            $lastpos += $xrange;
        }
    }

    return false;

}

?>