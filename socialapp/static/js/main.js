
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
        dataType: "json"
};
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

$(function() {
    _baseUrl = location.origin;
    ImagePreviewPostInputInitialize();
    SetAjaxEvents();
    SetWebSockets();

});
ImagePreviewPostInputInitialize = function()
{
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
             form_data.append("csrfmiddlewaretoken",$(this).parents("form").find("input[name='csrfmiddlewaretoken']").val())
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
            if($("#main_post_container").find(".post_container").length>0)
            {
                $("#main_post_container").find(".post_container").each(function(index, value)
                {
                    if (parseFloat($(value).attr("data-date-created"))<parseFloat(view_data.date_created_ms))
                    {
                        postHtml = GeneratePostHtml(view_data);
                        $(postHtml).insertBefore(value);
                        return false;
                    }
                })
            }
            else
            {
                $("#main_post_container").append(GeneratePostHtml(view_data));
            }

        }
        else if (view_data.type=="comment")
        {
            console.log(view_data)
            allPosts = $("#main_post_container").find("#post_"+view_data.post_id).find(".comment_all_container").find(".comment_wrapper")
            if (allPosts.length>0)
            {
                allPosts.each(function(index, value)
                {
                    console.log(value)
                    if (parseFloat($(value).attr("data-date-created"))>parseFloat(view_data.date_created_ms) || (index == allPosts.length-1))
                    {
                        postHtml = GenerateCommentHtml(view_data);
                        $(postHtml).insertAfter(value);
                        return false;
                    }
                })
            }
            else
            {
                console.log(view_data);
                $("#main_post_container").find("#post_"+view_data.post_id).find(".comment_all_container").append(GenerateCommentHtml(view_data))
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
    else if (data.status=="uploaded_comment")
    {

    }
}
AjaxCaller = function(url, data, options, callback)
{
    options.url =url;
    options.data = data;
    $.ajax(options)
    .done(function(data) {
      callback(data)
    })
    .fail(function() {
      alert("Ajax failed to fetch data")
    })
}
GeneratePostHtml = function(data)
{
    var return_html = '<div class="row post_container" id="post_'+data.id+'" data-date-created="'+data.date_created+'">'+
                    '<div class="col-xs-12 col-md-8 col-md-offset-2 col-sm-10 col-sm-offset-1">'+
                        '<div class="img-rounded panel panel-info">'+
                            '<div class="text-left panel-heading">'+
                                '<p class="visible-xs-inline-block visible-sm-inline-block visible-md-inline-block visible-lg-inline-block">'+data.creator_username+': </p>'+
                                '<p class="visible-xs-inline-block visible-sm-inline-block visible-md-inline-block visible-lg-inline-block">'+data.text+'</p>';

                            if (data.creator_id == $("#user_data").attr("data-userId"))
                            {
                                return_html += '<div class="btn btn-default pull-right margin-left-5px remove_button" data-url="/remove/post/'+data.id+'">'+
                                    '<span class="glyphicon glyphicon-remove-circle"></span>'+
                                    '<span>Remove</span>'+
                                '</div>';
                            }

                                return_html += '<div class="btn btn-default pull-right margin-left-5px like_button" data-url="/like/post/'+data.id+'">'+
                                    '<span class="glyphicon glyphicon-thumbs-up"></span>'+
                                    '<span>Like</span>'+
                                '</div>'+
                                '<div class="visible-xs-inline-block visible-sm-inline-block visible-md-inline-block visible-lg-inline-block pull-right margin-left-5px like_count">0</div>'+
                            '</div>';
                            if (data.image_url != "")
                            {
                                return_html += '<div class="panel-body">'+
                                    '<a href="'+data.image_url+'" class="thumbnail">'+
                                        '<img src="'+data.image_url+'" alt="'+data.image_url+'" class="img-responsive img-rounded">'+
                                    '</a>'+
                                 '</div>';
                            }
                            return_html += '<div class="panel-footer ">'+
                                '<p  class="visible-xs-inline-block visible-sm-inline-block visible-md-inline-block visible-lg-inline-block">&nbsp</p>'+
                                '<div class="btn btn-default pull-right" data-toggle="collapse" data-target="#comment_wrapper_'+data.id+'">'+
                                    '<span class="glyphicon glyphicon-comment"></span>'+
                                    '<span>Comment!</span>'+
                                '</div>'+
                                '<div class="row collapse" id="comment_wrapper_'+data.id+'">'+
                                    '<form method="post" class="form-horizontal" enctype="multipart/form-data">'+
                                        '<div class="row">'+
                                            '<div class="col-xs-12 col-md-8 col-md-offset-2 col-sm-10 col-sm-offset-1">'+
                                                '<div class="input-group">'+
                                                    '<input id="comment_text_'+data.id+'" name="comment_text" class="form-control" placeholder="" type="text" required>'+
                                                    '<span class="input-group-btn">'+
                                                        '<div class="btn btn-default image-select-upload" data-toggle="collapse" data-target="#image_upload_wrapper_'+data.id+'">'+
                                                            '<span class="glyphicon glyphicon-picture"></span>'+
                                                            '<span class="image-select">Add Image!</span>'+
                                                        '</div>'+
                                                        '<div class="btn btn-default upload_comment" data-url="/send/comment/">'+
                                                            '<span class="glyphicon glyphicon-upload"></span>'+
                                                            '<span>Post It!</span>'+
                                                        '</div>'+
                                                    '</span>'+
                                                '</div>'+
                                            '</div>'+
                                        '</div>'+
                                        '<div class="row">'+
                                            '<div id="image_upload_wrapper_'+data.id+'" class="col-xs-12 col-md-8 col-md-offset-2 col-sm-10 col-sm-offset-1 collapse">'+
                                                '<div class="input-group image-preview">'+
                                                    '<input type="text" class="form-control image-preview-filename" disabled="disabled">'+
                                                    '<span class="input-group-btn">'+
                                                        '<button type="button" class="btn btn-default image-preview-clear" style="display:none;">'+
                                                            '<span class="glyphicon glyphicon-remove"></span> Clear'+
                                                        '</button>'+
                                                        '<div class="btn btn-default image-preview-input">'+
                                                            '<span class="glyphicon glyphicon-folder-open"></span>'+
                                                            '<span class="image-preview-input-title">Browse</span>'+
                                                            '<input id="comment_image_'+data.id+'" type="file" accept="image/png, image/jpeg, image/gif" name=""/>'+
                                                        '</div>'+
                                                    '</span>'+
                                                '</div>'+
                                            '</div>'+
                                        '</div>'+
                                    '</form>'+
                                '</div>'+
                            '</div>'+
                        '</div>'+
                    '</div>'+
                '</div>';
    return return_html;
}
GenerateCommentHtml = function(data)
{
    var return_html = '<article class="row comment_wrapper" data-date-created="'+data.date_created_ms+'">'
                        if (data.creator_id == $("#user_data").attr("data-userId"))
                            return_html += '<div class="col-md-2 col-sm-2 hidden-xs ">'
                        else
                            return_html += '<div class="col-md-2 col-sm-2 hidden-xs pull-right">'
                        return_html += '<figure class="thumbnail">'+
                                '<img class="img-responsive" src="'+data.creator_image +'" />'+
                                '<figcaption class="text-center">'+data.creator_username +'</figcaption>'+
                              '</figure>'+
                            '</div>'+
                            '<div class="col-xs-12 col-sm-10">'+
                              '<div class="panel panel-default arrow left">'+
                                '<div class="panel-body">'+
                                  '<header class="text-left">'+
                                    '<div class="comment-user pull-left"><i class="fa fa-user"></i> '+data.creator_username +'</div>'+
                                    '<time class="comment-date pull-right" datetime="'+data.date_created+'"><i class="fa fa-clock-o"></i>'+data.date_created+'</time>'+
                                  '</header>'+
                                  '<div class="comment-post">'+
                                  '<hr>'+
                                    '<p>'+ data.text +'</p>';
                                    if (data.image != "")
                                    {
                                      return_html += '<div class="">'+
                                            '<a href="'+data.image +'" class="thumbnail">'+
                                                '<img src="'+data.image+'" alt="'+ data.image +'" class="img-responsive img-rounded">'+
                                            '</a>'+
                                         '</div>';
                                    }
                                  return_html += '</div>'+
                                '</div>'+
                              '</div>'+
                            '</div>'+
                          '</article>';
    return return_html;
}