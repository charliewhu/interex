<script lang="ts">
	import { PUBLIC_BASE_URL } from '$env/static/public'
	import { Button } from '$lib/components/ui/button'
	import { Input } from '$lib/components/ui/input'
	// let { data } = $props();
	const baseUrl = PUBLIC_BASE_URL

	let input = $state('')

	let client_id = Date.now()
	let chat = new WebSocket(`${baseUrl}/ws/chat/${client_id}`)
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

	let orderBook = new WebSocket(`${baseUrl}/ws/orders`)

	orderBook.onmessage = function (event) {
		const eventData = JSON.parse(event.data)
		currentPrice = eventData.price
		prices = eventData.prices
		error = eventData.error
	}

	function sendOrder(price: number | null, quantity: number) {
		const obj = { price: price, quantity: quantity }
		orderBook.send(JSON.stringify(obj))
	}
</script>

<h1 class="text-4xl font-extrabold tracking-tight mb-10">Interex Futures</h1>

<div class="grid grid-cols-1 sm:grid-cols-2 gap-14 mb-10">
	<div>
		<h2 class="text-xl font-extrabold tracking-tight mb-3">Depth Of Market</h2>
		<div>
			<div class="grid grid-cols-5 gap-4 justify-center items-center my-1">
				<div></div>
				<span class="col-span-2 text-center">Bids</span>
				<span class="col-span-2 text-center">Offers</span>
				{#each prices as { price, bids, offers }}
					<span class="" class:font-extrabold={price == currentPrice}>${price}</span>
					<Button
						class="col-span-2 text-lg bg-green-500 hover:bg-green-600"
						onclick={() => sendOrder(price, quantity)}
						disabled={price > currentPrice}
					>
						{bids || '-'}
					</Button>
					<Button
						class="col-span-2 text-lg bg-red-500 hover:bg-red-600"
						onclick={() => sendOrder(price, -quantity)}
						disabled={price < currentPrice}
					>
						{offers || '-'}
					</Button>
				{/each}
			</div>
		</div>
	</div>

	<div>
		<h2 class="text-xl font-extrabold tracking-tight mb-3">Adjust Order</h2>
		<div class="grid grid-cols-4 grid-rows-3 gap-4 h-100 self-start items-center">
			<span class="col-span-2">Quantity: <span class="text-lg">{quantity}</span></span>
			<Button class="" onclick={() => quantity++}>
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
					<path fill="currentColor" d="m7 15l5-5l5 5z" />
				</svg>
			</Button>
			<Button class="" onclick={() => quantity--} disabled={quantity <= 1}>
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
					<path fill="currentColor" d="m7 10l5 5l5-5z" />
				</svg>
			</Button>
			<Button
				class="col-span-2 w-full bg-green-500 hover:bg-green-600"
				onclick={() => sendOrder(null, quantity)}>Buy Market</Button
			>
			<Button
				class="col-span-2 w-full bg-red-500 hover:bg-red-600"
				onclick={() => sendOrder(null, -quantity)}
			>
				Sell Market
			</Button>
			<span class="col-span-4 text-red-600 text-lg">{error}</span>
		</div>
	</div>
</div>

<h2 class="text-xl font-extrabold tracking-tight mb-2">Market Chat</h2>
<h3 class="text-md tracking-tight mb-3">Your User ID: {client_id}</h3>
<form
	class="flex flex-col justify-center items-start gap-4 mb-6"
	action=""
	onsubmit={(e) => sendMessage(e)}
>
	<Input type="text" class="w-full max-w-xs" autocomplete="off" bind:value={input} />
	<Button type="submit">Send</Button>
</form>

<ul>
	{#each messages as message}
		<li>{message}</li>
	{/each}
</ul>
