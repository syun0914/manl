# -*- coding: utf-8 -*-
# 보안을 위해 일부 정보가 삭제되었습니다.
# Syun 제작

<?php
include 'key.php';

date_default_timezone_set('Asia/Seoul');
$rt=$_SERVER['REQUEST_TIME'];
$a=json_decode(file_get_contents('php://input'))->action->params->covidarea;
$date=date('Ymd');
$bdate=date('Ymd',$rt-86400);
$bbdate=date('Ymd',$rt-172800);

if ($a=='충남') {
	$area='Sido';
} else {
	$area='';
}

function info($dat) {
    $are=$GLOBALS['area'];
	$temp=simplexml_load_string(file_get_contents('**** URL ****'))->body->items[0];
	if ($are=='') {
	    return $temp->item[0];
	} else {
	    return $temp->item[6];
	}
}

function am($k) {
    $k=$k.'Cnt';
    $da=(int)$GLOBALS['d']->$k;
    $gap=$da-(int)$GLOBALS['bd']->$k;
    if ($gap>0) {
        $gap='+'.$gap;
    }
    return number_format($da).'명('.$gap.'명)';
}

$d=info($date);
$bd=info($bdate);
$t=0;
$day='오늘';

if (empty($d->deathCnt)) {
	$d=$bd;
	$bd=info($bbdate);
	$t=86400;
	$day='어제';
}

if ($area=='') {
    $data='누적 확진자: '.am('decide').'\n치료 중: '.am('care').'\n검사 중: '.am('exam').'\n격리 해제: '.am('clear').'\n음성 결과: '.am('resutlNeg').'\n사망 환자: '.am('death');
} else {
    $data='(충남)누적 확진자: '.am('def').'\n격리 중: '.am('isolIng').'\n격리 해제: '.am('isolClear').'\n사망 환자: '.am('death');
}

$result = [
	'version'=>'2.0', 
	'data'=>[
		'd'=>$day.'의 코로나 19 현황('.$a.')\n\n'.$data
	]
];

echo str_replace('\\\\n','\n',json_encode($result));
?>
