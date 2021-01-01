// 제작: Syun
// 본 소스를 이용해 생긴 일에 대한 책임은 사용자에게 있습니다.
// 본 소스에는 제작자의 개인정보 보호를 위해 일부 정보가 제거되었습니다.

<?php
include 'key.php';

$params=json_decode(file_get_contents('php://input'))->action->params;
$dt=str_replace('-' , '', json_decode($params->date)->value);

if ($params->mealtime = '중식') {
    $mt='2';
} else {
    $mt='3';
}

$data=preg_replace('/(\d|\.)/i','',str_replace('<br/>','\\n',json_decode(file_get_contents('**** URL ****'))->mealServiceDietInfo[1]->row[0]->DDISH_NM));

if (!isset($data)) {
    $data='급식이 없어요!';
}

$result = [
	'version' => '2.0', 
	'data' => [
		'd'=>'(밥)  '.substr($dt,0,4).'년 '.substr($dt,4,2).'월 '.substr($dt,6).'일\n\n'.$data
	]
];

echo str_replace('\\\\n','\n',json_encode($result,JSON_UNESCAPED_UNICODE))
?>
