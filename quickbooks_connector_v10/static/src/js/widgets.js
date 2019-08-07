openerp.warehouse_website_super_jemmy_cust = function (instance){
    
    
    var module = instance.warehouse_website_super_jemmy_cust;
    var _t     = instance.web._t;
    var QWeb   = instance.web.qweb;
    
    module.AddShipmentEditor = instance.web.Widget.extend({
        template: 'AddShipmentEditor',
        init: function() {
            alert('hello')
            this._super.apply(this, arguments);
        },
       
        return_product_info: function(product){ //get product info based on product
            var self = this;
            alert(product);
//            return list
//            return new instance.web.Model('product.product').call('search', [[['name', '=', product.name]]])
//                .then(function(op_ids) {
//                            return self.getParent().refresh_ui(op_ids);
//                        });
            
        },
        
        
        renderElement: function(){
            var self = this;
            this._super();
            
            this.$('#product_list').change(function(){
                var selection = self.$('#product_list input').text();
                self.getParent().return_product_info(selection);
            });
        },
        
        
    });
}