<script lang="ts">
	// let { data } = $props();
	let input = $state('');

	let client_id = Date.now();
	let ws = new WebSocket(`ws://0.0.0.0/api/ws/${client_id}`);
	let messages: string[] = $state([]);

	ws.onmessage = function (event) {
		messages.push(event.data);
	};

	function sendMessage(event: SubmitEvent) {
		ws.send(input);
		input = '';
		event.preventDefault();
	}
</script>

<ul></ul>

<h1>WebSocket Chat</h1>
<h2>Your ID: <span>{client_id}</span></h2>
<form action="" onsubmit={(e) => sendMessage(e)}>
	<input type="text" id="messageText" autocomplete="off" bind:value={input} />
	<button>Send</button>
</form>

<ul>
	{#each messages as message}
		<li>{message}</li>
	{/each}
</ul>
