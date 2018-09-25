<?php
require_once('wp-config.php');

$subs = Ninja_Forms()->form($argv[1])->get_subs();
$data = array();
foreach($subs as $sub)
{
    $d = $sub->get_field_values();
   $d_clean = array();
    foreach($d as $key => $value)
    {
       if($key[0] == '_' || $key == 'calculations')
        {
            continue;
        }
        if(strpos($key, "student") !== false) {
            $key = "student";            
        }elseif(strpos($key, "course_admission_policy") !== false) {
            $key = "policy";
        }elseif(strpos($key, "dance_partner") !== false) {
            $key = "partner";
        }else {
            $tokens = explode("_", $key);
            array_pop($tokens);
            $key = join('_', $tokens);
        }
        $d_clean[$key] = $value;
    }
    $data[] = $d_clean;
}
echo json_encode($data);
?>
