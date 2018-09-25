<?php
require_once('wp-config.php');
$props = array('nickname', 'first_name', 'last_name', 'gender', 'footloose_student', 'footloose_institution', 'footloose_faculty', 'birth_date', 'phone_number', 'footloose_address', 'footloose_postcode', 'footloose_city', 'footloose_tuemail_verific', 'footloose_fontys_verific', 'footloose_otherinstitution');
if($argv[1] == 'props') {
    $props[] = 'email';
    $props[] = 'roles';
    echo json_encode($props);
    exit(0);
}
$res = array();
$users = array();
if(count($argv) > 1){
    if(strpos($argv[1], '@') !== false) {
        $users = array(get_user_by('email', $argv[1]));
    } else {
        $users = array(get_user_by('login', $argv[1]));
    }
} else {
    $users = get_users();
}
foreach ($users as $user) {
    $data = array();
    foreach ($props as $prop) {
        $data[$prop] = get_user_meta($user->ID, $prop, true);
    }
    $data['gender'] = $data['gender'][0];
    $data['footloose_student'] = $data['footloose_student'][0];
    $data['email'] = $user->data->user_email;
    $data['roles'] = $user->roles;
    $res[] = $data;

}
echo json_encode($res);
?>
