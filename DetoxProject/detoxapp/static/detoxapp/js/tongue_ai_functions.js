var save_path = "/static/decodingapp/image/tongue_images"

$(document).ready(function(){
    let $drop = document.querySelector(".mb-3");

    $drop.ondrop = (e) => {
        e.preventDefault();
    
        let file = e.dataTransfer.files[0]
        let filename = file.name
    
        const formData = new FormData();
        formData.append('uploadFile', file);
    
        $.ajax({
            type: 'post',
            url: '/upload_tongue/',
            headers : {'X-CSRFTOKEN' : '{{ csrf_token }}'},
            data: formData,
            contentType: false,
            processData: false,
            enctype: "multipart/form-data",
            success: () => {
                console.log(filename)
                alert("이미지 저장이 완료되었습니다.")
                document.getElementById("Tongue").src = "/static/decodingapp/image/tongue_images/" + filename
                change_image(document.getElementById("Tongue").src)
            }
        })
    }
    $drop.ondragover = (e) => {e.preventDefault();}
})

$('ducument').ready(function(){
    $('#tabcontent_2').hide()})
    
    function tabno(n){
        let postdata = {'no':n};

        $.ajax({
            type : 'post',           // 타입 (get, post, put 등등)
            url : '/tongue_change/',           // 요청할 서버url
            headers : {              // Http header
            'X-CSRFTOKEN' : '{{ csrf_token }}'},
            dataType : 'json',       // 데이터 타입 (html, xml, json, text 등등)
            data : postdata,
            success : function(data) { // 결과 성공 콜백함수
            if (data['tabno'] == 2) {
                $('#tab_first').removeClass('active')
                $('#tab_second').addClass('active')
    
                $('#tabcontent_1').hide()
                $('#tabcontent_2').show()
            }
            else {
                $('#tab_second').removeClass('active')
                $('#tab_first').addClass('active')
    
                $('#tabcontent_2').hide()
                $('#tabcontent_1').show()
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
            $("#true_info").text(data['true']),
            $("#pred_info").text(data['true'])
        }})
})

////////////////// 모델 ////////////////////////
// 이미지 분할 모델
function Tongue_segment() {
    img_path = document.getElementById("Tongue").src
    img_path = decodeURIComponent(img_path)
    console.log(img_path)

    if (img_path.search('noimgicon') != -1){
        alert("이미지를 먼저 삽입해주세요.");
        return;}
    else if (img_path.search('out') != -1){
        alert("이미 추출된 이미지입니다.");
        return;}

    payload = {
        "image_path": img_path,
        "save_path": save_path}
    
    $.ajax({
        type: "POST",
        dataType : "JSON",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/Tongue_Project/Segment_Tongue",
        data: JSON.stringify(payload),
        
        success: function(data) {
            $("#loading").empty()
            alert('Segment Complete')
            out_path = data['output_path']
            document.getElementById("Tongue").src = out_path,
            change_image(document.getElementById("Tongue").src)},
        error: function(request, status, error) {alert('code:'+request.status+"\n"+"error:"+error)},
        beforeSend:function(){
    
            $("#loading").append("<span style='color:red; font-weight:bold'>로딩중입니다.....</span>");
    
        }
    })
}

// 이미지 분류 모델
function Tongue_predict() {
    img_path = document.getElementById("Tongue").src
    img_path = decodeURIComponent(img_path)

    if (img_path.search('noimgicon') != -1){
        alert("이미지를 먼저 삽입해주세요.");
        return;}
    else if (img_path.search('out') == -1){
        alert("이미지를 먼저 추출하세요.");
        return;}

    payload = {
        "image_path": img_path,
        "save_path": save_path}

    $.ajax({
        type: "POST",
        dataType : "JSON",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/Tongue_Project/Predict_Tongue",
        data: JSON.stringify(payload),

        success: function(data) {
            alert('Predict Complete')
            change_result(data)
            $('#result_data_predict').val(data['predict_list'])
            $('#result_data_real').val(data['true_list'])
            console.log(data)
            get_true_result()
            get_predict_result()

        },
        error: function(request, status, error) {
            alert('code:'+request.status+"\n"+"error:"+error)}
    })
}

