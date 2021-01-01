// 제작: Syun
// 본 소스를 이용해 생긴 일에 대한 책임은 사용자에게 있습니다.
// 본 소스에는 제작자의 개인정보 보호를 위해 일부 정보가 제거되었습니다.

<?php
include 'key.php';

$params=json_decode(file_get_contents('php://input'))->action->params;
$classroom=$params->classroom;
$day=$params->day;
$d='';
$data=json_decode(file_get_contents('**** URL ****'))->school->$day;

for ($i=1;$i<=7;$i++) {
    if (!empty($data->$i->sb)) {
        $d=$d.$i.'교시: '.$data->$i->sb.'\n';
    } else {
        $d=$d.$i.'교시: 없음\n';
    }
}


$result = [
	'version' => '2.0', 
	'data' => [
		'd'=>$d
	]
];

echo str_replace('\\\\n','\n',json_encode($result,JSON_UNESCAPED_UNICODE))
?>
