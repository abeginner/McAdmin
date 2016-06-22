function paginatorPostCommit(page) {
	var request = document.postform;
	var opt = document.createElement("textarea");        
    opt.name = "page";        
    opt.value = page;               
    request.appendChild(opt);
    request.submit();        
    return request;
}

//postCommit('pages/statisticsJsp/excel.action', {html :prnhtml,cm1:'sdsddsd',cm2:'haha'});
function postCommit(url, params) {        
    var temp = document.createElement("form");        
    temp.action = url;        
    temp.method = "post";        
    temp.style.display = "none";        
    for (var x in params) {        
        var opt = document.createElement("textarea");        
        opt.name = x;        
        opt.value = params[x];               
        temp.appendChild(opt);        
    }        
    document.body.appendChild(temp);        
    temp.submit();        
    return temp;        
} 