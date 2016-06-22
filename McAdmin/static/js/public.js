function paginatorPostCommit(page) {
	var request = document.postform;
	var opt = document.createElement("textarea");        
    opt.name = "page";        
    opt.value = page;               
    request.appendChild(opt);
    request.submit();        
    return request;
}


function loadPage(url)  
{  
        sendRequest(url);  
}  
var request=false;   
    try   
    {   
        request = new XMLHttpRequest();   
    }   
    catch (trymicrosoft)   
    { try   
        { request = new ActiveXObject("Msxml2.XMLHTTP");   
        } catch (othermicrosoft)   
        { try { request = new ActiveXObject("Microsoft.XMLHTTP");   
        } catch (failed) {   
                request = false;   
            }   
        }   
  }   
function sendRequest(url) {  
    //alert(request);  
    request.open("GET", url, true);  
    alert(url);  
    request.onreadystatechange = processResponse;  
    request.send(null);    
}  
  
function processResponse() {  
    if (request.readyState == 4) {   
        if (request.status == 200) {   
        var response = request.responseText;   
         document.getElementById("content").innerHTML = response;       
        } else if (request.status == 404) {   
        alert("Requested URL is not found.");   
        } else if (request.status == 403) {   
        alert("Access denied.");   
        } else   
        alert("status is " + request.status);   
        }   
} 
