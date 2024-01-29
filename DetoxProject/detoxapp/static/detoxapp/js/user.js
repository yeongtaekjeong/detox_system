
$(document).ready(function() {
    var csrftoken = $("input[name=csrfmiddlewaretoken]").val();

    $.ajaxSetup({
        headers: { "X-CSRFToken": csrftoken }
    });
})


$(document).on("click", "button[name='addGroup']", function () {
    groupname = $("input[name='groupname'").val()
    if (groupname.length > 20) {
        alert("권한명은 20자를 초과할 수 없습니다.")
        $("input[name='groupname'").focus()
        return;
    }
    if (!groupname) {
        alert("권한명을 입력해주세요.")
        $("input[name='groupname'").focus()
        return;
    }
    $("#addGroupForm").submit()
})


$(document).on("click", "button[name='deleteUser']", function () {
    if(confirm("정말 삭제합니까?") != true) return;
    pwd = $(this).parent().parent().children('.password')
    if (!pwd.val()) {
    alert('해당 계정의 삭제를 위해서, 패스워드 확인이 필요합니다.\n패스워드를 입력해주세요.');
        pwd.val("")
        pwd.focus()
        return;
    }
    id = $(this).parent().parent().parent().parent().attr('id')
    $("#Check").val(id)
    $("#CheckPwd").val(pwd.val())
    $("#form").submit()
})

$(document).on("click", "a[name='deleteGroup']", function () {
    if(confirm("정말 삭제합니까?\n해당 권한을 가진 사용자는 모두 비활성화 됩니다.") != true) return;
    id = $(this).parent().parent().attr('id')
    $("#groupid").val(id)
    $("#groupForm").submit()
})

$(document).on("change", ".permission_switch", function () {
    permission = $(this).val()
    id = $(this).parent().parent().parent().attr('id')
    if (id == '1' && permission == 'view_user') {
    alert("관리자의 '계정관리' 권한은 변경할 수 없습니다.")
    $(this).prop("checked", true);
    return;
    }
    var block_ele = $('.GroupList').closest('.card');
    postData = { "id": id, "permission": permission }

    $.ajax({
        url: '/changeGroupPermissionAjax/',
        type: 'POST',
        data: JSON.stringify(postData),
        dataType : 'JSON',
        contentType: "application/json",
        success: function(data) {
            if (data.statusCode == 404) location.href = '/alert?msg='+data.msg+'&link='+data.link
        },
        error: function(request, status, error){
            alert('code:'+request.status+"\n"+"error:"+error);
        }
    })
});

$(document).on("change", ".user_active_switch", function () {
    id = $(this).parent().parent().parent().attr('id')
    if (id == '1') {
    alert("admin 계정의 상태는 변경할 수 없습니다.")
    $(this).prop("checked", true);
    return;
    }
    var block_ele = $('.UserList').closest('.card');
    postData = { "id": id, }

    $.ajax({
        url: '/changeAuthActiveAjax/',
        type: 'POST',
        data: JSON.stringify(postData),
        dataType : 'JSON',
        contentType: "application/json",
        success: function(data) {
            if (data.statusCode == 404) location.href = '/alert?msg='+data.msg+'&link='+data.link
            alert(data.msg);
            location.replace('/user')
            if (data.su == 0) { location.replace('/user') }
        },
        error: function(request, status, error){
            alert('code:'+request.status+"\n"+"error:"+error);
        }
    })
});


$(document).on("change", ".user_groups", function () {
    td = $(this).parent()
    id = $(this).parent().parent().attr('id')
    if (id == '1') {
    alert("admin 계정의 권한은 변경할 수 없습니다.")
    $(this).val("1").prop("selected", true);
    return;
    }
    groupid = $(this).children("option:selected").val()
    var block_ele = $('.UserList').closest('.card');
    postData = { "id": id, "groupid": groupid }

    $.ajax({
        url: '/changeAuthGroupAjax/',
        type: 'POST',
        data: JSON.stringify(postData),
        dataType : 'JSON',
        contentType: "application/json",
        success: function(data) {
            if (data.statusCode == 404) location.href = '/alert?msg='+data.msg+'&link='+data.link
            alert(data.msg);
            location.replace('/user')
            if (data.su == 0) { location.replace('/user') }
            else {
                $("#curr").html('※ '+data.curr+' 기준')
                //td.children("div").html(data.groupname)
                //td.parent().children("td").eq(0).html(data.groupname)
            }
        },
        error: function(request, status, error){
            alert('code:'+request.status+"\n"+"error:"+error);
        }
    })
});