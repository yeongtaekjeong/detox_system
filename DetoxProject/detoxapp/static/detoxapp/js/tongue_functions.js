// 클릭 시 이미지 변경
function changeImage() {
    img_path = document.getElementById("Tongue").src
    img_path = decodeURIComponent(img_path)

    if (img_path.search('noimgicon') != -1){
        document.getElementById("Tongue").src = "/static/decodingapp/image/noimgicon.png";}
    else if (img_path.search('out') == -1){
        document.getElementById("Tongue").src = img_path.slice(0, -4) + "_out.jpg";
        change_image(document.getElementById("Tongue").src);}
    else if (img_path.search('out') != -1){
        document.getElementById("Tongue").src = img_path.slice(0, -8) + ".jpg";
        change_image(document.getElementById("Tongue").src);}
}

function fileCheck(file_path){
    $.ajax({
        url: file_path,
        type: 'HEAD',
        async: false,
        error: function() {
            console.log(file_path);
            if (file_path.search('out') != -1){
                document.getElementById("Tongue").src = file_path.slice(0, -8) + ".jpg";
                change_image(document.getElementById("Tongue").src)
                alert("이미지를 먼저 추출해주세요.")}
            else{
                document.getElementById("Tongue").src = "/static/decodingapp/image/noimgicon.png"
                change_image(document.getElementById("Tongue").src)}},
    })
}

// 데이터에 맞게 radio 박스 체크
function get_predict_result() {
    for(var i=0; i<9; i++){
        $("#p" + i + $("#result_data_predict").val()[i*2]).prop("checked", true)}
}

function get_true_result() {
    for(var i=0; i<9; i++){
        $("#r" + i + $("#result_data_real").val()[i*2]).prop("checked", true)}
}

// 결과 변경
function change_result(r){
    let result = r;

    $.ajax({
        type : 'post', 
        url : '/tongue_change_detail_result_send/', 
        headers : {'X-CSRFTOKEN' : '{{ csrf_token }}'},
        dataType : 'json', 
        data : result,
})}

// 이미지 변경
function change_image(ip){
    let image_path = {'image_path':ip};

    $.ajax({
        type : 'post', 
        url : '/change_current_image/', 
        headers : {'X-CSRFTOKEN' : '{{ csrf_token }}'},
        dataType : 'json', 
        data : image_path,
})}