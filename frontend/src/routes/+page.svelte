<script lang="ts">
	// let { data } = $props();
	let input = $state('')

	let client_id = Date.now()
	let chat = new WebSocket(`ws://0.0.0.0/api/ws/chat/${client_id}`)
	let messages: string[] = $state([])

	chat.onmessage = function (event) {
		messages.push(event.data)
	}

	function sendMessage(event: SubmitEvent) {
		chat.send(input)
		console.log(input)
		input = ''
		event.preventDefault()
	}

	let prices: [] = $state([])

	let quantity: number = $state(1)
	let currentPrice: number = $state(0)
	let error: string = $state('')

	let orderBook = new WebSocket(`ws://0.0.0.0/api/ws/orders`)

	orderBook.onmessage = function (event) {
		const eventData = JSON.parse(event.data)
		currentPrice = eventData.price
		prices = eventData.prices
		error = eventData.error
	}

	function sendOrder(price: number, quantity: number) {
		const obj = { price, quantity }
		orderBook.send(JSON.stringify(obj))
	}
</script>

<h1>Interex Futures</h1>

<h2 class="mb-3">Depth Of Market</h2>
<div class="grid grid-cols-2 gap-14 mb-10">
	<div>
		<div class="grid grid-cols-5 gap-4 justify-center items-center my-1">
			<div></div>
			<span class="col-span-2 text-center">Bids</span>
			<span class="col-span-2 text-center">Offers</span>
			{#each prices as { price, bids, offers }}
				<span class="text-base" class:text-white={price == currentPrice}>${price}</span>
				<button
					class="col-span-2 btn btn-success text-lg"
					onclick={() => sendOrder(price, quantity)}
					disabled={price > currentPrice}
				>
					{bids || '-'}
				</button>
				<button
					class="col-span-2 btn btn-error text-lg"
					onclick={() => sendOrder(price, -quantity)}
					disabled={price < currentPrice}
				>
					{offers || '-'}
				</button>
			{/each}
		</div>
	</div>

	<div class="grid grid-cols-4 grid-rows-3 gap-4 h-100 self-start items-center">
		<span>Quantity:</span>
		<span class="text-lg text-white">{quantity}</span>
		<button class="btn btn-neutral" onclick={() => quantity++}>
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
				<path fill="currentColor" d="m7 15l5-5l5 5z" />
			</svg>
		</button>
		<button class="btn btn-neutral" onclick={() => quantity--} disabled={quantity <= 1}>
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
				<path fill="currentColor" d="m7 10l5 5l5-5z" />
			</svg>
		</button>
		<button class="col-span-2 btn btn-success w-full text-base">Buy Market</button>
		<button class="col-span-2 btn btn-error w-full text-base">Sell Market</button>
		<span class="col-span-4 text-error text-lg">{error}</span>
	</div>
</div>

<h2>Market Chat</h2>
<h3>Your User ID: {client_id}</h3>
<form action="" onsubmit={(e) => sendMessage(e)}>
	<input
		type="text"
		class="input input-bordered w-full max-w-xs"
		autocomplete="off"
		bind:value={input}
	/>
	<button class="btn btn-primary">Send</button>
</form>

<ul>
	{#each messages as message}
		<li>{message}</li>
	{/each}
</ul>
