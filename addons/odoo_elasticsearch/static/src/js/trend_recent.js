/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('odoo_elasticsearch.custom',function(require){
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');

var _t = core._t;

// COPY TO CLIPBOARD
  $(document).ready(function() {

    $(window).load(function() {
        if ( $(".oe_search_box").length ) {
          var recent = [];
          if ((localStorage.getItem("RecentSearch")== null)){
              localStorage.setItem("RecentSearch", JSON.stringify(recent));
          }
        }
        localStorage.setItem("KeywordSearch", JSON.stringify(""));
    });

    var trending = $( "#trending_searches" ).val();
    var count_recent = $( "#count_recent" ).val();
    var $search_input = $( ".oe_search_box" );

    function onFocusTrendingSearch(obj) {
        if (JSON.parse(localStorage.KeywordSearch).length < 1){
            obj.autocomplete("search", "wkRecentSearch");
            if (!$('#recent_search').length && JSON.parse(localStorage.getItem('RecentSearch')).length > 0 ) {
                $('ul.ui-autocomplete').prepend("<li id='recent_search' style='padding-left: 12px;'><img src='/odoo_elasticsearch/static/src/image/Icon-Recent-Search.png' width='18' height='15'/><b style='color: #999999; padding-left: 10px;font-size: 12px;' >Recent Search </b><span id='clear_recent' class='clearAll' style='float: right;font-size: 12px;margin-right: 12px;color: #999999;cursor: pointer;' onclick='CheckSelected();'> clear X</span></li>");
             }
            if (!$('#trending_search').length) {
               try{
                    var recent = JSON.parse(localStorage.RecentSearch);
               }catch(err){
                  console.log(err);
               }
               if (JSON.parse(localStorage.getItem('RecentSearch')).length > 0 && JSON.parse(trending).length > 0 ){
                 $('ul.ui-autocomplete li:eq('+recent.length+')').after("<li id='trending_search' class='trending_search' style='padding-left: 12px;'><img src='/odoo_elasticsearch/static/src/image/Icon-Trending-Search.png' width='18' height='15'/><b style='color: #999999;padding-left: 10px;font-size: 12px;' >Trending Search </b></li>");
               }
               else{
                    if (JSON.parse(trending).length > 0 )
                      $('ul.ui-autocomplete').prepend("<li id='trending_search' class='trending_search' style='padding-left: 12px;'><img src='/odoo_elasticsearch/static/src/image/Icon-Trending-Search.png' width='18' height='15'/><b style='color: #999999;padding-left: 10px;font-size: 12px;' >Trending Search </b></li>");
               }
            }
            $('.dropdown1').hide();
            $('.dropdown2').hide();
        }
    }


    $search_input.focus(function() {
        onFocusTrendingSearch($(this));
    });


    $(".o_website_sale_search").submit(function(){
      var val = $('.oe_search_box').val().trim();
      var localRecent = JSON.parse(localStorage.getItem('RecentSearch'));
      if (!localRecent.includes(val) && (val != '') && (localRecent.length < 10) ){
        localRecent.push(val);
        localStorage.setItem("RecentSearch", JSON.stringify(localRecent));
      }
    });

    $search_input.keyup(function() {
        localStorage.setItem("KeywordSearch", JSON.stringify($(this).val()));
        onFocusTrendingSearch($(this));

    });


  });
});
