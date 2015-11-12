
/*
window.addEventListener("load", function() {

    var connection = new autobahn.Connection({
        url: 'ws://127.0.0.1:8080/ws',
        realm: 'realm1'
    });

    connection.onopen = function (session) {

        // 1) subscribe to a topic
        function onevent(args) {
            var dict = args[0];
            console.log("args:", args[0]);
        }

        session.subscribe("SocialUserId.", onevent);
    };
    connection.open();
});
*/
_baseUrl = "http://127.0.0.1:8000";


_file_options = {
        url: "",
        data: "",
        type: "POST",
        dataType: "json",
        processData: false, // Don't process the files
        contentType: false // Set content type to false as jQuery will tell the server its a query string request

    };

_text_options = {
        url: "",
        data: "",
        type: "POST",
        dataType: "json"
};

function GetCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}

$(function() {
    _baseUrl = location.origin;
    ImagePreviewPostInputInitialize();
    SetAjaxEvents();
    SetWebSockets();

});
ImagePreviewPostInputInitialize = function()
{
    $(document).on('click', '#close-preview', function(){
        $('.image-preview').popover('hide');
        // Hover befor close the preview
        $('.image-preview').hover(
            function () {
               $('.image-preview').popover('show');
            },
             function () {
               $('.image-preview').popover('hide');
            }
        );
    });
     // Create the close button
    var closebtn = $('<button/>', {
        type:"button",
        text: 'x',
        id: 'close-preview',
        style: 'font-size: initial;',
    });
    closebtn.attr("class","close pull-right");
    // Set the popover default content
    $('.image-preview').popover({
        trigger:'manual',
        html:true,
        title: "<strong>Preview</strong>"+$(closebtn)[0].outerHTML,
        content: "There's no image",
        placement:'bottom'
    });
    // Clear event
    $('.image-preview-clear').click(function(){
        $('.image-preview').attr("data-content","").popover('hide');
        $('.image-preview-filename').val("");
        $('.image-preview-clear').hide();
        $('.image-preview-input input:file').val("");
        $(".image-preview-input-title").text("Browse");
    });
    // Create the preview image
    $(".image-preview-input input:file").change(function (){
        var img = $('<img/>', {
            id: 'dynamic',
            width:250,
            height:200
        });
        var file = this.files[0];
        var reader = new FileReader();
        // Set preview image into the popover data-content
        reader.onload = function (e) {
            $(".image-preview-input-title").text("Change");
            $(".image-preview-clear").show();
            $(".image-preview-filename").val(file.name);
            img.attr('src', e.target.result);
            $(".image-preview").attr("data-content",$(img)[0].outerHTML).popover("show");
        }
        reader.readAsDataURL(file);
    });
}
SetAjaxEvents = function()
{
    $(document).on("click", ".remove_button", function(event){
        var url = _baseUrl+$(this).attr("data-url");
        AjaxCaller(url,"",_text_options,RemoveElement );
    });
    $(document).one("click", ".like_button", function(event){
        var url = _baseUrl+$(this).attr("data-url");
        AjaxCaller(url,"",_text_options,ParseLikeResonse );
    });
    $(document).on("click", ".add_friend", function(event){
        var url = _baseUrl+$(this).attr("data-url");
        AjaxCaller(url,"",_text_options,ManageFriend );
    });
     $(document).on("click", ".upload_comment", function(event){
         post_id = $(this).parents(".post_container").attr("id").split("_")[1];
         console.log($("#comment_text_"+post_id).val())
         var text = $("#comment_text_"+post_id).val()
         if (text != "" && text != undefined)
         {
             var url = _baseUrl+$(this).attr("data-url");
             var post_id = $(this).parents(".post_container").attr("id").split("_")[1];
             var user_id = $("#user_data").attr("data-userId");
             //var data = {"text": comment_text, "image":image_file, "post_id": post_id, "user_id":user_id}
             var form_data = new FormData();
             form_data.append("text", text);
             var image_file = $("#comment_image_"+post_id)[0].files
             if (image_file != undefined)
                form_data.append("image", image_file[0]);
             else
                form_data.append("image", undefined);
             form_data.append("post_id", post_id);
             form_data.append("user_id", user_id);
             form_data.append("csrfmiddlewaretoken",$("input[name='csrfmiddlewaretoken']").val())
             AjaxCaller(url,form_data, _file_options, AddCommentOrPost );
         }
    });
    $(document).on("click", ".upload_post", function(event){
         var text = $("#post_text").val()
         if (text != "" && text != undefined)
         {
             var url = _baseUrl+$(this).parents("form").attr("action");
             var user_id = $("#user_data").attr("data-userId");
             //var data = {"text": comment_text, "image":image_file, "post_id": post_id, "user_id":user_id}
             var form_data = new FormData();
             form_data.append("text", text);
             var image_file = $("#post_upload_input")[0].files
             if (image_file != undefined)
                form_data.append("image", image_file[0]);
             else
                form_data.append("image", undefined);
             form_data.append("csrfmiddlewaretoken",$(this).parents("form").find("input[name='csrfmiddlewaretoken']").val())
             form_data.append("user_id", user_id);
             AjaxCaller(url,form_data,_file_options,AddCommentOrPost );
         }
    });
}
SetWebSockets = function()
{
    var connection = new autobahn.Connection({
        url: 'ws://127.0.0.1:8080/ws',
        realm: 'realm1'
    });

    connection.onopen = function (session) {

        // 1) subscribe to a topic
        console.log("uspjesna konekcija")
        userId = $("#user_data").attr("data-userId");
        session.subscribe("User_"+userId, WebSocketEventParser);
    };
    connection.open();
}
WebSocketEventParser = function(data)
{
    recived_data = data[0];
    console.log(data[0]);
    if (recived_data.event=="like_update")
    {
        view_data = recived_data.data;
        if (view_data.type=="post")
        {
            $("#post_"+view_data.post_id).find(".like_count").text(view_data.like_count);
        }
    }
    else if (recived_data.event=="post_removed")
    {
        view_data = recived_data.data;
        if (view_data.type=="post")
        {
            $("#post_"+view_data.post_id).remove();
        }
        else if (view_data.type=="comment")
        {
            $("#comment_"+view_data.post_id).remove();
        }
    }
    else if (recived_data.event=="post_added")
    {
        view_data = recived_data.data;
        if (view_data.type=="post")
        {
            var allPosts = $("#main_post_container").find(".post_container");
            if(allPosts.length>0)
            {
                allPosts.each(function(index, value)
                {
                    if (parseFloat($(value).attr("data-date-created"))<parseFloat(view_data.date_created_ms) || (index == allPosts.length-1))
                    {
                        //postHtml = GeneratePostHtml(view_data);
                        //$(postHtml).insertBefore(value);

                         $(Templates.post(view_data)).insertBefore(value);

                        return false;
                    }
                })
            }
            else
            {
                $("#main_post_container").append(Templates.post(view_data));
            }

        }
        else if (view_data.type=="comment")
        {
            console.log(view_data)
            var allPosts = $("#main_post_container").find("#post_"+view_data.post_id).find(".comment_all_container").find(".comment_wrapper")
            if (allPosts.length>0)
            {
                allPosts.each(function(index, value)
                {
                    console.log(value)
                    if (parseFloat($(value).attr("data-date-created"))>parseFloat(view_data.date_created_ms) || (index == allPosts.length-1))
                    {

                        //postHtml = GenerateCommentHtml(view_data);
                        //$(postHtml).insertAfter(value);

                        $(Templates.comment(view_data)).insertAfter(value);

                        return false;
                    }
                })
            }
            else
            {
                console.log(view_data);
                $("#main_post_container").find("#post_"+view_data.post_id).find(".comment_all_container").append(Templates.comment(view_data))
            }

        }
    }
}
RemoveElement = function(data)
{
    console.log(data);
    if (data.status=="deleted")
    {
        $(data.id).remove();
    }
}
ParseLikeResonse = function(data)
{
    console.log(data);
    var like_button = $(data.id).find(".like_button");
    if (data.status=="liked")
    {
        like_button.attr("data-url",like_button.attr("data-url").replace("/like/","/unlike/"));
        like_button.addClass("btn-success");
    }
    else if (data.status=="unliked")
    {
        like_button.attr("data-url",like_button.attr("data-url").replace("/unlike/","/like/"));
        like_button.removeClass("btn-success");
    }
    $(document).one("click", ".like_button", function(event){
        var url = _baseUrl+$(this).attr("data-url");
        AjaxCaller(url,"",_text_options,ParseLikeResonse );
    });
}
ManageFriend = function(data)
{
    console.log(data);
    var friend_button = $(data.id).find(".add_friend");
    if (data.status=="friend_added")
    {

        friend_button.attr("data-url",friend_button.attr("data-url").replace("/add/","/remove/"));
        friend_button.addClass("btn-success");
        friend_button.html("Unfriend friend!");
    }
    else if (data.status=="friend_removed")
    {
        friend_button.attr("data-url",friend_button.attr("data-url").replace("/remove/","/add/"));
        friend_button.removeClass("btn-success");
        friend_button.html("Add as friend!");
    }
}
AddCommentOrPost = function (data) {
    console.log(data)
    if (data.status=="post_added")
    {
        $("#post_text").val("");
        $('.image-preview-clear').click();
    }
    else if (data.status=="comment_added")
    {
        $("#comment_text_"+data.id).val("");
        $("#image_upload_wrapper_"+data.id).find(".image-preview-clear").click();
    }
}
AjaxCaller = function(url, data, options, callback)
{
    options.url =url;
    options.data = data;
    options.headers = { 'X-CSRFToken': GetCookie("csrftoken") };
    $.ajax(options)
    .done(function(data) {
      callback(data)
    })
    .fail(function() {
      alert("Ajax failed to fetch data")
    })
}
Templates = {
    post : function(data)
    {
        //_.templateSettings = { interpolate: /\{\{(.+?)\}\}/g }; // da bude teplate sa dvostrukim viticastim kao u djangu
        console.log("popunjavam post");
        var user_id = $("#user_data").attr("data-userId");
        data.user_id = user_id;
        data.csrftoken = GetCookie("csrftoken");
        var template_post = $("#post_template_data").html();
        var template = _.template(template_post );
        var populated_template = template(data);
        console.log(populated_template);
        return populated_template
    },
    comment : function(data)
    {
        //_.templateSettings = { interpolate: /\{\{(.+?)\}\}/g }; // da bude teplate sa dvostrukim viticastim kao u djangu
        console.log("popunjavam comment");
        var user_id = $("#user_data").attr("data-userId");
        data.user_id = user_id;
        data.csrftoken = GetCookie("csrftoken");
        var template_post = $("#comment_template_data").html();
        var template = _.template(template_post );
        var populated_template = template(data);
        console.log(populated_template);
        return populated_template
    }
}

Search = function(ajaxData, timeoutMs )
{
    if (this.liveSearchTimer)
    {
        clearTimeout(this.liveSearchTimer);
    }

    this.liveSearchTimer = setTimeout(function ()
    {
        AjaxCaller(ajaxData.url, ajaxData.data, ajaxData.options, ajaxData.callback);
    }, timeoutMs);
}