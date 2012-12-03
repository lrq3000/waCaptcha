<?php
/**
 * Encodes the given data into a query string format
 * @param $data - array of string elements to be encoded
 * @return string - encoded request
 */
function captcha_qsencode ($data) {
        $req = "";
        foreach ( $data as $key => $value )
                $req .= $key . '=' . urlencode( stripslashes($value) ) . '&';

        // Cut the last '&'
        $req=substr($req,0,strlen($req)-1);
        return $req;
}



/**
 * Submits an HTTP POST to a reCAPTCHA server
 * @param string $host
 * @param string $path
 * @param array $data
 * @param int port
 * @return array response
 */
function captcha_http_post($host, $path, $data, $port = 8888) {

        if (!empty($data)) {
            $req = captcha_qsencode ($data);
        } else {
            $req = null;
        }

        $http_request  = "POST $path HTTP/1.1\r\n";
        $http_request .= "Host: $host\r\n";
        $http_request .= "Content-Type: application/x-www-form-urlencoded;\r\n";
        if (!empty($req)) $http_request .= "Content-Length: " . strlen($req) . "\r\n";
        $http_request .= "User-Agent: CAPTCHA/PHP\r\n";
        $http_request .= "Connection: Close\r\n";
        $http_request .= "\r\n";
        if (!empty($req)) $http_request .= $req;

        $response = '';
        if( false == ( $fs = @fsockopen($host, $port, $errno, $errstr, 10) ) ) {
            print("$errno: $errstr");
            die ('Could not open socket');
        }

        stream_set_timeout ( $fs , 3 );

        fwrite($fs, $http_request);

        while (!feof($fs)) {
            $response .= fgets($fs, 1160); // One TCP-IP packet
        }

        fclose($fs);
        $response = explode("\r\n\r\n", $response, 2);

        return $response;
}

function captcha_http_get($host, $path, $data, $port = 8888) {

        if (!empty($data)) {
            $req = "?".captcha_qsencode ($data);
        } else {
            $req = '';
        }

        $http_request  = "GET $path$req HTTP/1.1\r\n";
        $http_request .= "Host: $host\r\n";
        $http_request .= "User-Agent: CAPTCHA/PHP\r\n";
        $http_request .= "Connection: Close\r\n";
        $http_request .= "\r\n";

        $response = '';
        if( false == ( $fs = @fsockopen($host, $port, $errno, $errstr, 10) ) ) {
            print("$errno: $errstr");
            die ('Could not open socket');
        }

        stream_set_timeout ( $fs , 3 );

        fwrite($fs, $http_request);

        while (!feof($fs)) {
            $response .= fgets($fs, 128);
        }

        fclose($fs);
        $response = explode("\r\n\r\n", $response, 2);

        return $response;
}
?>