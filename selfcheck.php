// 제작: Syun
// 본 소스를 이용해 생긴 일에 대한 책임은 사용자에게 있습니다.
// 본 소스에는 제작자의 개인정보 보호를 위해 일부 정보가 제거되었습니다.

<?php
include 'key.php';

$params=json_decode(file_get_contents('php://input'))->action->params;
$name = $params->name;
$birth=substr(str_replace('-' , '', json_decode($params->birth)->value),2);;
$pw = $params->pw;

$url = file_get_contents('**** URL ****');

if (isset(json_decode($url)->registerDtm)) {
    $success='성공';
} else {
    $success='실패';
}

$result = [
	'version' => '2.0', 
	'data' => [
		'd'=>$success
	]
];

echo json_encode($result,JSON_UNESCAPED_UNICODE);
?>
