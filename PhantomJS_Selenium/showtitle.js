'use strict';
var page = require('webpage').create();
var url = 'http://www.baidu.com';
page.onConsoleMessage = function(msg) {
    console.log('Page title is ' + msg);
  };
page.onResourceRequested = function(request) {
    console.log('Request ' + JSON.stringify(request, undefined, 4));
};
page.onResourceReceived = function(response) {
    console.log('Receive ' + JSON.stringify(response, undefined, 4));
};
page.open(url,function(status){
    var title = page.evaluate(function(){
        console.log(document.title);
        return document.title;
    });
    //console.log('Page title is ' + title);
    phantom.exit();
});