function get_cookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function ajax_post(url,data)
{
    var csrftoken =  get_cookie('csrftoken');
     $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
    $.ajax({
            //提交数据的类型 POST GET
            type:"POST",
            //提交的网址
            url:url,
            //提交的数据
            data:data,
            //返回数据的格式
            datatype: "json",//"xml", "html", "script", "json", "jsonp", "text".
            //在请求之前调用的函数
            //成功返回之后调用的函数
            success:function(data){

             document.getElementById("tbody").innerHTML = data;
            }   ,
            //调用出错执行的函数
            error: function(){
                //请求出错处理
                console.log("wrong");
            }
         });
}
function submitSelect(button)
{
     // var root = document.getElementById("tbody");
     // var selected = new Array();
    //  for(var i=0;i<root.rows.length;i++)
    // {
    //      var sel = root.rows[i].cells[0].firstChild.nextSibling;
    //      if(!sel.disabled && sel.checked )
    //      {
    //          selected.push(sel.id);
    //      }

    //  }
    var t = document.getElementById("have_num_"+button.id)
    var have_num = Number(document.getElementById("have_num_"+button.id).innerHTML);
    var max_num = Number(document.getElementById("max_num_"+button.id).innerHTML);
        console.log(have_num)
    console.log(max_num)
     var isselected = 0;
     var id = button.id;

     if (button.name =="selected"){
        isselected = 1;

    }
     else if (button.name =="noselected")
     {
          if(have_num>max_num){
            alert("不合理输入")
            return
        }
        isselected = 0;
     }


     var url = "/student/select/";
     ajax_post(url,{"isselected":isselected,"id":id});


}

function unSelect(button)
{
     var url = "/student/unselect/";
     ajax_post(url,{"id":button.id});
}


function submitScore(button)
{
     var url = "/teacher/score/";
     var input= document.getElementById("score_"+button.id);

     var score = input.value;
     if( input.disabled){
        input.disabled = false;
        button.innerHTML = "提交";
        return ;
     }
     if(score>0 && score<101){
     ajax_post(url,{"s_id":button.id,"score":score});
     }
     else{
        alert("不合理输入")
     }
}

function editScore(button){
    var input= document.getElementById("score_"+button.id);

}





