odoo.daily_record = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    instance.web.daily_record = instance.web.daily_record || {};

    instance.web.views.add('tree_daily_record_move_line_quickadd', 'instance.web.daily_record.QuickAddListView');
    instance.web.daily_record.QuickAddListView = instance.web.ListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.rel = [];
            this.current_val = null;
        },
        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            //this.$el.parent().prepend(QWeb.render("DailyMoveLineQuickAdd", {widget: this}));
            this.$el.parent().prepend("<div class='any_ui_quickadd ui-toolbar' />");
            this.$el.parent().find('.any_ui_quickadd').append('<select class=oe_daily_select_creator />');
            this.$el.parent().find('.oe_daily_select_creator').change(function() {
                self.current_val = this.value === '' ? null : parseInt(this.value);
                self.do_search(self.last_domain, self.last_context, self.last_group_by);
            });
            return tmp;
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var mod = new instance.web.Model("daily.record", context, domain);
            return $.when(mod.call("list_creator", []).then(function(result) {
                self.rel = result;
            })).then(function () {
                var o;
                self.$el.parent().find('.oe_daily_select_creator').children().remove().end();
                self.$el.parent().find('.oe_daily_select_creator').append(new Option('创建人', ''));
                for (var i = 0;i < self.rel.length;i++){
                    o = new Option(self.rel[i][1], self.rel[i][0]);
                    self.$el.parent().find('.oe_daily_select_creator').append(o);
                }    
                self.$el.parent().find('.oe_daily_select_creator').val(self.current_val).attr('selected',true);
                return self.search_by();
            });
        },
        search_by: function() {
            var self = this;
            var domain = [];
            if (self.current_val !== null) domain.push(["create_uid", "=", self.current_val]);
            if (self.current_val === null) delete self.last_context["create_uid"];
            else self.last_context["create_uid"] =  self.current_val;
            return self.old_search(new instance.web.CompoundDomain(self.last_domain, domain), self.last_context, self.last_group_by);
        },
    });
};
