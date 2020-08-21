odoo.define('email_verification.email_verification', function(require) {
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    $(document).ready(function() {
        let href = location.href;
        if ( href.includes('is_verified') ) {
            location.href = href.split('is_verified=True')[0];
            alert(_t('You are already verified'));
        }
        
        var oe_website_sale = this;
        $('.oe_website_sale').on('click', '#restrict_checkout,a[href^="/shop/checkout"]', function(event) {
            if (('disabled' in this.attributes) && this.attributes.disabled.value == 'True') {
                event.preventDefault();
                $(this).popover({
                    content: "<center><font color='blue'>You have not verified your email yet, please verify your email for proceeding further.</font></center",
                    title: "<center><font color='red'>WARNING!!</font></font></center>",
                    placement: "top",
                    html: true,
                    trigger: 'focus',
                });
                $(this).popover('show');
            }
        });
    });
});
