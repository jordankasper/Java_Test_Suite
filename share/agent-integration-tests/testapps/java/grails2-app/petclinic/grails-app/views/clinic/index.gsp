<html>
	<head>
		<meta name="layout" content="main">
		<title>Welcome</title>
	</head>
	<body id="welcome">
		<img src="${resource(dir:'images', file:'pets.png')}" align="right" style="position:relative;right:30px;">
		<h2><g:message code="welcome"/></h2>

		<ul>
			<li><g:link controller="owner" action="find">Find owner</g:link></li>
			<li><g:link action="vets">Display all veterinarians</g:link></li>
			<li><a href="${resource(dir:'html', file:'petclinic.html')}">Tutorial</a></li>
		</ul>
	</body>
</html>
