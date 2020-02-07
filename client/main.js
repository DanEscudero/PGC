console.log('hey client');

function onButtonPress() {
	const Http = new XMLHttpRequest();
	Http.open('GET', 'http://127.0.0.1:3000/test/');
	Http.send();

	Http.onreadystatechange = (e) => {
		console.log(Http.response);
	};
}
