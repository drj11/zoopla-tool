zoopla-tool
===========

Zoopla Tool on ScraperWiki

To update this tool on ScraperWiki (so that ScraperWiki has the
latest stuff from github.com) do this:

    $.ajax({url:"/api/tools",type:"POST",data:{name:"zoopla-search"}}).complete(function(r){console.log(r.responseText)})
