/* global require, module */

var EmberApp = require('ember-cli/lib/broccoli/ember-app');
var pickFiles = require('broccoli-static-compiler');

var app = new EmberApp();

// Use `app.import` to add additional libraries to the generated
// output files.
//
// If you need to use different assets in different
// environments, specify an object as the first parameter. That
// object's keys should be the environment name and the values
// should be the asset to use in that environment.
//
// If the library that you are including contains AMD or ES6
// modules that you would like to import into your application
// please specify an object with the list of modules as keys
// along with the exports of each module as its value.

app.import('bower_components/bootstrap/dist/js/bootstrap.js');
app.import('bower_components/bootstrap/dist/css/bootstrap.css');
app.import('bower_components/bootstrap/dist/css/bootstrap.css.map', {
  destDir: 'assets'
})
app.import('bower_components/bootstrap-contextmenu/bootstrap-contextmenu.js');
app.import('bower_components/moment/moment.js');
app.import('bower_components/lightbox2/src/js/lightbox.js');
app.import('bower_components/lightbox2/src/css/lightbox.css');
app.import('bower_components/multiselect/js/jquery.multi-select.js');
app.import('bower_components/multiselect/css/multi-select.css');
app.import("bower_components/codemirror/lib/codemirror.css");
app.import("bower_components/codemirror/lib/codemirror.js");
app.import("bower_components/codemirror/mode/css/css.js");
app.import("bower_components/codemirror/mode/htmlmixed/htmlmixed.js");
app.import("bower_components/codemirror/mode/javascript/javascript.js");
app.import("bower_components/codemirror/mode/markdown/markdown.js");
app.import("bower_components/codemirror/mode/php/php.js");
app.import("bower_components/codemirror/mode/python/python.js");
app.import("bower_components/codemirror/mode/ruby/ruby.js");
app.import("bower_components/codemirror/mode/shell/shell.js");
app.import("bower_components/codemirror/mode/xml/xml.js");
app.import("bower_components/font-awesome/css/font-awesome.css");
app.import("bower_components/fira/fira.css");
var fontAwesome = pickFiles('bower_components/font-awesome/fonts', {
    srcDir: '/',
    destDir: 'fonts'
});
var firaEot = pickFiles('bower_components/fira/eot', {
    srcDir: '/',
    destDir: 'assets/eot'
});
var firaOtf = pickFiles('bower_components/fira/otf', {
    srcDir: '/',
    destDir: 'assets/otf'
});
var firaTtf = pickFiles('bower_components/fira/ttf', {
    srcDir: '/',
    destDir: 'assets/ttf'
});
var firaWoff = pickFiles('bower_components/fira/woff', {
    srcDir: '/',
    destDir: 'assets/woff'
});
app.import("bower_components/lightbox2/src/images/close.png", {destDir: '/img'});
app.import("bower_components/lightbox2/src/images/next.png", {destDir: '/img'});
app.import("bower_components/lightbox2/src/images/prev.png", {destDir: '/img'});
app.import("bower_components/lightbox2/src/images/loading.gif", {destDir: '/img'});
app.import("bower_components/multiselect/img/switch.png", {destDir: '/img'});

module.exports = app.toTree([fontAwesome, firaEot, firaOtf, firaTtf, firaWoff]);
