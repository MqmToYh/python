"use strict";
var page = require('webpage').create();
page.open('https://www.baidu.com/',function(status){
    console.log('status:'+status);
    if (status == 'success'){
        page.render('baidu.png')
    }
    phantom.exit();
});