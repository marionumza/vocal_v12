odoo.define('web_text_count_widget.counter_widget', function (require) {
"use strict";

var basicFields = require('web.basic_fields');
var core = require('web.core');
var fieldRegistry = require('web.field_registry');
var dom = require('web.dom');
var framework = require('web.framework');


var FieldText = basicFields.FieldText;
var InputField = basicFields.InputField;
var QWeb = core.qweb;

var _t = core._t
var TextCounterWidget = InputField.extend({
    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
        this.nbrChar = 0;
        this.maxChar = this.nodeOptions.max || 500;
        this.remChar = this.nodeOptions.max || 500;
        this.tagName = 'div';
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Compute the number of characters
     * @private
     */
    _compute: function () {
        var content = this._getValue();
        this.nbrChar = content.length;
        this.nbrChar += (content.match(/\n/g) || []).length;
        this.remChar = this.maxChar - this.nbrChar
        this._renderTemp();
    },
    /**
     * @private
     * @override
     */
    _renderEdit: function () {
        this.$el.empty();
        this._prepareInput($('<textarea/>')).appendTo(this.$el);
        this.$el.append($(QWeb.render("web_text_counter_widget.text_count", {})));
        this._compute();
    },
    /**
     * Render the number of characters
     * @private
     */
    _renderTemp: function () {
        this.$('.o_text_count').text(_.str.sprintf(_t('%s chars in, %s chars remaining / %s'), this.nbrChar, this.remChar, this.maxChar));
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------   

    /**
     * @override
     * @private
     */
    _onChange: function () {
        this._super.apply(this, arguments);
        this._compute();
    },
    /**
     * @override
     * @private
     */
    _onInput: function () {
        this._super.apply(this, arguments);
        this._compute();
    },
});

fieldRegistry.add('counter_widget', TextCounterWidget);

return TextCounterWidget;
});
