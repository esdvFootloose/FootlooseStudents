<?php
require_once('wp-config.php');
$res = wp_authenticate($argv[1], $argv[2]);
if(is_a($res, "WP_Error"))
{
    echo strip_tags($res->get_error_message());
}
else
{
    #echo json_encode(array_keys($res->get_role_caps()));
    $data = array(
        "username" => $res->data->user_login,
        "email" => $res->data->user_email,
        "roles" => $res->roles
    );
    echo json_encode($data);
}

?>
