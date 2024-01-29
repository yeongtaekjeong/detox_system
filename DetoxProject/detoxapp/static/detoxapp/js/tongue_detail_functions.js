function tabno(n){
    let postdata = {'no':n};

    $.ajax({
        type : 'post',           // 타입 (get, post, put 등등)
        url : '/tongue_change/',           // 요청할 서버url
        headers : {              // Http header
        'X-CSRFTOKEN' : '{{ csrf_token }}'
        },
        dataType : 'json',       // 데이터 타입 (html, xml, json, text 등등)
        data : postdata,
        success : function(data) { // 결과 성공 콜백함수
        if (data['tabno'] == 3) {
            $('#tab_first').removeClass('active')
            $('#tab_second').removeClass('active')
            $('#tab_third').addClass('active')

            $('#tabcontent_1').hide()
            $('#tabcontent_2').hide()
            $('#tabcontent_3').show()
        }
        else if (data['tabno'] == 2) {
            $('#tab_first').removeClass('active')
            $('#tab_second').addClass('active')
            $('#tab_third').removeClass('active')

            $('#tabcontent_1').hide()
            $('#tabcontent_2').show()
            $('#tabcontent_3').hide()
        }
        else {
            $('#tab_first').addClass('active')
            $('#tab_second').removeClass('active')
            $('#tab_third').removeClass('active')

            $('#tabcontent_1').show()
            $('#tabcontent_2').hide()
            $('#tabcontent_3').hide()
        }
        return ;
        },
        error : function(request, status, error) { // 결과 에러 콜백함수
            console.log(error)
        }
    })
}

$(document).ready(function(){
    $.ajax({
        type : 'post', 
        url : '/tongue_change_detail/', 
        headers : {'X-CSRFTOKEN' : '{{ csrf_token }}'},
        dataType : 'json', 
        success : function(data) { 
            document.getElementById("Tongue").src = data['image_path'],
            console.log(data['image_path'])}
        })
})

$(document).ready(function(){
    $.ajax({
        type : 'post', 
        url : '/tongue_change_detail_result/', 
        headers : {'X-CSRFTOKEN' : '{{ csrf_token }}'},
        dataType : 'json', 
        success : function(data) { 
            $('#result_data_predict').val(data['predict_list'])
            get_predict_result()
            get_result_info()
        }})
})

function get_result_info(){
    var textarea_str = $('#exampleFormControlTextarea1').val()
    for(var i=0; i<9; i++){
        if (i==0){
            if ($("#result_data_predict").val()[i*2]==1){
                textarea_str = textarea_str + "담백설로 허로가 예상됩니다.\n";}
            else if (i==0 && $("#result_data_predict").val()[i*2]==2){
                textarea_str = textarea_str + "홍설로 열증이 예상됩니다.\n";}
            else if (i==0 && $("#result_data_predict").val()[i*2]==2){
                textarea_str = textarea_str + "홍설로 어혈이 예상됩니다.\n";}
            else if (i==0 && $("#result_data_predict").val()[i*2]==2){
                textarea_str = textarea_str + "홍설로 어혈이 예상됩니다.\n";}}
        else if (i==1){
            if ($("#result_data_predict").val()[i*2]==1){
                textarea_str = textarea_str + "어반이 있어 어혈이 예상됩니다.\n";}}
        else if (i==2){
            if ($("#result_data_predict").val()[i*2]==1){
                textarea_str = textarea_str + "치흔이 있어 허로가 예상됩니다.\n";}}
        else if (i==3){
            if ($("#result_data_predict").val()[i*2]==1){
                textarea_str = textarea_str + "심장 영역에 설열이 있어 심장질환이 예상됩니다.\n";}}
        else if (i==4){
            if ($("#result_data_predict").val()[i*2]==2){
                textarea_str = textarea_str + "대장 영역에 백태가 있어 과민성대장이 예상됩니다.\n";}
            else if ($("#result_data_predict").val()[i*2]==3){
                textarea_str = textarea_str + "대장 영역에 황태가 있어 과민성대장이 예상됩니다.\n";}}
        else if (i==7){
            if ($("#result_data_predict").val()[i*2]==1){
                textarea_str = textarea_str + "폐 영역에 설반이 있어 알러지가 예상됩니다.\n";}}
        else if (i==8){
            if ($("#result_data_predict").val()[i*2]==1){
                textarea_str = textarea_str + "심장 영역에 설첨 홍이 있어 심장질환이 예상됩니다.\n";}}
        }
    if (textarea_str.length == 0){
        textarea_str = textarea_str + "이상이 존재하지 않습니다.\n";}
    $('#exampleFormControlTextarea1').html(textarea_str);
}