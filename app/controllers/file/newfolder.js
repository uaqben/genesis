import Ember from "ember";
import ENV from "../../config/environment";
import toB64 from "../../utils/to-b64";


export default Ember.ObjectController.extend({
  needs: ["files"],
  newFile: "",
  actions: {
    save: function(){
      var self = this,
          fn = this.get("newFile"),
          cp = this.get("controllers.files.currentPath") || "/";
      $.ajax({
        url: ENV.APP.krakenHost+'/api/files/'+toB64(cp),
        type: "POST",
        data: JSON.stringify({file: {name: fn, folder: true}}),
        contentType: 'application/json',
        processData: false,
        success: function(j) {
          self.get("controllers.files.currentFolder").pushObject(j.file);
        },
        error: function(e) {
          if (e.status == 500) self.transitionToRoute("error", e);
        }
      });
    },
    removeModal: function(){
      this.set("newFile", "");
      return true;
    }
  }
});
