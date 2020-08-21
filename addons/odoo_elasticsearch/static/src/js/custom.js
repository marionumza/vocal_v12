/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('odoo_elasticsearch.custom',function(require){
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');

var _t = core._t;

// COPY TO CLIPBOARD

  $(document).ready(function() {

    var image_url = "<img src='%base_url/web/image/%model_name/%id/image/45x45' width='45' height='45'>";
    var $search_input = $( ".oe_search_box" );
    var start_limit = $("#search_start_limit").val();
    var text_color = $("#text_color").val();
    var hover_text_color = $("#hover_text_color").val();
    var hover_background_color = $("#hover_background_color").val();
    var base_url = $("#base_url").val();
    var is_prdct_thumb = $("#is_prdct_thumb").val();
    var is_prdct_desc = $("#is_prdct_desc").val();
    var max_prdct_desc = $("#max_prdct_desc").val();
    var index_name = $("#index_name").val();
    var doc_type = $("#doc_type").val();
    var desc_color = $("#desc_color").val();
    var resize_menu = $("#resize_menu").val();
    var max_prdct_sugg = $("#max_prdct_sugg").val();
    var connectionInfo = $("#connectionInfo").val();
    var style_desc_color = "style='color:%s!important;'";
    var elasticServer = connectionInfo+"/"+index_name+"/"+doc_type;
    style_desc_color = style_desc_color.replace("%s",desc_color);

    image_url = image_url.replace("%base_url",base_url);
    image_url = image_url.replace("%model_name",doc_type);
    $('<style>.ui-state-focus-override { background : '+hover_background_color+';  color:'+ hover_text_color+'!important; }</style>').appendTo('body');

    var search_term = "";
    $search_input.keyup(function() {
        search_term = $(this).val();
    });


    var trendSearch = $("#trending_searches").val();
    function getData(array) {
        var src = [];
        var i;
        for (i = 0; i < array.length; i++) {
            src.push({
                        value:array[i]._source.name,
                        label:array[i]._source.name,
                        desc:array[i]._source.description,
                        desc_sale:array[i]._source.description_sale,
                        id:array[i]._id
                        });

        }
        return src;
    }



    function _computeDescp(str) {
        var desc = " ";
        if (typeof(str) == "string"){
            if (str.length > max_prdct_desc){
                desc = str.substring(0,max_prdct_desc)+" ...";
            }
            else{
                desc = str;
            }
        }
        else{
        desc = desc;
        }
        return desc;
    }

    function _getSearchQuery(search_term) {
      return {
               "size" : max_prdct_sugg,
               "query": {
                   "bool": {
                       "filter": [
                           {
                                   "term": {
                                           "website_published": "true"
                                   }
                           },
                           {
                                   "term": {
                                           "sale_ok": "true"
                                   }
                           },
                           {
                                   "term": {
                                           "active": "true"
                                   }
                           },
                       ],
                       "must": {
                               "simple_query_string" : {
                                    "query": search_term+"*",
                                   "fields": ["name"],
                                   "default_operator": "and"
                               }
                       }
                   }
             }
           }
    }

    function _getBoldName(search_term,ItemName) {
        var str = ItemName;
        if (typeof str == "string"){
            var reg = new RegExp(search_term, 'gi');
            var res = str.match(reg);
            var i;
            if( Array.isArray(res)){
                for (i=0;i<res.length;i++)
                {
                    str = str.replace(res[i],"<b>"+res[i]+"</b>");
                }
             }
             else{
                str = str;
             }
         }
         else{
            str = "";
         }
        return str;
    }
    var is_recentSearch = false;
    $search_input.autocomplete({
        search: function(event, ui) {
                     $(".dropdown1").show();

               },
        response: function(event, ui) {
                        if (ui.content.length === 0) {
                            $("#no-result-found").text('Sorry, nothing found for "'+search_term.substring(0,10)+'"');
                            $(".dropdown2").show();
                        } else {
                              $(".dropdown2").hide();
                              $(".dropdown1").hide();
                        }
              },
        source : function( request, response ) {
                    var srch = request.term.toLowerCase().trim();
                    if (request.term == 'wkRecentSearch'){
                       is_recentSearch = true;
                       var recent = [" "]
                       try {
                           recent  = JSON.parse(localStorage.RecentSearch);
                        }
                        catch(err) {
                          // console.log(err);
                        }
                       var trend = JSON.parse(trendSearch);
                       response(recent.concat(trend));

                    }
                    else{
                       is_recentSearch = false;
                       var SearchQuery1 = _getSearchQuery(srch);
                      $.ajax({
                          url: elasticServer+"/_search",
                          method: "POST",
                          dataType: "json",
                          data: JSON.stringify(SearchQuery1),
                          crossDomain : true,
                          contentType: "application/json",
                      	}).done(function (result) {
                                  var res = getData(result.hits.hits);
                                  response(res);

      					      });
                    }
        },
        open: function(e,ui) {

            var acData = $(this).data("ui-autocomplete");
                acData.menu.element.find('li').each(function() {
                        var me = $(this);
                        me.css("color", text_color);
                    });
//
//            if (!$('#ac-add-venue').length && $('.elastic-serach-dropdown-result').length ) {
//                $('ul.ui-autocomplete').prepend("<li id='product-header'>Product header </li>");
//
//             }
        },

        minLength: start_limit,

        select: function(event, ui) {
                        $(".oe_search_box").val(ui.item.value);
                        $(".o_website_sale_search").submit();
        },


        focus: function (event, ui) {
            var menu = $(this).data("ui-autocomplete").menu.element,
            focused = menu.find('.ui-state-focus');
            menu.children().removeClass("ui-state-focus-override");
            focused.removeClass( "ui-state-focus" ).addClass( "ui-state-focus-override" );
        }
    })
    $search_input.autocomplete( "instance" )._renderItem = function( ul, item ) {
      if (is_recentSearch){
        var html_content = "<div class='right'>"+item.label+"</div>";
        return $( "<li>" )
          .append(html_content)
          .appendTo( ul );

      }else{
         var match_bold_char = _getBoldName(search_term,item.label);
         var itemName = match_bold_char;
         var image_tag = image_url.replace("%id",item.id);
         var html_content = "<span class='right elastic-serach-dropdown-result'>"+itemName;
         if  (is_prdct_desc){
             html_content = html_content + "<br><span class='prdct_descp'"+style_desc_color+">"+_computeDescp(item.desc_sale)+"</span></span>";
         }else{
              html_content = html_content + "</span>";
         }
         if (is_prdct_thumb){
                  html_content = "<span class='left' >"+image_tag+"</span>" + html_content;
         }
         html_content = "<a href='"+base_url+"/shop/product/"+item.id+"' style='display: inline-block;'>"+html_content+"</a>"
        return $( "<li>" )
          .append(html_content)
          .appendTo( ul );
      }
    };



    $search_input.autocomplete( "instance" )._resizeMenu =  function() {
      this.menu.element.outerWidth( resize_menu );
    }

    $search_input.focusout(function () {
        $(".dropdown2").hide();
        $(".dropdown1").hide();
    });

  });
});
