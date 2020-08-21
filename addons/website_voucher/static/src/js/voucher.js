/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
    /* See LICENSE file for full copyright and licensing details. */
odoo.define('website_voucher.website_voucher', function (require) {
"use strict";
    var ajax = require('web.ajax');
    $(".copy_code").on('click',function (e) {
            var $temp = $("<input>");
            $("body").append($temp);
            $temp.val($(this).prev().text()).select();
            document.execCommand("copy");
            $temp.remove();
            $('.copy_code').text("Copy Code");
            $(this).text("Code Copied");
    });
    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;
        $(".wk_voucher").on('click',function (ev){
            ApplyVoucher();
            
            });
        $("#voucher_8d_code").keyup(function (e) {
                if (e.keyCode == 13) {
                    ApplyVoucher();
                   }
        });
        function ApplyVoucher() {
            var secret_code = $("#voucher_8d_code").val();
            ajax.jsonRpc("/website/voucher/", 'call', {'secret_code': secret_code}).then(function (result)
            {
                if(result['status'])
                {
                    $(".success_msg").css('display','block')
                    $(".success_msg").html(result['message']); 
                    $(".success_msg").fadeOut(3000);
                    $(location).attr('href',"/shop/cart");
                }
                else
                {
                    $(".error_msg").css('display','block')
                    $(".error_msg").html(result['message']); 
                    $(".error_msg").fadeOut(5000);
                }
                    
            }).fail(function (err) {
                $(".error_msg").css('display','block')
                $(".error_msg").html('Unknown Error ! Please try again later.'); 
                $(".error_msg").fadeOut(5000);       
                });
            }


    $(oe_website_sale).on("change", ".oe_cart input.js_quantity[data-product-id]", function () {
        setTimeout(function(){
            ajax.jsonRpc("/voucher/validate/cart_change", 'call', {})
                .then(function (data) {
                if (data)
                {
                    location.reload();
                }
                });
            }, 500);
        });
});
});