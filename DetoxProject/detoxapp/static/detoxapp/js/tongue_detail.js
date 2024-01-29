var _save_path = "/static/detoxapp/image/tongue_images"

function resetProcess(){
$('.div-progress .circle').eq(0).html('1')
$('.div-progress .circle').eq(1).html('2')
$('.div-progress .circle').eq(2).html('3')
$('.div-progress .circle').eq(3).html('4')
$('.progressbar').css("width", "0%")
$('.div-predict').hide()
$('.div-upload').show()
$("#loading").css("display","none");
}

function DataURIToBlob(dataURI, filename) {
    const splitDataURI = dataURI.split(',')
    const byteString = splitDataURI[0].indexOf('base64') >= 0 ? atob(splitDataURI[1]) : decodeURI(splitDataURI[1])
    const mimeString = splitDataURI[0].split(':')[1].split(';')[0]

    const ia = new Uint8Array(byteString.length)
    for (let i = 0; i < byteString.length; i++)
        ia[i] = byteString.charCodeAt(i)

    return new Blob([ia, filename], { type: mimeString })
}

$(document).ready(function(){
    $('.div-predict').hide()
})

$(document).ready(function(){
    let $drop = document.querySelector(".div-upload");

    $drop.ondrop = (e) => {
        e.preventDefault();

        let file = e.dataTransfer.files[0]
        let filename = file.name
        let question_sq = $('input[name=question_sq]').val()

        const formData = new FormData();
        formData.append('File', file);
        formData.append('question_sq', question_sq);

        html_loading = '<div class="spinner-border text-secondary" style="width: 2rem; height: 2rem;" role="status">'
        html_loading += '<span></span>'
        html_loading += '</div>'
        html_success = '<i class="bi bi-check-lg fs-2 text-success"></i>'
        $.ajax({
            type: 'post',
            url: '/upload_tongue/',
            headers : {'X-CSRFTOKEN' : '{{ csrf_token }}'},
            data: formData,
            contentType: false,
            processData: false,
            enctype: "multipart/form-data",
            success: (data) => {
                console.log('★1STEP 진입 완료:')
                console.log(data)
                if (!data.su) {alert("데이터베이스 연결 실패"); location.reload();}
                else{
                if (data.img_dupl) {
                    flag = confirm("이미 분석했던 사진입니다.\n이전 기록을 덮어씌우겠습니까?")
                    if (!flag) {resetProcess();return false;}
                }
                if ('cur_seq' in data){$('#cur_seq').val(data['cur_seq']);}
                $('.target-img img').attr("src", _save_path + '/' + filename)
                setTimeout(function(){
                  $('.div-progress .circle').eq(0).html(html_success)
                  $('.progressbar').css("width", "33%")
                }, 1000);
                setTimeout(function(){
                  $('.div-progress .circle').eq(1).html(html_loading)
                  Tongue_segment(filename)
                }, 1500);
                }
            },
            beforeSend: function() {
                $("#loading").css("display","");
                $('.div-progress .circle').eq(0).html(html_loading)
                $('.div-predict').show()
                $('.div-upload').hide()
            },
            error: function(request, status, error){
            alert('알 수 없는 에러 발생\ncode:'+request.status+"\n"+"error:"+error);
            resetProcess()
            }
        })
    }
    $drop.ondragover = (e) => {
    e.preventDefault();
    }
})

function Tongue_segment(filename) {
    payload = {
        "filename": filename}

    $.ajax({
        url: "/segment_tongue/",
        type: "POST",
        dataType : "json",
        data: JSON.stringify(payload),
        contentType: "application/json",
        success: function(data) {
            console.log('★2STEP 진입 완료:')
            console.log(data)
            const file = DataURIToBlob(data.file.replace(/["]/g,''))
            const formData = new FormData();
            formData.append('File', file)
            formData.append('file_name', data.seg_filename)
            formData.append('img_seq', $('#cur_seq').val())
            Tongue_segment_upload(formData)
        },
        error: function(request, status, error)
        {
            alert('알 수 없는 에러 발생\ncode:'+request.status+"\n"+"error:"+error);
            resetProcess()
        },
    })
}



function Tongue_segment_upload(formData) {
    $.ajax({
        type: 'post',
        url: '/upload_tongue/',
        headers : {'X-CSRFTOKEN' : '{{ csrf_token }}'},
        data: formData,
        contentType: false,
        processData: false,
        enctype: "multipart/form-data",
        success: (data) => {
            console.log('★3STEP 진입 완료:')
            console.log(data)
            if (!data.su) {alert("데이터베이스 연결 실패"); location.reload();}
            else{
            filename = data.img_path
            setTimeout(function(){
              $('.target-img img').attr("src", _save_path + '/' + filename)
            }, 300);
            setTimeout(function(){
              $('.div-progress .circle').eq(1).html(html_success)
              $('.progressbar').css("width", "66%")
            }, 500);
            setTimeout(function(){
              $('.div-progress .circle').eq(2).html(html_loading)
              Tongue_predict(filename)
            }, 1000);
            }
        },
        beforeSend: function() {
            $("#loading").css("display","");
            $('.div-progress .circle').eq(1).html(html_loading)
            $('.div-predict').show()
            $('.div-upload').hide()
        },
        error: function(request, status, error){
        alert('알 수 없는 에러 발생\ncode:'+request.status+"\n"+"error:"+error);
        resetProcess()
        }
    })
}

function Tongue_predict(filename) {
    payload = {"filename": filename,
    'img_seq': $('#cur_seq').val()}
    console.log(payload)
    $.ajax({
        type: "POST",
        dataType : "JSON",
        contentType: "application/json;",
        url: "/predict_tongue/",
        data: JSON.stringify(payload),

        success: function(data) {
            console.log('★4STEP 진입 완료:')
            console.log(data)
            if (!data.su) {alert("데이터베이스 연결 실패"); location.reload();}
            setTimeout(function(){
                  $('.div-progress .circle').eq(2).html(html_success)
                  $('.progressbar').css("width", "99%")
                  $.each(data.predict_list, function(i, v){
                    // td = $('.table-predict').find('tr:eq('+i+')').children()  
                    td = $('.table-predict').find('div#radio_value:eq('+i+')')
                    td.find('input:radio[value="'+v+'"]').prop('checked', true);
                  })
            }, 1000);
            setTimeout(function(){
              $('.div-progress .circle').eq(3).html(html_loading)
              get_result_info(data.predict_list)
            }, 1500);


        },
        error: function(request, status, error) {
            alert('code:'+request.status+"\n"+"error:"+error)
            resetProcess()
        }
    })
}


function get_result_info(predict_list) {
    console.log(predict_list)
    textarea_str = ""
    for(var i=0; i<15; i++){
        if (i==0){
            if (predict_list[i]==1){
                textarea_str = textarea_str + "담백설로 허로가 예상됩니다.<br>";}
            else if (predict_list[i]==2){
                textarea_str = textarea_str + "홍설로 열증이 예상됩니다.<br>";}
            else if (predict_list[i]==3){
                textarea_str = textarea_str + "강설로 어혈이 예상됩니다.<br>";}
            else if (predict_list[i]==4){
                textarea_str = textarea_str + "자설로 어혈이 예상됩니다.<br>";}}
        else if (i==3){
            if (predict_list[i]==1){
                textarea_str = textarea_str + "어반이 있어 어혈이 예상됩니다.<br>";}}
        else if (i==4){
            if (predict_list[i]==1){
                textarea_str = textarea_str + "치흔이 있어 허로가 예상됩니다.<br>";}}
        else if (i==5){
            if (predict_list[i]==2){
                textarea_str = textarea_str + "대장 영역에 백태가 있어 과민성대장이 예상됩니다.<br>";}
            else if (predict_list[i]==3){
                textarea_str = textarea_str + "대장 영역에 황태가 있어 과민성대장이 예상됩니다.<br>";}}
        else if (i==9){
            if (predict_list[i]==1){
                textarea_str = textarea_str + "심장 영역에 설열이 있어 심장질환이 예상됩니다.<br>";}}
        else if (i==12){
            if (predict_list[i]==1){
                textarea_str = textarea_str + "폐 영역에 설반이 있어 알러지가 예상됩니다.<br>";}}
        else if (i==13){
            if (predict_list[i]==1){
                textarea_str = textarea_str + "설첨 홍이 있어 심장질환이 예상됩니다.<br>";}}
        }
    if (textarea_str.length == 0){
        textarea_str = textarea_str + "이상이 존재하지 않습니다.";}
    setTimeout(function(){
      $('.predict-text').html(textarea_str);
    }, 1000);
    setTimeout(function(){
          $('.div-progress .circle').eq(3).html(html_success)
    }, 1200);
    setTimeout(function(){
      $("#loading").css("display","none");
    }, 1500);
}


// 한의사 진단 후 DB 저장
function label_tongue(){
    let true_result = get_true_result()
    if (true_result.length != 15){
        alert('모든 진단을 완료해주세요.')
        return}

    result = {'true_list': true_result, 'img_seq': $('#cur_seq').val()},
    $.ajax({
        type : 'post',
        url : '/label_tongue/',
        headers : {'X-CSRFTOKEN' : '{{ csrf_token }}'},
        dataType : 'json',
        async : false,
        data : result,
        success : function(data){
            if (!data.su) {alert("데이터베이스 연결 실패"); location.reload();}
            alert('저장이 완료되었습니다.')
            location.href = '/tongue_list/prescription'
            },
        error: function(request, status, error) {
            alert('code:'+request.status+"\n"+"error:"+error)}
    })
}

function get_true_result(){
    var selected_arr = []

    for(var i=0; i<15; i++){
        // td = $('.table-predict').find('tr:eq('+i+')').children()
        td = $('.table-predict').find('div#radio_value:eq('+i+')')
        value = td.find('input:checked').val()
        selected_arr.push(value)
    }
    console.log(selected_arr)
    return selected_arr
}