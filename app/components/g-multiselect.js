import Ember from "ember";


export default Ember.Component.extend({
  _initializeMulti: (function() {
    return $(".multi").multiSelect({
      afterInit: (function(_this) {
        return function(controller) {
          if (_this.selected) {
            var selectedItems = [];
            _this.selected.forEach(function(i){
              if (i.selectId) selectedItems.pushObject(i.selectId)
              else if (i.id) selectedItems.pushObject(i.id)
              else selectedItems.pushObject(i);
            });
          };
          $('.multi').multiSelect('select', selectedItems);
        }
      })(this),

      afterSelect: (function(_this) {
        return function(values) {
          return _this.sendAction("addAction", values);
        };
      })(this),

      afterDeselect: (function(_this) {
        return function(values) {
          return _this.sendAction("removeAction", values);
        };
      })(this)

    });
  }).on("didInsertElement")
});
