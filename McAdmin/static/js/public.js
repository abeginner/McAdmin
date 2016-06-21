function paginatorPostCommit(page) {
	var request = document.hostform;
	var opt = document.createElement("textarea");        
    opt.name = "page";        
    opt.value = page;               
    request.appendChild(opt);
    request.submit();        
    return request;
}


